from django.urls import path

from . import views

urlpatterns = [

    #path('contact_isei/<str:userID>', views.ContactISEI, name='contactisei'),
    path('sendemail/', views.send_email, name='send_email'),
]