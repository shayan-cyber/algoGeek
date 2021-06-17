import datetime
from django.http.response import Http404
from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponseForbidden,HttpResponse
import requests
import json
from . models import Contest, Profile, Question,DsAlgoTopics, ScoreCard, Bookmark, SolvedOrNot
import uuid
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from datetime import date,datetime
import pytz

# import datetime

# print(uuid.uuid4())
RUN_URL = "https://api.hackerearth.com/v3/code/run/"


def home(request):
   
    return render(request,"home.html")

@login_required(login_url='/register')
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
        if len(question.input_cases)> 0:
            data["input"] = question.input_cases
            # print(question.input_cases)

        

        


        resp = requests.post(RUN_URL, data=data)
        resp_json = resp.json()
        
        if resp_json['run_status']['status']=='AC':
            output_ = resp_json['run_status']['output'] 
            output_ =str(output_)
            
            time_limit_reached = resp_json['run_status']['time_used']
            # print(str(output_))
            # print(str(question.test_cases))
            string = question.test_cases
           
           





            x = len(output_)-2
            if output_[-2]==" " :

            
                print(len(output_))
                # print(output_[0:x])
                output_ = output_[0:(x)]
                print(output_)
            else:
                output_ = output_[0:(x+1)]

                print(output_)







            print(resp_json)
            print (string.splitlines())
            print(output_.splitlines())
            # print(string.splitlines()[0])


            if string.splitlines()==output_.splitlines():

                print("test cases passed")
                print(resp_json)
                # if float(time_limit_reached) <= float(question.time_limit):



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
                    scoredcard_check_2 =ScoreCard.objects.filter(_contest = question.contest_of , prof = Profile.objects.filter(user =request.user)[0])[0]
                    print(scoredcard_check_2)
                    if scorecard_check:
                        print("already got marks")
                    elif scoredcard_check_2:
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
                # else:
                #     msg ={
                #         'message':"Time Limit Exceeded",
                #         'output': resp_json['run_status']['output']
                #     }

            else:
                msg= {
                    'message':"Test Cases Not Passed",
                    'output':resp_json['run_status']['output']
                }


        elif resp_json['run_status']['status']=='TLE':
            msg = {
                        'message':"Time Limit Exceeded",
                       'output': resp_json['run_status']['output']
                     }

        else:
            print("Compilation Error")
            print(resp_json)
            msg ={
                    'message':"Compilation Error",
                  
                }

        return JsonResponse(msg,safe=False)


@login_required(login_url='/register')
def problem_setting(request, pk):
    contest = Contest.objects.filter(pk =pk)[0]
    dsalgos = DsAlgoTopics.objects.all()
    ques = Question.objects.filter(contest_of = contest).order_by('-curation_time')
    print(ques)

    print(contest)
    

    if request.method =='POST':
        test_case = request.POST.get('test_cases','')
        input_case = request.POST.get('input_cases','')
        score = request.POST.get('score','')
        description = request.POST.get('description','')
        time_limit = request.POST.get('time_limit','')
        difficulty = request.POST.get('difficulty', '')
        contest_id = request.POST.get('contest_id','')
        contest_uid = request.POST.get('contest_uid','')
        title = request.POST.get('title','')
        category = request.POST.get('category','')
        dsalgo = DsAlgoTopics.objects.filter(pk = category)[0]

        
        contest =Contest.objects.filter(pk = contest_id, unique_id = contest_uid)[0]
        print(contest)
        question = Question(title=title, description=description, score=score,time_limit=time_limit, test_cases = test_case, input_cases= input_case,difficulty=difficulty, category=dsalgo,contest_of =contest)

        question.save()

    context = {
        "contest":contest,
        'dsalgos':dsalgos,
        'ques':ques,
    }
    return render(request,"problem_setting.html",context)

@login_required(login_url='/register')
def normal_problem_setting(request,pk):
    dsalgos = DsAlgoTopics.objects.all()
    # ques = Question.objects.filter(contest_of = contest).order_by('-curation_time')
    prof_ = Profile.objects.filter(pk = pk)[0]

    not_contest = Contest.objects.filter(unique_id = "not_a_contest",title="Not A contest")[0]
    

    if request.method =='POST':
        test_case = request.POST.get('test_cases','')
        input_case = request.POST.get('input_cases','')
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
        question = Question(title=title, description=description, score=score,time_limit=time_limit, test_cases = test_case, input_cases= input_case,difficulty=difficulty, category=dsalgo,contest_of =contest)

        question.save()
        return redirect("/profile/" + str(pk))

    # context = {
    #     "contest":contest,
    #     'dsalgos':dsalgos,
        
    # }

    else:
        raise Http404()
