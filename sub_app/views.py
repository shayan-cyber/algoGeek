import datetime
from django.http.response import Http404
from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponseForbidden,HttpResponse
import requests
import json
from . models import Contest, Profile, Question,DsAlgoTopics, ScoreCard, Bookmark, SolvedOrNot,Testcase
import uuid
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from datetime import date,datetime
import pytz
from django.core.mail import EmailMessage, message
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
# from dateutil.tz import gettz
IST = pytz.timezone('Asia/Kolkata')

# import datetime

# print(uuid.uuid4())
RUN_URL = "https://api.hackerearth.com/v3/code/run/"


def home(request):
   
    return render(request,"home.html")

@login_required(login_url='/')
def run_code(request):
    if request.is_ajax():
        code_ = request.POST['code_']
        lang = request.POST['lang']
        print(lang)
        data = {
            'client_secret': '01f0859bab2c86c1e6a1c1fb549f27a805baad59' ,
            'async':0,
            'source':code_,
            'lang':lang,
            'time_limit':10,
            'memory_limit': 262144,

        }
        

        if 'Input' in request.POST:
            print(request.POST.get('Input',''))
            data["input"] = request.POST.get('Input','')


        resp = requests.post(RUN_URL, data=data)
        print(resp)
        return JsonResponse(resp.json(),safe=False)
    else:
        return HttpResponseForbidden


@login_required(login_url='/')
def submit_code(request,pk):
    question =Question.objects.filter(pk=pk)[0]
    UTC = pytz.utc
    
    timeZ_Kl = pytz.timezone('Asia/Kolkata') 

    
    dt_Kl = datetime.now(timeZ_Kl)

    
    utc_Kl = dt_Kl.astimezone(UTC)
    now2 = dt_Kl.strftime('%Y-%m-%d %H:%M:%S')
    now = datetime.strptime(now2, '%Y-%m-%d %H:%M:%S')
    if request.is_ajax():
        code_ = request.POST['code_']
        lang = request.POST['lang']
        # print(lang)
        data = {
            'client_secret': '01f0859bab2c86c1e6a1c1fb549f27a805baad59' ,
            'async':0,
            'source':code_,
            'lang':lang,
            'time_limit':question.time_limit,
            'memory_limit': 262144,

        }
        testCases = Testcase.objects.filter(quest = question)
        print("tescases")
        print(testCases)
        count = 0

        for testCase in testCases:
           
            if len(testCase.input_cases)> 0:
                data["input"] = testCase.input_cases
                print("input giiven")
                
            resp = requests.post(RUN_URL, data=data)
            resp_json = resp.json()
            
            if resp_json['run_status']['status']=='AC':
                output_ = resp_json['run_status']['output'] 
                output_ =str(output_)
                
                time_limit_reached = resp_json['run_status']['time_used']
                
                string =testCase.test_cases
        
                string_ = str(string.replace(" ", "").replace("\n",""))
                output_ =output_.replace(" ", "").replace("\n","")
                
            
               
                print(''.join(string_.splitlines()))
                
                print(''.join(output_.splitlines()))


                in_put = ''.join(string_.splitlines())
                out_put =''.join(output_.splitlines())


                if in_put==out_put:

                    print("test cases passed")
                    count = count +1
                    print(count)

            elif resp_json['run_status']['status']=='TLE':
                msg = {
                            'message':"Time Limit Exceeded",
                        'output': resp_json['run_status']['output']
                        }
                return JsonResponse(msg,safe=False)

            else:
                print("Compilation Error")
                print(resp_json)
                msg ={
                        'message':"Compilation Error",
                    
                    }
                return JsonResponse(msg,safe=False)
                
                    
                    
        if count == len(testCases):
            print("all passed")

            
            #for dry run by curator

            if request.user == question.contest_of.curator.user:
                print('curator visited')
                
            else:
                

                #solved r not
                solved_check = SolvedOrNot.objects.filter(owner =Profile.objects.filter(user =request.user)[0])
                if solved_check :
                    solved_check[0].probs.add(question)
                else:
                    solved_or_not = SolvedOrNot(owner =Profile.objects.filter(user =request.user)[0])
                    solved_or_not.save()
                    solved_check = SolvedOrNot.objects.filter(owner =Profile.objects.filter(user =request.user)[0])[0]
                    solved_check.probs.add(question)
                



                # checking scorecard
                scorecard_check = ScoreCard.objects.filter(_contest = question.contest_of , prof = Profile.objects.filter(user =request.user)[0], _ques= question)
                scoredcard_check_2 =ScoreCard.objects.filter(_contest = question.contest_of , prof = Profile.objects.filter(user =request.user)[0])
                print(scoredcard_check_2)
                if scorecard_check:
                    print("already got marks")
                elif scoredcard_check_2:
                    scoredcard_check_2= scoredcard_check_2[0]
                    endtime = str(question.contest_of.end_time)
                    endtime = endtime[:19]
                    if datetime.strptime(endtime, '%Y-%m-%d %H:%M:%S')  > now:
                        scoredcard_check_2._ques.add(question)
                        scoredcard_check_2.score = scoredcard_check_2.score + question.score
                        scoredcard_check_2.time = now
                        scoredcard_check_2.save()
                        scorecards_for_total_points = ScoreCard.objects.filter(prof = Profile.objects.filter(user = request.user)[0])
                        #adding total points 
                        total = 0
                        for scr in scorecards_for_total_points:
                            total = total + int(scr.score)
                        prof_of_the_user = Profile.objects.filter(user =request.user)[0]
                        prof_of_the_user.total_points = total
                        prof_of_the_user.save()
                            


            msg ={
                'message':"Test Cases Passed",
                'output': resp_json['run_status']['output']
                }

        else:
            msg= {
                'message':"Test Cases Not Passed",
                'output':resp_json['run_status']['output']
            }


            

        return JsonResponse(msg,safe=False)


