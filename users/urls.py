from django.urls import path
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

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
    path('school_admin_dashboard/<str:schoolID>/', views.school_admin_dashboard, name='school_admin_dashboard'),
    path('manage_school_staff/<str:schoolID>/', views.manage_school_staff, name='manage_school_staff'),
    path('manage_students/<str:schoolID>/', views.manage_students, name='manage_students'),

    path('add_school_staff/<str:schoolID>/', views.add_school_staff, name='add_school_staff'),

    path('update_school_staff/<str:userID>/', views.update_school_staff, name='update_school_staff'),
    path('delete_school_staff/<str:userID>/', views.delete_school_staff, name='delete_school_staff'),
]