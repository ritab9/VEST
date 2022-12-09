from django.urls import path, register_converter
from . import views
#from .converters import DateConverter
#register_converter(DateConverter, 'date')

urlpatterns = [
    # data management urls school_admin

    path('school_year/<int:schoolid>/', views.school_year, name='school_year'),
    path('add_school_year/<int:schoolid>/', views.add_school_year, name='add_school_year'),
    path('manage_school_year/<int:schoolid>/<int:schoolyearid>/', views.manage_school_year, name='manage_school_year'),
    path('delete_school_year/<int:schoolid>/<int:schoolyearid>/', views.delete_school_year, name='delete_school_year'),
    path('school_settings/<int:schoolid>/', views.school_settings, name="school_settings"),

    # data management urls vocational_coordinator
    path('department_list/<int:schoolid>/', views.department_list, name='department_list'),
    path('manage_department/<int:schoolid>/', views.manage_department, name='manage_department'),

    path('skill_list/<int:schoolid>/', views.skill_list, name='skill_list'),
    path('manage_skill/<int:departmentid>/', views.manage_skill, name='manage_skill'),

    path('instructor_assignment/<int:schoolid>/', views.instructor_assignment, name='instructor_assignment'),
    path('manage_instructor_assignment/<int:schoolid>/', views.manage_instructor_assignment,
         name='manage_instructor_assignment'),

    path('student_assignment/<int:schoolid>/', views.student_assignment, name='student_assignment'),
    path('manage_student_assignment/<int:schoolid>/<int:quarterid>/', views.manage_student_assignment,
         name='manage_student_assignment'),
    path('student_assignment_student_filter/<int:schoolid>/', views.student_assignment_student_filter,
         name='student_assignment_student_filter'),
    path('student_assignment_department_filter/<int:schoolid>/', views.student_assignment_department_filter,
         name='student_assignment_department_filter'),
    path('vc_validate_grades/<int:schoolid>/', views.vc_validate_grades, name="vc_validate_grades"),

    # Instructor links
    path('grade_list/<int:userid>/', views.grade_list, name='grade_list'),
    path('grade_list_all/<int:userid>/', views.grade_list_all, name='grade_list_all'),

    path('initiate_grade_entry/<int:schoolid>/', views.initiate_grade_entry, name='initiate_grade_entry'),
    path('add_grade/<int:quarterid>/<str:type>/<int:departmentid>/<str:evaluation_date>/<int:instructorid>/',
         views.add_grade, name='add_grade'),
    path('add_skills_grade/<int:quarterid>/<int:departmentid>/<str:evaluation_date>/<int:instructorid>/',
         views.add_skill_grade, name='add_skill_grade'),
    # AJAX to get the level that belongs to that student
    path('get_level', views.get_level, name='get_level'),
    path('finalize_grade/<int:gradeid>/', views.finalize_grade, name="finalize_grade"),
    path('finalize_skill_grade/<int:gradeid>/', views.finalize_skill_grade, name="finalize_skill_grade"),

    path('student_vocational_info/<int:studentid>/', views.student_vocational_info, name="student_vocational_info"),

    # parent links
    path("parent_page/<int:parentid>/", views.parent_page, name="parent_page"),
    path("student_grades/<int:studentid>/", views.student_grades, name="student_grades"),

    # student links
    path("student_page/<int:studentid>/", views.student_page, name="student_page"),
    # path("student_grades/<int:studentid>/", views.student_grades, name="student_grades"),

]