@login_required(login_url='/register')  
def normal_problem_edit(request,pk):
    problem_ = Question.objects.filter(pk =pk)[0]
    if request.method == "POST":
        if problem_.prof_w_c == Profile.objects.filter(user = request.user)[0]:
            
            test_case = request.POST.get('test_cases_edit','')
            input_case = request.POST.get('input_cases_edit','')
            description = request.POST.get('description_edit','')
            score = 0
            time_limit = request.POST.get('time_limit_edit','')
            difficulty = request.POST.get('difficulty_edit', '')
            
            
            title = request.POST.get('title_edit','')
            category = request.POST.get('category_edit','')
            dsalgo = DsAlgoTopics.objects.filter(pk = category)[0]

            problem_.test_cases =test_case
            problem_.input_cases = input_case
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



@login_required(login_url='/register')
def contests(request):
    contests_ = Contest.objects.exclude(unique_id ="not_a_contest", title="Not A contest").order_by('-curation_time')



    for contest_ in contests_:
        if contest_.status =="AC":
            now = datetime.now()
            now = pytz.utc.localize(now)
           
            if now > contest_.end_time:
                print("done")
                contest_.status = "IA"
                contest_.save()
                print(contest_.status)
    active_contests = Contest.objects.filter(status = "AC").order_by('-curation_time').difference(Contest.objects.filter(unique_id ="not_a_contest", title="Not A contest").order_by('-curation_time')) 
    previous_contests = Contest.objects.filter(status ="IA").order_by("-curation_time").difference(Contest.objects.filter(unique_id ="not_a_contest", title="Not A contest").order_by('-curation_time'))  
    context ={
        'active_contests':active_contests,
        'previous_contests': previous_contests,
    }
    return render(request,"contests.html",context)

@login_required(login_url='/register')
def problem(request, pk):
    now = datetime.now()
    now = pytz.utc.localize(now)
    
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
        

        if question.contest_of.start_time < now:
            end_time= str(question.contest_of.end_time)
            context = {
                'question':question,
                'end_time':end_time,
            }
            return render(request,"problem.html", context)
        else:
            raise Http404()



@login_required(login_url='/register')
def view_contest(request,pk):
    contest_ = Contest.objects.filter(pk =pk)[0]
    questions_ = Question.objects.filter(contest_of = contest_)
    end_time_ = str(contest_.end_time)
    now = datetime.now()
    now = pytz.utc.localize(now)
    # print(end_time_)
    score_cards = ScoreCard.objects.filter(_contest =contest_).order_by('-score')
    # score_cards = score_cards.order_by("time")
    #checking for solved ques
   
    scr_crd = ScoreCard.objects.filter(_contest = contest_, prof = Profile.objects.filter(user = request.user)[0])
    
    solved_or_not = SolvedOrNot.objects.filter(owner= Profile.objects.filter(user = request.user)[0])
    if solved_or_not:

        
        solved_or_not = solved_or_not[0].probs.all()
    else:
        solved_or_not =[]

    boomarks_ = Bookmark.objects.filter(owner= Profile.objects.filter(user = request.user)[0])[0]
    boomark_ques = boomarks_.questions.all()

    


    if contest_.start_time > now:
        
        start_time = str(contest_.start_time)
        context = {
            'contest' : contest_,
            'questions': questions_,
            'start_time':start_time,
            'solved_or_not':solved_or_not,
            'bookmarked':boomark_ques
            
            
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
        'bookmarked':boomark_ques
        }



    
    return render(request, "view_contest.html", context)

@login_required(login_url='/register')
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

@login_required(login_url='/register')
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


@login_required(login_url='/register')
def delete_contest(request, pk):
    contest_ = Contest.objects.filter(pk=pk)[0]
    prof_ = contest_.curator
    if request.user == prof_.user:
        contest_.delete()
    return redirect('/profile/'+ str(prof_.pk))

