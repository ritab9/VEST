from django.shortcuts import render
from users.models import User
from .forms import EmailForm
from .filters import *
from django.core import mail
from django.contrib.auth.decorators import login_required
from users.decorators import allowed_users
from smtplib import SMTPException
from .functions import send_email_school


# Create your views here.

#view that sends an email using a form on a website filtering options for email addresses
@login_required(login_url='login')
@allowed_users(allowed_roles=['school_admin', 'vocational_coordinator', 'instructor'])
def send_email(request):
    school = request.user.profile.school

    form_used = EmailForm
    users = User.objects.filter(is_active = True)

    #filter
    user_filter =UserFilter(request.GET, queryset=users)
    users = user_filter.qs

    user_emails = users.values_list('email', flat=True)

    if request.method == "GET":
        form = form_used
        return render(request, 'sendemail.html',
                      {'email_form': form, 'user_emails':user_emails,
                       'user_filter': user_filter})

    if request.method == "POST":
        form = form_used(request.POST, request.FILES)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            files = request.FILES.getlist('attach')
            try:
                #connection = mail.get_connection()
                #connection.open()
                password = school.email_password[::-1]
                for user_email in user_emails:
                    send_email_school(request, subject, message, [user_email,], school)
                    #email = mail.EmailMessage(subject, message, school.email_address , [e], connection=connection, auth_user=school.email_address, auth_password=password,)
                    #for f in files:
                        #email.attach(f.name, f.read(), f.content_type)
                    #email.send()
                #connection.close()

                return render(request, 'sendemail.html',
                              {'error_message': 'Sent email to %s' %list(user_emails)})
            except SMTPException as e:
                return render(request, 'sendemail.html',
                              {'email_form': form, 'error_message': 'Unable to send email. Please contact the website administrator. \n' + e})

        return render(request, 'sendemail.html',
                      {'email_form': form,
                       'error_message': 'Attachment too big or corrupt', })
