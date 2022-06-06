from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    path('crash/', views.crash, name='crash'),
#login paths
    path('', views.logoutuser, name='logout'),
    path('login/', views.loginuser, name='login'),
    path('logout/', views.logoutuser, name='logout'),

    path('admin/', views.loginuser, name='admin'),

    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="users/password_reset.html"),
         name="reset_password"),
    path('reset_password_sent/',
         auth_views.PasswordResetDoneView.as_view(template_name="users/password_reset_sent.html"),
         name="password_reset_done"),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name="users/password_reset_form.html"),
         name='password_reset_confirm'),
    path('reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"),
         name="password_reset_complete"),

#isei admin paths
    path('isei_admin_dashboard/', views.isei_admin_dashboard, name='isei_admin_dashboard'),
    path('isei_data_summary/', views.isei_data_summary, name='isei_data_summary'),

    path('add_school/', views.add_school, name='add_school'),
    path('add_school_admin/', views.add_school_admin, name='add_school_admin'),

#school admin paths
    path('school_admin_dashboard/<str:schoolid>/', views.school_admin_dashboard, name='school_admin_dashboard'),
    
    path('manage_school_staff/<str:schoolid>/', views.manage_school_staff, name='manage_school_staff'),
    path('manage_inactive_school_staff/<str:schoolid>/', views.manage_inactive_school_staff, name='manage_inactive_school_staff'),
    path('add_school_staff/<str:schoolid>/', views.add_school_staff, name='add_school_staff'),
    path('update_school_staff/<str:userid>/', views.update_school_staff, name='update_school_staff'),
    path('delete_school_staff/<str:userid>/', views.delete_school_staff, name='delete_school_staff'),

    path('manage_students/<str:schoolid>/', views.manage_students, name='manage_students'),
    path('manage_inactive_students/<str:schoolid>/', views.manage_inactive_students, name='manage_inactive_students'),
    path('add_student/<str:schoolid>/', views.add_student, name='add_student'),
    path('update_student/<str:userid>/', views.update_student, name='update_student'),
    path('delete_student/<str:userid>/', views.delete_student, name='delete_student'),
    path('mark_inactive_students/<str:schoolid>/', views.mark_inactive_students, name='mark_inactive_students'),

    #path('manage_parents/<str:schoolid>/', views.manage_parents, name='manage_parents'),
    #path('manage_inactive_parents/<str:schoolid>/', views.manage_inactive_parents, name='manage_inactive_parents'),
    path('add_parent/<str:userid>/', views.add_parent, name='add_parent'),
    path('update_parent/<str:userid>/', views.update_parent, name='update_parent'),
    path('delete_parent/<str:userid>/<str:studentid>/', views.delete_parent, name='delete_parent'),

    path('add_parent_from_list/<str:userid>/<str:listtype>/', views.add_parent_from_list, name='add_parent_from_list'),

]