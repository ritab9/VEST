from django.urls import path

from . import views

urlpatterns = [

    path('message_list/', views.message_list, name='message_list'),
    path('message_list/<str:school_id>/', views.message_list, name='message_list'),

    path('create_system_message/', views.create_system_message, name='create_system_message'),
    path('edit_system_message/<str:message_id>/', views.edit_system_message, name='edit_system_message'),
    path('delete_system_message/<str:message_id>/', views.delete_system_message, name='delete_system_message'),

    #editing all system messages at the same time - might take this out
    path('system_messages_management/', views.system_messages_management, name='system_messages_management'),

    path('create_customized_system_message/<str:message_id>/', views.create_customized_system_message, name='create_customized_system_message'),
    path('edit_customized_system_message/<str:message_id>/', views.edit_customized_system_message, name='edit_customized_system_message'),
    path('delete_customized_system_message/<str:message_id>/', views.delete_customized_system_message, name='delete_customized_system_message'),

    path('create_local_message/<str:school_id>/', views.create_local_message, name='create_local_message'),
    path('edit_local_message/<str:message_id>/', views.edit_local_message, name='edit_local_message'),
    path('delete_local_message/<str:message_id>/', views.delete_local_message, name='delete_local_message'),

    path('sendemail/', views.send_email, name='send_email'),
    # path('contact_isei/<str:userID>', views.ContactISEI, name='contactisei'),

    path('get_subject/', views.get_subject, name='get_subject'),
    path('get_message/', views.get_message, name='get_message'),

]