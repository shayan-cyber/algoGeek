from django.urls import path
from . import views
urlpatterns =[
    path('', views.home, name="home"),
    path('run_code', views.run_code, name='run_code'),
    path('submit_code/<int:pk>', views.submit_code, name='submit_code'),
    path('problem_setting/<int:pk>', views.problem_setting, name="problem_setting"),
    path("contests", views.contests, name="contests"),
    path("problem/<int:pk>", views.problem, name="problem"),
    path("profile/<int:pk>", views.profile_visit, name="profile"),
    path("add_contest", views.add_contest, name="add_contest"),
    path('register', views.register, name='register'),
    path('signUp', views.signUp, name="signUp"),
    path('log_in',views.log_in, name="log_in")
    

]