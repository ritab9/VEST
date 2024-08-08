from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from smtplib import SMTPException
from django.contrib import messages
from django.utils.safestring import mark_safe
from .models import *


# contains dynamic information that can be used in email messages
# if his is changed make sure to chang the dynamic_email_content template
def format_message(message, user, child=None, extra_message=None):
    return message.format(first_name=user.first_name, last_name=user.last_name,
                          username=user.username.rsplit('_', 1)[-1],
                          link='iseivest.org', child=child, extra_message=extra_message)

#ISEI sends email to School admin on account creation
def send_email_school_admin(request, user):
    try:
        subject = SystemMessage.objects.filter(name="NewStaff").values_list("subject", flat=True).first()
        message = str(SystemMessage.objects.filter(name="NewStaff").values_list("message", flat=True).first())
        formatted_message = format_message(message, user)
        mail = EmailMessage(subject, formatted_message, settings.EMAIL_HOST_USER, [user.email], cc=["vest@iseiea.org"])
        mail.send()
        messages.info(request, "Email(s) sent successfully to " + str(user.email))
    except SMTPException as e:
        messages.error(request, mark_safe('Email was not sent to ' + str(user.email) + '. <br>' + str(e)))


#school sends email to new users: staff, student, parent
def send_system_email_from_school(request, user, school, message_name, child=None, extra_message=None):

    try:
        customize = CustomizedSystemMessage.objects.filter(name__name=message_name, school=school).first()
        if customize:
            subject = customize.subject
            message = customize.message
        else:
            subject = SystemMessage.objects.filter(name=message_name).values_list("subject", flat=True).first()
            message = str(SystemMessage.objects.filter(name=message_name).values_list("message", flat=True).first())
        formatted_message = format_message(message, user, child, extra_message)
        send_mail(subject, formatted_message, school.email_address, [user.email], fail_silently=False,
                  auth_user=school.email_address,
                  auth_password=school.email_password[::-1], connection=None, html_message=None)
        messages.info(request, "Email(s) sent successfully to " + str(user.email))
    except SMTPException as e:
        messages.error(request, mark_safe('Email was not sent to ' + str(user.email) + '. <br>' + str(e)))



def send_email_school(request, subject, message, user=None, school=None):
    # message = message+school.signature
    password = school.email_password[::-1]
    if user is None:
        email = school.email_address
        formatted_message=message
    else:
        email=user.email
        formatted_message = format_message(message, user)

    try:
        send_mail(subject, formatted_message, school.email_address, [email], fail_silently=False, auth_user=school.email_address,
                  auth_password=password,
                  connection=None, html_message=None)
        messages.info(request, "Email(s) sent successfully")
    except SMTPException as e:
        return False
        messages.error(request, mark_safe('Email was not sent. Contact your school administrator. <br>' + str(e)))

#TODO not used yet
def send_email_isei(request, subject, message, send_to):
    try:
        mail = EmailMessage(subject, message, settings.EMAIL_HOST_USER, send_to, cc=["vest@iseiea.org"])
        mail.send()
        messages.info(request, "Email(s) sent successfully to " + str(send_to))
    except SMTPException as e:
        messages.error(request, mark_safe('Email was not sent to ' + str(send_to) + '. <br>' + str(e)))