@login_required(login_url='/register')
def edit_problem(request,pk):
    problem_ = Question.objects.filter(pk=pk)[0]
    contest_ =problem_.contest_of.pk
    if request.method == "POST":
        test_case = request.POST.get('test_cases_edit','')
        input_case = request.POST.get('input_cases_edit','')
        description = request.POST.get('description_edit','')
        score = request.POST.get('score_edit','')
        time_limit = request.POST.get('time_limit_edit','')
        difficulty = request.POST.get('difficulty_edit', '')
        problem_id = request.POST.get('problem_id_edit','')
        # contest_uid = request.POST.get('contest_uid','')
        title = request.POST.get('title_edit','')
        category = request.POST.get('category_edit','')
        dsalgo = DsAlgoTopics.objects.filter(pk = category)[0]

        problem_.test_cases =test_case
        problem_.input_cases = input_case
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



@login_required(login_url='/register')
def normal_problems(request):
    not_contest_ = Contest.objects.filter(unique_id = "not_a_contest",title="Not A contest")[0]

    probs = Question.objects.filter(contest_of = not_contest_).order_by("-curation_time")
    solved_or_not = SolvedOrNot.objects.filter(owner= Profile.objects.filter(user = request.user)[0])
    boomarks_ = Bookmark.objects.filter(owner= Profile.objects.filter(user = request.user)[0])[0]
    boomark_ques = boomarks_.questions.all()
    if solved_or_not:

        
        solved_or_not = solved_or_not[0].probs.all()
    else:
        solved_or_not =[]
    context ={
        'probs':probs,
        'solved_or_not':solved_or_not,
        'bookmarked':boomark_ques
    }

    return render(request, "normal_problems.html",context)
    



@login_required(login_url='/register')
def profile_visit(request,pk):
    prof_ = Profile.objects.filter(pk=pk)[0]
    if prof_._type == "CU":
        contests_ = Contest.objects.exclude(unique_id ="not_a_contest", title="Not A contest").order_by('-curation_time')
        probs_w_c = Question.objects.filter(prof_w_c= Profile.objects.filter(user = request.user)[0],contest_of =Contest.objects.filter(unique_id = "not_a_contest",title="Not A contest")[0]).order_by('-curation_time')  
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
        bookmark = Bookmark.objects.filter(owner = prof_)[0]
        bookmarked_ques = bookmark.questions.all()



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



        elif total_points >400:
            progress = 100
            start_point = 400
            end_point = 0
        else:
            progress = total_points*2
            start_point =0
            end_point =  50





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
    
@login_required(login_url='/register')
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
        return redirect('/contests')
    else:
        return render(request,"register.html")

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
            return redirect('/contests')
        else:
            messages.warning(request, "Invalid Credentials")
            return redirect('/register')
@login_required(login_url='/register')
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

@login_required(login_url='/register')
def problem_w_c(request,pk):
    problem_ = Question.objects.filter(pk = pk)[0]
    context ={
        'question':problem_,
    }
    return render(request, "problem_without_contest.html",context)

@login_required(login_url='/register')
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
        if len(question.input_cases)> 0:
            data["input"] = question.input_cases
            

        

        


        resp = requests.post(RUN_URL, data=data)
        resp_json = resp.json()
        
        if resp_json['run_status']['status']=='AC':
            output_ = resp_json['run_status']['output'] 
            time_limit_reached = resp_json['run_status']['time_used']
            output_ = str(output_)
            
            string = question.test_cases
           
           





            x = len(output_)-2
            if output_[-2]==" " :

            
                print(len(output_))
                # print(output_[0:x])
                output_ = output_[0:(x)]
                print(output_)
            else:
                output_ = output_[0:(x+1)]
                
                print(output_)







            print(resp_json)
            print (string.splitlines())
            print(output_.splitlines())
            if string.splitlines() == output_.splitlines():
                print("test cases passed")
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
                # else:
                #     msg ={
                #         'message':"Time Limit Exceeded",
                #         'output': resp_json['run_status']['output']
                #     }

            else:
                msg= {
                    'message':"Test Cases Not Passed",
                    'output':resp_json['run_status']['output']
                }


        elif resp_json['run_status']['status']=='TLE':
            msg = {
                        'message':"Time Limit Exceeded",
                       'output': resp_json['run_status']['output']
                     }

        else:
            print("Compilation Error")
            print(resp_json)
            msg ={
                    'message':"Compilation Error",
                  
                }

        return JsonResponse(msg,safe=False)
        

