from django.db import models
from sub_app.models import *
TYPE_OF_ROOM =[
    ('PR','Private'),
    ('PB','Public')
]
# Create your models here.
class Room(models.Model):
    owner = models.ForeignKey(Profile,on_delete=models.CASCADE)
    members = models.ManyToManyField(Profile,related_name="members")
    name = models.CharField(max_length=100)
    unique_id = models.CharField(max_length=1000)
    status = models.CharField(max_length=2, choices=TYPE_OF_ROOM,default='PB')
    description = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.name) + ' ' + str(self.unique_id)
class Chat(models.Model):
    chatter = models.ForeignKey(Profile, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    message= models.TextField()
    room_of = models.ForeignKey(Room, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.chatter.user.username) +" room: " +str(self.room_of)