@login_required(login_url='/')
def problem_setting(request, pk):
    
    contest = Contest.objects.filter(pk =pk)[0]
    if request.user == contest.curator.user:
        dsalgos = DsAlgoTopics.objects.all()
        ques = Question.objects.filter(contest_of = contest)
        print(ques)

        print(contest)
        

        if request.method =='POST':
            # test_case = request.POST.get('test_cases','')
            # input_case = request.POST.get('input_cases','')
            score = request.POST.get('score','')
            description = request.POST.get('description','')
            time_limit = request.POST.get('time_limit','')
            difficulty = request.POST.get('difficulty', '')
            contest_id = request.POST.get('contest_id','')
            contest_uid = request.POST.get('contest_uid','')
            title = request.POST.get('title','')
            category = request.POST.get('category','')
            dsalgo = DsAlgoTopics.objects.filter(pk = category)[0]

            # print(test_case)
            contest =Contest.objects.filter(pk = contest_id, unique_id = contest_uid)[0]
            print(contest)
            question = Question(title=title, description=description, score=score,time_limit=time_limit, difficulty=difficulty, category=dsalgo,contest_of =contest)

            question.save()

        context = {
            "contest":contest,
            'dsalgos':dsalgos,
            'ques':ques,
        }
        return render(request,"problem_setting.html",context)
    else:
        raise Http404()



@login_required(login_url='/')
def add_test_cases_page(request, pk):
    question_ = Question.objects.filter(pk =pk)[0]
    if request.user == question_.contest_of.curator.user:
        test_cases = Testcase.objects.filter(quest =question_)
        context= {
            'test_cases':test_cases,
            'question':question_
        }
        return render(request, "add_test_case_page.html", context)
    elif request.user == question_.prof_w_c.user :
        test_cases = Testcase.objects.filter(quest =question_)
        context= {
            'test_cases':test_cases,
            'question':question_
        }
        return render(request, "add_test_case_page.html", context)

    else:
        raise Http404()
    



@login_required(login_url='/')
def add_test_cases(request, pk):
    if request.method =="POST":
        question_ = Question.objects.filter(pk = pk)[0]
        #adding test cases
        test_case  = request.POST.get("test_cases","")
        input_case = request.POST.get("input_cases", "")
        title = request.POST.get("title","")


        test_case = Testcase(quest = question_, test_cases= test_case, input_cases =input_case,title=title)
        test_case.save()
        contest_pk = question_.contest_of.pk
        return redirect("/add_test_cases_page/" + str(question_.pk))

        
    else:
        raise Http404()
@login_required(login_url='/')
def edit_test_case(request,pk):
    if request.method =="POST":
        test_cases = request.POST.get("test_cases_edit","")

        input_cases = request.POST.get("input_cases_edit","")

        test_case = Testcase.objects.filter(pk =pk)[0]
        test_case.test_cases = test_cases
        test_case.input_cases = input_cases
        test_case.save()
        question_ = test_case.quest.pk
        return redirect("/add_test_cases_page/"+str(question_))
        
    else:
        raise Http404()

