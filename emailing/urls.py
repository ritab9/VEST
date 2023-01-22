from django.urls import path

from . import views

urlpatterns = [

    path('message_list/', views.message_list, name='message_list'),
    path('message_list/<str:school_id>/', views.message_list, name='message_list'),

    path('create_default_message/', views.create_default_message, name='create_default_message'),
    path('edit_default_message/<str:message_id>/', views.edit_default_message, name='edit_default_message'),
    path('delete_default_message/<str:message_id>/', views.delete_default_message, name='delete_default_message'),

    #editing all default messages at the same time - might take this out
    path('default_messages_management/', views.default_messages_management, name='default_messages_management'),

    path('create_override_message/<str:message_id>/', views.create_override_message, name='create_override_message'),
    path('edit_override_message/<str:message_id>/', views.edit_override_message, name='edit_override_message'),
    path('delete_override_message/<str:message_id>/', views.delete_override_message, name='delete_override_message'),

    path('create_school_message/<str:school_id>/', views.create_school_message, name='create_school_message'),
    path('edit_school_message/<str:message_id>/', views.edit_school_message, name='edit_school_message'),
    path('delete_school_message/<str:message_id>/', views.delete_school_message, name='delete_school_message'),

    path('sendemail/', views.send_email, name='send_email'),
    # path('contact_isei/<str:userID>', views.ContactISEI, name='contactisei'),

    path('get_subject/', views.get_subject, name='get_subject'),
    path('get_message/', views.get_message, name='get_message'),

]