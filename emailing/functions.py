from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from smtplib import SMTPException
from django.contrib import messages
from django.utils.safestring import mark_safe


def send_email_school(request, subject, message, send_to, school):
    #message = message+school.signature
    password= school.email_password[::-1]
    try:
        send_mail(subject, message, school.email_address, send_to, fail_silently=False, auth_user=school.email_address, auth_password=password,
              connection=None, html_message=None)
        messages.info(request, "Email(s) sent successfully")
    except SMTPException as e:
        messages.error(request, mark_safe('Email was not sent. Contact your school administrator. <br>' +  str(e)))



# def send_email(subject, message, send_to):
#     message = message
#     mail = EmailMessage(subject, message, settings.EMAIL_HOST_USER, send_to, cc=["teacher_certification@iseiea.org"])
#     mail.send()