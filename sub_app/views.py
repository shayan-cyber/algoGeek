from django.http.response import Http404
from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponseForbidden,HttpResponse
import requests
import json
from . models import Contest, Profile, Question,DsAlgoTopics
import uuid
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

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
            'time_limit':5,
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
    if request.is_ajax():
        code_ = request.POST['code_']
        lang = request.POST['lang']
        print(lang)
        data = {
            'client_secret': '01f0859bab2c86c1e6a1c1fb549f27a805baad59' ,
            'async':0,
            'source':code_,
            'lang':lang,
            'time_limit':5,
            'memory_limit': 262144,

        }
        if len(question.input_cases)> 0:
            data["input"] = question.input_cases
            print(question.input_cases)

        

        


        resp = requests.post(RUN_URL, data=data)
        resp_json = resp.json()
        
        if resp_json['run_status']['status']=='AC':
            output_ = resp_json['run_status']['output'] 
            print(str(output_))
            # print(str(question.test_cases))
            string = question.test_cases
            print(string)
            print (string.splitlines())
            print(output_.splitlines())


            if string.splitlines() == output_.splitlines():
                print("passed")
                msg ={
                    'message':"Test Cases Passed",
                    'output': resp_json['run_status']['output']
                }
            else:
                msg= {
                    'message':"Test Cases Not Passed",
                    'output':resp_json['run_status']['output']
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
        question = Question(title=title, description=description, time_limit=time_limit, test_cases = test_case, input_cases= input_case,difficulty=difficulty, category=dsalgo,contest_of =contest)

        question.save()

    context = {
        "contest":contest,
        'dsalgos':dsalgos,
        'ques':ques,
    }
    return render(request,"problem_setting.html",context)



@login_required(login_url='/register')
def contests(request):
    questions = Question.objects.all()
    context ={
        'ques':questions
    }
    return render(request,"contests.html",context)

@login_required(login_url='/register')
def problem(request, pk):
    question = Question.objects.filter(pk =pk)[0]
    context = {
        'question':question,
    }
    return render(request,"problem.html", context)


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
        




        contest_ = Contest(title =title, start_time=start_time, end_time = end_time, unique_id = unique_id, difficulty = difficulty,curator = prof)
        contest_.save()
        search_contest = Contest.objects.filter(unique_id= unique_id)[0]
        print(search_contest.title)
        context={
            'contest':search_contest,
        }
        return redirect("/problem_setting/" + str(search_contest.pk))

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
        
        contest_.title = title
        contest_.start_time = start_time
        contest_.end_time = end_time
        contest_.difficulty = difficulty
        contest_.save()
        return redirect('/profile/'+ str(prof_.pk))
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
        problem_.time_limit =time_limit
        problem_.dfficulty =difficulty
        problem_.title =title
        problem_.category =dsalgo
        problem_.save()
        
        return redirect("/problem_setting/"+str(contest_))
    else:
        raise Http404()

       
    



@login_required(login_url='/register')
def profile_visit(request,pk):
    prof_ = Profile.objects.filter(pk=pk)[0]
    if prof_.type == "CU":
        contests_ = Contest.objects.filter(curator = prof_).order_by("-curation_time")
        context={
            'contests':contests_,
            'prof':prof_
        }
        # print(prof_)
        # print(contests_)

    return render(request, "profile.html",context)
# def add_problem(request):
#     return render(request, "problem_setting.html")

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