@login_required(login_url='/')
def normal_problem_setting(request,pk):
    dsalgos = DsAlgoTopics.objects.all()
    # ques = Question.objects.filter(contest_of = contest).order_by('-curation_time')
    prof_ = Profile.objects.filter(pk = pk)[0]

    not_contest = Contest.objects.filter(unique_id = "not_a_contest",title="Not A contest")[0]
    

    if request.method =='POST':
        # test_case = request.POST.get('test_cases','')
        # input_case = request.POST.get('input_cases','')
        score = 0
        description = request.POST.get('description','')
        time_limit = request.POST.get('time_limit','')
        difficulty = request.POST.get('difficulty', '')
        # contest_id = request.POST.get('contest_id','')
        # contest_uid = request.POST.get('contest_uid','')
        title = request.POST.get('title','')
        category = request.POST.get('category','')
        dsalgo = DsAlgoTopics.objects.filter(pk = category)[0]

        
        contest =not_contest
        print(contest)
        question = Question(title=title, description=description, score=score,time_limit=time_limit,difficulty=difficulty,prof_w_c=prof_, category=dsalgo,contest_of =contest)

        question.save()
        return redirect("/profile/" + str(pk))

    # context = {
    #     "contest":contest,
    #     'dsalgos':dsalgos,
        
    # }

    else:
        raise Http404()
@login_required(login_url='/')  
def normal_problem_edit(request,pk):
    problem_ = Question.objects.filter(pk =pk)[0]
    if request.method == "POST":
        if problem_.prof_w_c == Profile.objects.filter(user = request.user)[0]:
            
            
            description = request.POST.get('description_edit','')
            score = 0
            time_limit = request.POST.get('time_limit_edit','')
            difficulty = request.POST.get('difficulty_edit', '')
            
            
            title = request.POST.get('title_edit','')
            category = request.POST.get('category_edit','')
            dsalgo = DsAlgoTopics.objects.filter(pk = category)[0]

           
            problem_.description =description
            problem_.score = score
            problem_.time_limit =time_limit
            problem_.dfficulty =difficulty
            problem_.title =title
            problem_.category =dsalgo
            problem_.save()
            
            return redirect("/profile/"+str(problem_.prof_w_c.pk))
        else:
            raise Http404()
    else:
        raise Http404()   



@login_required(login_url='/')
def contests(request):
    contests_ = Contest.objects.exclude(unique_id ="not_a_contest", title="Not A contest").order_by('-curation_time')



    for contest_ in contests_:
        if contest_.status =="AC":
            UTC = pytz.utc
    
            timeZ_Kl = pytz.timezone('Asia/Kolkata') 

            
            dt_Kl = datetime.now(timeZ_Kl)

            
            utc_Kl = dt_Kl.astimezone(UTC)
            now2 = dt_Kl.strftime('%Y-%m-%d %H:%M:%S')
            now = datetime.strptime(now2, '%Y-%m-%d %H:%M:%S')
            endtime = str(contest_.end_time)
            endtime = endtime[:19]
            if now > datetime.strptime(endtime, '%Y-%m-%d %H:%M:%S'):
                print("done")
                contest_.status = "IA"
                contest_.save()
                print(contest_.status)
    active_contests = Contest.objects.filter(status = "AC").difference(Contest.objects.filter(unique_id ="not_a_contest", title="Not A contest")).order_by('-curation_time')
    previous_contests = Contest.objects.filter(status ="IA").difference(Contest.objects.filter(unique_id ="not_a_contest", title="Not A contest")).order_by('-curation_time')
    context ={
        'active_contests':active_contests,
        'previous_contests': previous_contests,
    }
    return render(request,"contests.html",context)

@login_required(login_url='/')
def problem(request, pk):
    UTC = pytz.utc
    
    timeZ_Kl = pytz.timezone('Asia/Kolkata') 

    
    dt_Kl = datetime.now(timeZ_Kl)

    
    utc_Kl = dt_Kl.astimezone(UTC)
    now2 = dt_Kl.strftime('%Y-%m-%d %H:%M:%S')
    now = datetime.strptime(now2, '%Y-%m-%d %H:%M:%S')
    question = Question.objects.filter(pk =pk)[0]


    #test for curator 
    if request.user == question.contest_of.curator.user:
        end_time= str(question.contest_of.end_time)
        context = {
            'question':question,
            # 'end_time':end_time,
        }
        return render(request,"problem.html", context)
    else:
        
        starttime = str(question.contest_of.start_time)
        starttime = starttime[:19]

        if datetime.strptime(starttime, '%Y-%m-%d %H:%M:%S') < now:
            end_time= str(question.contest_of.end_time)
            context = {
                'question':question,
                'end_time':end_time,
            }
            return render(request,"problem.html", context)
        else:
            raise Http404()



