from django.http.response import Http404
from django.shortcuts import redirect, render,HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from . models import *
import uuid
from django.contrib import messages
# Create your views here.
@login_required(login_url='/')
def team_home(request):
    rooms = Room.objects.filter(status="PB")
    your_rooms = Room.objects.filter(owner=Profile.objects.filter(user = request.user)[0]) 
    context ={
        'rooms':rooms,
        'your_rooms':your_rooms

    }
    return render(request, "team/team_home.html", context)


@login_required(login_url='/')
def join_room(request,pk):
    if request.method == "POST":
        unique_id = request.POST.get('unique_id', '')
        room_ = Room.objects.filter(unique_id =unique_id)
        if room_.exists():

            return redirect("/team/join_room/" + str(room_[0].pk))
        else:
            messages.warning(request, "Invalid Room ID")
            return redirect("/team/")
    else:
        room_pk = Room.objects.filter(pk =pk)[0]
        room_pk.members.add(Profile.objects.filter(user = request.user)[0])
        chats = Chat.objects.filter(room_of =room_pk).order_by('time')
        context ={
            'room':room_pk,
            'chats':chats
        }
        return render(request, 'team/room.html',context)

@login_required(login_url='/')
def create_room(request):
    if request.method =="POST":
        unique_id = str(uuid.uuid4())[:8]
        room_name = request.POST.get("room_name",'')
        room_desc = request.POST.get('room_desc','')
        status = request.POST.get('status', '')
        room_create = Room(owner = Profile.objects.filter(user = request.user)[0], name = room_name, unique_id=unique_id,status =status, description = room_desc)
        room_create.save()
        return redirect("/team/")
    else:
        raise Http404()
def delete_room(request,pk):
    room_ = Room.objects.filter(pk=pk)[0]
    if room_.owner == Profile.objects.filter(user = request.user)[0]:
        room_.delete()
        return redirect("/team/")
    else:
        raise Http404()

def send_message(request):
    if request.is_ajax():
        room_pk = request.POST.get('room_pk', '')
        message = request.POST.get('message','')
        room_ = Room.objects.filter(pk = room_pk)[0]
        chatter = Profile.objects.filter(user = request.user)[0]
        chat_ = Chat(chatter=chatter, room_of =room_, message=message)
        chat_.save()
        msg ={
            'msg':'message sent successfully'
        }
        return JsonResponse(msg,safe=False)
    else:
        raise Http404()

    
# def load_messages(request, pk):
#     if request.is_ajax():
#         room_ = Room.objects.filter(pk = pk)[0]
#         messages = Chat.objects.filter(room_of =  room_).order_by('time')

