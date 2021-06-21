from django.urls import path
from . import views
urlpatterns = [
    path('', views.team_home, name="team_home"),
    path("join_room/<int:pk>", views.join_room, name="join_room"),
    path('create_room', views.create_room, name='create_room'),
    path('delete_room/<int:pk>', views.delete_room, name="delete_room"),
    path('send_message', views.send_message, name="send_message")
]