@login_required(login_url='/')
def view_contest(request,pk):
    contest_ = Contest.objects.filter(pk =pk)[0]
    questions_ = Question.objects.filter(contest_of = contest_)
    end_time_ = str(contest_.end_time)
    UTC = pytz.utc
    
    timeZ_Kl = pytz.timezone('Asia/Kolkata') 

    
    dt_Kl = datetime.now(timeZ_Kl)

    
    utc_Kl = dt_Kl.astimezone(UTC)
    now2 = dt_Kl.strftime('%Y-%m-%d %H:%M:%S')
    now = datetime.strptime(now2, '%Y-%m-%d %H:%M:%S')

    
    score_cards = ScoreCard.objects.filter(_contest =contest_).order_by('-score')
   
   
    scr_crd = ScoreCard.objects.filter(_contest = contest_, prof = Profile.objects.filter(user = request.user)[0])
    
    solved_or_not = SolvedOrNot.objects.filter(owner= Profile.objects.filter(user = request.user)[0])
    if solved_or_not:

        
        solved_or_not = solved_or_not[0].probs.all()
    else:
        solved_or_not =[]


    prof_ = Profile.objects.filter(user = request.user)[0]
    if Bookmark.objects.filter(owner = prof_):
            bookmark = Bookmark.objects.filter(owner = prof_)[0]
            bookmark_ques = bookmark.questions.all()
    else:
        bookmark  = None
        bookmark_ques =[]

    

    starttime = str(contest_.start_time)
    starttime = starttime[:19]
    if datetime.strptime(starttime, '%Y-%m-%d %H:%M:%S') > now:
        
        start_time = str(contest_.start_time)
        context = {
            'contest' : contest_,
            'questions': questions_,
            'start_time':start_time,
            'solved_or_not':solved_or_not,
            'bookmarked':bookmark_ques,
            'now':now,
            
            "now2":now2,
            
            
            
        }
    else:
        if contest_.status == "AC":
            scorecard_check = ScoreCard.objects.filter(_contest = contest_, prof = Profile.objects.filter(user = request.user)[0])
            if scorecard_check:
                print("scorecard exists")
            else:
                score_card = ScoreCard(_contest = contest_, prof = Profile.objects.filter(user = request.user)[0])
                score_card.save()
                print(score_card)
            
        context = {
        'contest' : contest_,
        'questions': questions_,
        'end_time':end_time_,
        'score_cards':score_cards,
        'solved_or_not':solved_or_not,
        'bookmarked':bookmark_ques,
        'now':now,
      
        "now2":now2
        }



    
    return render(request, "view_contest.html", context)

@login_required(login_url='/')
def add_contest(request):
    if request.method =="POST":

        title= request.POST.get('title','')
        start_time = request.POST.get('start_time','')
        end_time = request.POST.get('end_time', '')
        difficulty = request.POST.get('difficulty', '')
        unique_id = uuid.uuid4()
        start_time = start_time.replace("T", " ")
        end_time = end_time.replace("T"," ")
        
        print(start_time)
        print(end_time)
        print(title)
        print(difficulty)
        print(unique_id)


        prof = Profile.objects.filter(user=request.user)[0]
        



        if start_time < end_time:
            print("correct")



            contest_ = Contest(title =title, start_time=start_time, end_time = end_time, unique_id = unique_id, difficulty = difficulty,curator = prof)
            contest_.save()
            search_contest = Contest.objects.filter(unique_id= unique_id)[0]
            print(search_contest.title)
            context={
                'contest':search_contest,
            }
            return redirect("/problem_setting/" + str(search_contest.pk))
        else:
            messages.warning(request, "Start Time Must Be Less Than End Time !!")
            return redirect("/profile/"+ str(prof.pk))

    else:
        raise Http404()

@login_required(login_url='/')
def edit_contest(request, pk):
    if request.method =="POST":
        title= request.POST.get('title_edit','')
        start_time = request.POST.get('start_time_edit','')
        end_time = request.POST.get('end_time_edit', '')
        difficulty = request.POST.get('difficulty_edit', '')
        
        start_time = start_time.replace("T", " ")
        end_time = end_time.replace("T"," ")
        contest_ = Contest.objects.filter(pk=pk)[0]
        prof_ = contest_.curator
        print(title)
        print(start_time)
        print(end_time)
        if start_time < end_time:
        
            contest_.title = title
            contest_.start_time = start_time
            contest_.end_time = end_time
            contest_.difficulty = difficulty
            contest_.save()
            return redirect('/profile/'+ str(prof_.pk))
        else:
            messages.warning(request, "Start Time Must Be Less Than End Time !!")
            return redirect("/profile/"+ str(prof_.pk))

    else:
        raise Http404()


@login_required(login_url='/')
def delete_contest(request, pk):
    contest_ = Contest.objects.filter(pk=pk)[0]
    prof_ = contest_.curator
    if request.user == prof_.user:
        contest_.delete()
    return redirect('/profile/'+ str(prof_.pk))

