from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from smtplib import SMTPException
from django.contrib import messages
from django.utils.safestring import mark_safe
from .models import *


# contains dynamic information that can be used in email messages
# if his is changed make sure to chang the dynamic_email_content template
def format_message(message, user, child=None):
    return message.format(first_name=user.first_name, last_name=user.last_name,
                          username=user.username.rsplit('_', 1)[-1],
                          link='http://127.0.0.1:8000', child=child)

#ISEI sends email to School admin on account creation
def send_email_school_admin(request, user):
    try:
        subject = DefaultMessage.objects.filter(name="NewStaff").values_list("subject", flat=True).first()
        message = str(DefaultMessage.objects.filter(name="NewStaff").values_list("message", flat=True).first())
        formatted_message = format_message(message, user)
        mail = EmailMessage(subject, formatted_message, settings.EMAIL_HOST_USER, [user.email], cc=["vest@iseiea.org"])
        mail.send()
        messages.info(request, "Email(s) sent successfully to " + str(user.email))
    except SMTPException as e:
        messages.error(request, mark_safe('Email was not sent to ' + str(user.email) + '. <br>' + str(e)))


#school sends email to new users: staff, student, parent
def send_default_email_from_school(request, user, school, message_name, child=None):

    try:
        override = OverrideMessage.objects.filter(name__name=message_name, school=school).first()
        if override:
            subject = override.subject
            message = override.message
        else:
            subject = DefaultMessage.objects.filter(name=message_name).values_list("subject", flat=True).first()
            message = str(DefaultMessage.objects.filter(name=message_name).values_list("message", flat=True).first())
        formatted_message = format_message(message, user, child)
        send_mail(subject, formatted_message, school.email_address, [user.email], fail_silently=False,
                  auth_user=school.email_address,
                  auth_password=school.email_password[::-1], connection=None, html_message=None)
        #messages.info(request, "Email(s) sent successfully to " + str(user.email))
    except SMTPException as e:
        print('Email was not sent to ' + str(user.email) + '. <br>' + str(e))
        #messages.error(request, mark_safe('Email was not sent to ' + str(user.email) + '. <br>' + str(e)))



#Todo not used yet
def send_email_school(request, subject, message, user, school):
    # message = message+school.signature
    password = school.email_password[::-1]
    formatted_message = format_message(message, user)
    try:
        send_mail(subject, formatted_message, school.email_address, [user.email], fail_silently=False, auth_user=school.email_address,
                  auth_password=password,
                  connection=None, html_message=None)
        #messages.info(request, "Email(s) sent successfully")
    except SMTPException as e:
        print('Email was not sent to ' + str(user.email) + '. <br>' + str(e))
        #messages.error(request, mark_safe('Email was not sent. Contact your school administrator. <br>' + str(e)))

#TODO not used yet
def send_email_isei(request, subject, message, send_to):
    try:
        mail = EmailMessage(subject, message, settings.EMAIL_HOST_USER, send_to, cc=["vest@iseiea.org"])
        mail.send()
        messages.info(request, "Email(s) sent successfully to " + str(send_to))
    except SMTPException as e:
        messages.error(request, mark_safe('Email was not sent to ' + str(send_to) + '. <br>' + str(e)))
