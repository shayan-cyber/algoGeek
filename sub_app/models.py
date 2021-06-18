from django.db import models
from django.contrib.auth.models import User
from requests.api import request
DIFFICULTY_CHOICES =[
    ('ES', 'Easy'),
    ('MD', 'Medium'),
    ('HD', 'Hard'),
    ('VH', 'Very Hard'),
    ('EX', 'Expert')

]

DSALGO_TYPES =[
    ('DS','Data Structures'),
    ('AL', 'Algorithms')
]



TYPE_OF_PROFILE =[
    ('CU','Curator'),
    ('LR','Learner')
]
STATUS_CONTEST = [
    ('AC', 'Active'),
    ('IA', 'Inactive')
]
# Create your models here.
class Profile(models.Model):
    _type = models.CharField(max_length=2, choices=TYPE_OF_PROFILE,default='LR')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=100,default=" ")
    total_points = models.IntegerField(default=0)
    def __str__(self):
        return str(self.user.username)

class Contest(models.Model):
    title = models.CharField(max_length = 50)
    unique_id = models.CharField(max_length=200, default="")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    difficulty = models.CharField(max_length=2,choices=DIFFICULTY_CHOICES, default='MD')
    curation_time = models.DateTimeField(auto_now_add=True)
    curator = models.ForeignKey(Profile, on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=STATUS_CONTEST, default="AC")
    def __str__(self):
        return str(self.title)

    
class DsAlgoTopics(models.Model):
    type = models.CharField(max_length=2, choices=DSALGO_TYPES,default='DS')
    name = models.CharField(max_length=100)
    def __str__(self):
        return str(self.name)





class Question(models.Model):
    title = models.CharField(max_length=400)
    description= models.TextField()
    time_limit = models.IntegerField()
    # test_cases = models.TextField()
    # input_cases = models.TextField(null=True, blank=True)
    # test_case_mult = models.ForeignKey
    curation_time = models.DateTimeField(auto_now_add=True)
    difficulty = models.CharField(max_length=2,choices=DIFFICULTY_CHOICES, default='MD')
    category = models.ForeignKey(DsAlgoTopics, on_delete=models.CASCADE, null=True,blank=True)
    contest_of = models.ForeignKey(Contest, on_delete=models.CASCADE, null=True,blank=True)
    prof_w_c = models.ForeignKey(Profile, on_delete=models.CASCADE,blank=True, null=True) 
    score = models.IntegerField(default=0)
    

    def __str__(self):
        return str(self.title)
class Testcase(models.Model):
    title = models.CharField(max_length=100)
    test_cases = models.TextField()
    input_cases = models.TextField()
    quest = models.ForeignKey(Question,on_delete=models.CASCADE)
    def __str__(self):
        return str(self.title) + " from " + str(self.quest.title)

#no use -->       
class NormalProblem(models.Model):
    title = models.CharField(max_length=400)
    description= models.TextField()
    time_limit = models.IntegerField()
    test_cases = models.TextField()
    input_cases = models.TextField(null=True, blank=True)
    curation_time = models.DateTimeField(auto_now_add=True)
    difficulty = models.CharField(max_length=2,choices=DIFFICULTY_CHOICES, default='MD')
    category = models.ForeignKey(DsAlgoTopics, on_delete=models.CASCADE, null=True,blank=True)
    curator = models.ForeignKey(Profile, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.title)

#no use<--

class ScoreCard(models.Model):
    _contest = models.ForeignKey(Contest, on_delete=models.CASCADE,blank=True, null=True)
    prof = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    score = models.IntegerField(default=0)
    _ques = models.ManyToManyField(Question, blank=True)
    time = models.DateTimeField(blank=True,null=True)
    def __str__(self):
        return str(self._contest) + " from " + str(self.prof)
class Bookmark(models.Model):
    questions = models.ManyToManyField(Question)
    owner = models.OneToOneField(Profile,on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=STATUS_CONTEST, default="AC")
    def __str__(self):
        return str(self.owner)


class SolvedOrNot(models.Model):
    owner = models.OneToOneField(Profile, on_delete=models.CASCADE, null=True, blank=True)
    probs = models.ManyToManyField(Question)
    def __str__(self):
        return str(self.owner)