@login_required(login_url='/')
def edit_problem(request,pk):
    problem_ = Question.objects.filter(pk=pk)[0]
    contest_ =problem_.contest_of.pk
    if request.method == "POST":
 
        description = request.POST.get('description_edit','')
        score = request.POST.get('score_edit','')
        time_limit = request.POST.get('time_limit_edit','')
        difficulty = request.POST.get('difficulty_edit', '')
        problem_id = request.POST.get('problem_id_edit','')
        # contest_uid = request.POST.get('contest_uid','')
        title = request.POST.get('title_edit','')
        category = request.POST.get('category_edit','')
        dsalgo = DsAlgoTopics.objects.filter(pk = category)[0]

        
        problem_.description =description
        problem_.score = score
        problem_.time_limit =time_limit
        problem_.dfficulty =difficulty
        problem_.title =title
        problem_.category =dsalgo
        problem_.save()
        
        return redirect("/problem_setting/"+str(contest_))
    else:
        raise Http404()



@login_required(login_url='/')
def normal_problems(request):
    not_contest_ = Contest.objects.filter(unique_id = "not_a_contest",title="Not A contest")[0]

    probs = Question.objects.filter(contest_of = not_contest_).order_by("-curation_time")
    solved_or_not = SolvedOrNot.objects.filter(owner= Profile.objects.filter(user = request.user)[0])
    prof_ =Profile.objects.filter(user = request.user)[0]
    if Bookmark.objects.filter(owner = prof_):
            bookmark = Bookmark.objects.filter(owner = prof_)[0]
            bookmarked_ques = bookmark.questions.all()
    else:
        bookmark  = None
        bookmarked_ques =[]
    if solved_or_not:

        
        solved_or_not = solved_or_not[0].probs.all()
    else:
        solved_or_not =[]
    dsalgos = DsAlgoTopics.objects.all()
    context ={
        'probs':probs,
        'solved_or_not':solved_or_not,
        'bookmarked':bookmarked_ques,
        'dsalgos':dsalgos
    }

    return render(request, "normal_problems.html",context)
    
@login_required(login_url='/')
def normal_problems_filtered(request):

    if request.method == "GET":
        filter_text = request.GET.get('filter_text', "")
        not_contest_ = Contest.objects.filter(unique_id = "not_a_contest",title="Not A contest")[0]

        probs = Question.objects.filter(contest_of = not_contest_, category = DsAlgoTopics.objects.filter(name=filter_text)[0]).order_by("-curation_time")
        solved_or_not = SolvedOrNot.objects.filter(owner= Profile.objects.filter(user = request.user)[0])
        prof_ =Profile.objects.filter(user = request.user)[0]
        if Bookmark.objects.filter(owner = prof_):
                bookmark = Bookmark.objects.filter(owner = prof_)[0]
                bookmarked_ques = bookmark.questions.all()
        else:
            bookmark  = None
            bookmarked_ques =[]
        if solved_or_not:

            
            solved_or_not = solved_or_not[0].probs.all()
        else:
            solved_or_not =[]
        dsalgos = DsAlgoTopics.objects.all()
        context ={
            'probs':probs,
            'solved_or_not':solved_or_not,
            'bookmarked':bookmarked_ques,
            'dsalgos':dsalgos,
            'filter_text':filter_text
        }

        return render(request, "normal_problems_filtered.html",context)
    else:
        raise Http404()



@login_required(login_url='/')
def profile_visit(request,pk):
    prof_ = Profile.objects.filter(pk=pk)[0]
    if prof_._type == "CU":
        contests_ = Contest.objects.filter(curator = Profile.objects.filter(user = request.user)[0]).order_by('-curation_time')
        probs_w_c = Question.objects.filter(prof_w_c= Profile.objects.filter(user = request.user)[0],contest_of =Contest.objects.filter(unique_id = "not_a_contest",title="Not A contest")[0]).order_by('-curation_time') 
        print(probs_w_c)
        print(contests_) 
        print(Contest.objects.filter(unique_id = "not_a_contest",title="Not A contest"))
        context={
            'contests':contests_,
            'prof':prof_,
            'problems_w_c': probs_w_c,
            'dsalgos':DsAlgoTopics.objects.all()
        }
        # print(prof_)
        # print(contests_)

        return render(request, "profile_curator.html",context)
    else:


        solved_or_not = SolvedOrNot.objects.filter(owner= Profile.objects.filter(user = request.user)[0])
        if solved_or_not:

            
            solved_or_not = solved_or_not[0].probs.all()
        else:
            solved_or_not =[]


        #for contests participated 
        score_cards = len(ScoreCard.objects.filter(prof = prof_))
        print(score_cards)
        



        # for progress bar
        total_points =int(prof_.total_points)
        
        progress = 0
        if total_points >= 50 and total_points<100:
            progress = int(100- ((100-total_points)/50)*100)
            start_point = 50 
            end_point =100
        elif total_points >= 100 and total_points<200:
            progress = int(100- ((200-total_points)/100)*100)
            start_point = 100 
            end_point =200
            
        elif total_points >= 200 and total_points<400:
            progress = int(100- ((400-total_points)/200)*100)
            start_point = 200 
            end_point =400



        elif total_points >=400:
            progress = 100
            start_point = 400
            end_point = 0
        else:
            progress = total_points*2
            start_point =0
            end_point =  50



        
        if Bookmark.objects.filter(owner = prof_):
            bookmark = Bookmark.objects.filter(owner = prof_)[0]
            bookmarked_ques = bookmark.questions.all()
        else:
            bookmark  = None
            bookmarked_ques =[]

        context ={
            "bookmarked_ques":bookmarked_ques,
            'bookmark':bookmark,
            'prof':prof_,
            'solved_or_not':solved_or_not,
            'contests_no':score_cards,
            'progress':progress,
            'start_point':start_point,
            'end_point':end_point,
        }
        return render(request, "profile_learner.html",context)
    
