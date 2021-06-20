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
    path('signUp_curator', views.signUp_curator, name="signUp_curator"),
    path('log_in_curator',views.log_in_curator, name="log_in_curator"),
    path("edit_contest/<int:pk>", views.edit_contest, name='edit_contest'),
    path('delete_contest/<int:pk>', views.delete_contest, name="delete_contest"),
    path('edit_problem/<int:pk>', views.edit_problem, name="edit_problem"),
    path('view_contest/<int:pk>', views.view_contest, name="view_contest"),
    path('add_to_bookmark/<int:pk>', views.add_to_bookmark, name="add_to_bookmark"),
    path("problem_w_c/<int:pk>", views.problem_w_c, name="problem_w_c"),
    path('submit_code_w_c/<int:pk>', views.submit_code_w_c, name="submit_code_w-c"),
    path('normal_problem_setting/<int:pk>', views.normal_problem_setting, name="normal_problem_setting"),
    path('normal_problem_edit/<int:pk>', views.normal_problem_edit, name="normal_problem_edit"),
    path('normal_problems', views.normal_problems, name="normal_problems"),
    path('delete_bookmark/<int:bk>/<int:qk>', views.delete_bookmark, name="delete_bookmark"),
    path("add_test_cases/<int:pk>", views.add_test_cases, name="add_test_cases"),
    path("add_test_cases_page/<int:pk>", views.add_test_cases_page, name="add_test_cases_page"),
    path("edit_test_case/<int:pk>", views.edit_test_case, name='edit_test_case'),
    path('learner_home', views.learner_home, name="learner_home"),
    path('curator_home', views.curator_home, name="curator_home"),
    path('register_curator', views.register_curator, name="register_curator"),
    path('log_out', views.log_out, name="log_out"),
    path('delete_prob_w_c/<int:pk>', views.delete_prob_w_c, name="delete_prob_w_c"),
    path('searching', views.searching,name ="searching" ),
    path("normal_problems_filtered", views.normal_problems_filtered, name="normal_problems_filtered")

    
    



    

]