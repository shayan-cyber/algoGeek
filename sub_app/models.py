from django.db import models
from django.contrib.auth.models import User
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

# Create your models here.

class Contest(models.Model):
    title = models.CharField(max_length = 50)
    unique_id = models.CharField(max_length=200, default="")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    difficulty = models.CharField(max_length=2,choices=DIFFICULTY_CHOICES, default='MD')
    curation_time = models.DateTimeField(auto_now_add=True, blank=True, null=True)
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
    test_cases = models.TextField()
    input_cases = models.TextField(null=True, blank=True)
    curation_time = models.DateTimeField(auto_now_add=True)
    difficulty = models.CharField(max_length=2,choices=DIFFICULTY_CHOICES, default='MD')
    category = models.ForeignKey(DsAlgoTopics, on_delete=models.CASCADE, null=True,blank=True)
    contest_of = models.ForeignKey(Contest, on_delete=models.CASCADE, null=True,blank=True) 
    

    def __str__(self):
        return str(self.title)
class Profile(models.Model):
    type = models.CharField(max_length=2, choices=TYPE_OF_PROFILE,default='LR')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=100,default=" ")
    def __str__(self):
        return str(self.user.username)