@login_required(login_url='/')
def delete_bookmark(request, bk, qk):
    book_mark =Bookmark.objects.filter(pk = bk)[0]
    if request.user == book_mark.owner.user:
        que_ = Question.objects.filter(pk=qk)[0]
        book_mark.questions.remove(que_)
        return redirect("/profile/" + str(book_mark.owner.user.pk))
    else:
        raise Http404()




def register(request):
    if request.user.is_authenticated:
        prof_ = Profile.objects.filter(user =request.user)
        if prof_[0]._type =="LR":
            return redirect("/learner_home")
        else:

            return redirect('/curator_home')
        
    
    else:
        return render(request,"register.html")


@login_required(login_url='/')
def learner_home(request):
    return render(request, "learner_home.html")


@login_required(login_url='/')
def curator_home(request):
    prof_ = Profile.objects.filter(user =request.user)[0]
    context ={
        'prof':prof_,
        'type':prof_._type
    }
    return render(request, "curator_home.html",context)


def register_curator(request):
    if request.user.is_authenticated:
        prof_ = Profile.objects.filter(user =request.user)
        if prof_[0]._type =="CU":
            return redirect("/curator_home")
        else:

            return redirect('/learner_home')
    else:
        return render(request,"register_curator.html")




"""
donor_mail = fulldet.email
        donor = fulldet.user.username
        donor_id =fulldet.user.pk
        #email to locator
        template_locator = render_to_string('Email_templates/email_to_donor.html',{'name':name, 'email':email, 'phone':phone, 'donor':donor, 'donor_id':donor_id})
        email_locator = EmailMessage(
            name + ' , Has Requested For Blood Donation',
            template_locator,
            settings.EMAIL_HOST_USER,
            [donor_mail],

            )
        email_locator.fail_silently = False
        email_locator.send()
"""



def signUp_curator(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        name = request.POST.get('name','')
        username = request.POST.get('username', '')
        password = request.POST.get('pass', '')
        conf_pass = request.POST.get('conf_pass','')
        usercheck = User.objects.filter(username =username)

        if len(username)>20:
            messages.warning(request,"User name is too long")
        elif usercheck:
            messages.warning(request, "User name already exists")
        elif password != conf_pass:
            messages.warning(request, "Passwords Do not Match")
        else:
            user_ = User.objects.create_user(
                first_name =name,
                password=password,
                username =username,
                email = email
            )
            user_.save()
            #email to locator
            user_det = User.objects.filter(username=username)[0]
            template_locator = render_to_string('Email_templates/email_to_admin.html',{'name':user_det.first_name, 'email':user_det.email, 'username': user_det.username})
            email_locator = EmailMessage(
                name + ' , Has Requested For Curator Role',
                template_locator,
                settings.EMAIL_HOST_USER,
                ["algogeek.mail@gmail.com"],

                )
            email_locator.fail_silently = False
            email_locator.send()
            messages.success(request,"Account Created Successfully, application for curator role sent")
        # return render(request, "register.html")
        return redirect('/register_curator')
    else:
        raise Http404()

def log_in_curator(request):
    if request.method =="POST":
        username = request.POST.get('username_login','')
        password = request.POST.get('pass_login','')
        print(username)
        print(password)
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request,user)
            return redirect('/curator_home')
        else:
            messages.warning(request, "Invalid Credentials")
            return redirect('/register_curator')



