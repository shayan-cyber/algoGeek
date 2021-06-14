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
    path('log_in',views.log_in, name="log_in"),
    path("edit_contest/<int:pk>", views.edit_contest, name='edit_contest'),
    path('delete_contest/<int:pk>', views.delete_contest, name="delete_contest"),
    path('edit_problem/<int:pk>', views.edit_problem, name="edit_problem"),
    path('view_contest/<int:pk>', views.view_contest, name="view_contest"),
    path('add_to_bookmark/<int:pk>', views.add_to_bookmark, name="add_to_bookmark"),
    path("problem_w_c/<int:pk>", views.problem_w_c, name="problem_w_c"),
    path('submit_code_w_c/<int:pk>', views.submit_code_w_c, name="submit_code_w-c")



    

]