def signUp(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        name = request.POST.get('name','')
        username = request.POST.get('username', '')
        password = request.POST.get('pass', '')
        conf_pass = request.POST.get('conf_pass','')
        usercheck = User.objects.filter(username =username)

        if len(username)>20:
            messages.warning(request,"User name is too long")
        elif usercheck:
            messages.warning(request, "User name already exists")
        elif password != conf_pass:
            messages.warning(request, "Passwords Do not Match")
        else:
            user_ = User.objects.create_user(
                first_name =name,
                password=password,
                username =username,
                email = email
            )
            user_.save()
            messages.success(request,"Account Created Successfully")
        # return render(request, "register.html")
        return redirect('/register')
    else:
        raise Http404()
def log_in(request):
    if request.method =="POST":
        username = request.POST.get('username_login','')
        password = request.POST.get('pass_login','')
        print(username)
        print(password)
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request,user)
            return redirect('/learner_home')
        else:
            messages.warning(request, "Invalid Credentials")
            return redirect('/register')
@login_required(login_url='/')
def add_to_bookmark(request, pk):
    if request.is_ajax():
        pk_id = request.POST.get('pk','')
        question_ =Question.objects.filter(pk=pk)[0]
        bookmark = Bookmark.objects.filter(owner = Profile.objects.filter(user = request.user)[0])
        if bookmark:
            if question_ not in bookmark:
                bookmark[0].questions.add(question_)
        else:
            bookmark_ = Bookmark(owner= Profile.objects.filter(user = request.user)[0] )
            bookmark_.save()
            bookmark = Bookmark.objects.filter(owner = Profile.objects.filter(user = request.user)[0])
            bookmark[0].questions.add(question_)
        return JsonResponse({'message':"bookmarks added"},safe=False)

@login_required(login_url='/')
def problem_w_c(request,pk):
    problem_ = Question.objects.filter(pk = pk)[0]
    context ={
        'question':problem_,
    }
    return render(request, "problem_without_contest.html",context)








"""
@login_required(login_url='/register')
def submit_code(request,pk):
    question =Question.objects.filter(pk=pk)[0]
    now = datetime.now()
    now = pytz.utc.localize(now)
    if request.is_ajax():
        code_ = request.POST['code_']
        lang = request.POST['lang']
        # print(lang)
        data = {
            'client_secret': '01f0859bab2c86c1e6a1c1fb549f27a805baad59' ,
            'async':0,
            'source':code_,
            'lang':lang,
            'time_limit':question.time_limit,
            'memory_limit': 262144,

        }
        testCases = Testcase.objects.filter(quest = question)
        print("tescases")
        print(testCases)
        count = 0

        for testCase in testCases:
           
            if len(testCase.input_cases)> 0:
                data["input"] = testCase.input_cases
                print("input giiven")
                
            resp = requests.post(RUN_URL, data=data)
            resp_json = resp.json()
            
            if resp_json['run_status']['status']=='AC':
                output_ = resp_json['run_status']['output'] 
                output_ =str(output_)
                
                time_limit_reached = resp_json['run_status']['time_used']
                
                string =testCase.test_cases
        
                string_ = str(string.replace(" ", "").replace("\n",""))
                output_ =output_.replace(" ", "").replace("\n","")
                
            
               
                print(''.join(string_.splitlines()))
                
                print(''.join(output_.splitlines()))


                in_put = ''.join(string_.splitlines())
                out_put =''.join(output_.splitlines())


                if in_put==out_put:

                    print("test cases passed")
                    count = count +1
                    print(count)

            elif resp_json['run_status']['status']=='TLE':
                msg = {
                            'message':"Time Limit Exceeded",
                        'output': resp_json['run_status']['output']
                        }
                return JsonResponse(msg,safe=False)

            else:
                print("Compilation Error")
                print(resp_json)
                msg ={
                        'message':"Compilation Error",
                    
                    }
                return JsonResponse(msg,safe=False)
                
                    
                    
        if count == len(testCases):
            print("all passed")

            
            #for dry run by curator

            if request.user == question.contest_of.curator.user:
                print('curator visited')
                
            else:
                

                #solved r not
                solved_check = SolvedOrNot.objects.filter(owner =Profile.objects.filter(user =request.user)[0])
                if solved_check :
                    solved_check[0].probs.add(question)
                else:
                    solved_or_not = SolvedOrNot(owner =Profile.objects.filter(user =request.user)[0])
                    solved_or_not.save()
                    solved_check = SolvedOrNot.objects.filter(owner =Profile.objects.filter(user =request.user)[0])[0]
                    solved_check.probs.add(question)
                



                # checking scorecard
                scorecard_check = ScoreCard.objects.filter(_contest = question.contest_of , prof = Profile.objects.filter(user =request.user)[0], _ques= question)
                scoredcard_check_2 =ScoreCard.objects.filter(_contest = question.contest_of , prof = Profile.objects.filter(user =request.user)[0])
                print(scoredcard_check_2)
                if scorecard_check:
                    print("already got marks")
                elif scoredcard_check_2:
                    scoredcard_check_2= scoredcard_check_2[0]
                    if question.contest_of.end_time > now:
                        scoredcard_check_2._ques.add(question)
                        scoredcard_check_2.score = scoredcard_check_2.score + question.score
                        scoredcard_check_2.time = now
                        scoredcard_check_2.save()
                        scorecards_for_total_points = ScoreCard.objects.filter(prof = Profile.objects.filter(user = request.user)[0])
                        #adding total points 
                        total = 0
                        for scr in scorecards_for_total_points:
                            total = total + int(scr.score)
                        prof_of_the_user = Profile.objects.filter(user =request.user)[0]
                        prof_of_the_user.total_points = total
                        prof_of_the_user.save()
                            


            msg ={
                'message':"Test Cases Passed",
                'output': resp_json['run_status']['output']
                }

        else:
            msg= {
                'message':"Test Cases Not Passed",
                'output':resp_json['run_status']['output']
            }


            

        return JsonResponse(msg,safe=False)
"""


@login_required(login_url='/')
def submit_code_w_c(request,pk):
    question =Question.objects.filter(pk=pk)[0]
  
    if request.is_ajax():
        code_ = request.POST['code_']
        lang = request.POST['lang']
       
        data = {
            'client_secret': '01f0859bab2c86c1e6a1c1fb549f27a805baad59' ,
            'async':0,
            'source':code_,
            'lang':lang,
            'time_limit':question.time_limit,
            'memory_limit': 262144,

        }


        testCases = Testcase.objects.filter(quest = question)
        print("tescases")
        print(testCases)
        count = 0
        for testCase in testCases:

            if len(testCase.input_cases)> 0:
                data["input"] = testCase.input_cases
                

            

            


            resp = requests.post(RUN_URL, data=data)
            resp_json = resp.json()
            
            if resp_json['run_status']['status']=='AC':
                output_ = resp_json['run_status']['output'] 
                output_ =str(output_)
                
                # time_limit_reached = resp_json['run_status']['time_used']
                
                string = testCase.test_cases
        
                string_ = str(string.replace(" ", "").replace("\n",""))
                output_ =output_.replace(" ", "").replace("\n","")
                
            
                print(resp_json)
                print(''.join(string_.splitlines()))
                
                print(''.join(output_.splitlines()))


                in_put = ''.join(string_.splitlines())
                out_put =''.join(output_.splitlines())


                if in_put==out_put:
                    print("test case passed")
                    count = count +1
                    print(count)
            elif resp_json['run_status']['status']=='TLE':
                msg = {
                            'message':"Time Limit Exceeded",
                        'output': resp_json['run_status']['output']
                        }
                return JsonResponse(msg,safe=False)

            else:
                print("Compilation Error")
                print(resp_json)
                msg ={
                        'message':"Compilation Error",
                    
                    }
                return JsonResponse(msg,safe=False)  

        if count == len(testCases):
            print("all passed")
              
            print(resp_json)
            
            #solved r not
            solved_check = SolvedOrNot.objects.filter(owner =Profile.objects.filter(user =request.user)[0])
            if solved_check :
                solved_check[0].probs.add(question)
            else:
                solved_or_not = SolvedOrNot(owner =Profile.objects.filter(user =request.user)[0])
                solved_or_not.save()
                solved_check = SolvedOrNot.objects.filter(owner =Profile.objects.filter(user =request.user)[0])[0]
                solved_check.probs.add(question)

            msg ={
                'message':"Test Cases Passed",
                'output': resp_json['run_status']['output']
            }
        else:
            msg= {
                'message':"Test Cases Not Passed",
                'output':resp_json['run_status']['output']
            }
        return JsonResponse(msg,safe=False)

    





def log_out(request):
    logout(request)
    return redirect("/")


def delete_prob_w_c(request,pk):
    question_ = Question.objects.filter(pk=pk)[0]
    if question_.prof_w_c.user == request.user:
        prof_pk = question_.prof_w_c.pk
        question_.delete()
        return redirect("/profile/"+str(prof_pk))
    else:
 
        raise Http404()

@login_required(login_url='/')
def searching(request):
    if request.method =="GET":
        search_text = request.GET.get("search_text","")
        search_results_ques = Question.objects.filter(title__icontains = search_text, contest_of = Contest.objects.filter(unique_id="not_a_contest")[0])
        
        search_results_contests =Contest.objects.filter(title__icontains = search_text).difference(Contest.objects.filter(unique_id="not_a_contest"))
        context ={
            'questions':search_results_ques,
            'contests':search_results_contests

        }
        return render(request,"searching.html",context)
    else:
        raise Http404()

