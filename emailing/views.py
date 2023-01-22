from django.shortcuts import render, redirect
from users.models import User
from .forms import *
from .filters import *
from django.core import mail
from django.contrib.auth.decorators import login_required
from users.decorators import allowed_users
from smtplib import SMTPException
from .functions import send_email_school


#default messages views

#ToDo Evaluate if you want to keep the view below
#edit all default messages at the same time
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin'])
def default_messages_management(request):

    messages = DefaultMessage.objects.all()
    if request.method=="POST":
        formset = DefaultMessageFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('message_list')
    else:
        formset = DefaultMessageFormSet(queryset=messages)

    context = dict(formset=formset)
    return render(request, 'default_messages_management.html', context)

#lists all default messages, link to open Edit, link to add
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'school_admin'])
def message_list(request, school_id=None):

    if school_id:
        default_messages = DefaultMessage.objects.filter(overridden=None).order_by('name')
        override_messages = OverrideMessage.objects.filter(school_id=school_id).order_by('name')
        school_messages = SchoolMessage.objects.filter(school_id=school_id).order_by('name')
    else:
        default_messages = DefaultMessage.objects.all().order_by('name')
        override_messages = OverrideMessage.objects.all().order_by('name')
        school_messages = SchoolMessage.objects.all().order_by('name')

    context = dict(default_messages=default_messages, override_messages=override_messages,
                   school_messages = school_messages)
    return render(request, 'message_list.html', context)

#create default message with given link
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'school_admin'])
def create_default_message(request):

    if request.method=="POST":
        form = DefaultMessageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('message_list')
    else:
        form = DefaultMessageForm()

    context = dict(form=form)
    return render(request, 'edit_default_message.html', context)

#edit the default message with given link
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'school_admin'])
def edit_default_message(request, message_id):
    message = DefaultMessage.objects.get(id=message_id)
    if request.method=="POST":
        form = DefaultMessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            return redirect('message_list')
    else:
        form = DefaultMessageForm(instance=message)

    context = dict(form=form)
    return render(request, 'edit_default_message.html', context)



@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'school_admin'])
def delete_default_message(request, message_id):
    message = DefaultMessage.objects.get(id=message_id)

    if request.method == 'POST':
        message.delete()
        return redirect('message_list')

    context = dict(message=message)
    return render(request, 'delete_default_message.html', context)

#override default message
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'school_admin'])
def create_override_message(request, message_id):
    message = DefaultMessage.objects.get(id=message_id)
    school = School.objects.get(id=request.user.profile.school_id)
    override_message = OverrideMessage(name=message, school=school)

    if request.method=="POST" and 'save' in request.POST:
        form = OverrideMessageForm(request.POST, instance = override_message)
        if form.is_valid():
            form.save()
            return redirect('message_list', school.id)
        else:
            print("not valid")
    else:
        form = OverrideMessageForm(instance=override_message)

    context = dict(form=form)
    return render(request, 'create_override_message.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'school_admin'])
def edit_override_message(request, message_id):
    message = OverrideMessage.objects.get(id=message_id)
    if request.method == "POST":
        form = OverrideMessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            return redirect('message_list', message.school.id)
    else:
        form = OverrideMessageForm(instance=message)
    context = dict(form=form)
    return render(request, 'edit_override_message.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'school_admin'])
def delete_override_message(request, message_id):
    message = OverrideMessage.objects.get(id=message_id)
    school_id=message.school.id
    if request.method == 'POST':
        message.delete()
        return redirect('message_list', school_id)
    context = dict(message=message)
    return render(request, 'delete_override_message.html', context)

#override default message
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'school_admin'])
def create_school_message(request, school_id):

    school = School.objects.get(id=school_id)
    school_message = SchoolMessage(school=school)

    if request.method=="POST" and 'save' in request.POST:
        form = SchoolMessageForm(request.POST, instance = school_message)
        if form.is_valid():
            form.save()
            return redirect('message_list', school.id)
        else:
            print("not valid")
    else:
        form = SchoolMessageForm(instance=school_message)

    context = dict(form=form)
    return render(request, 'create_school_message.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'school_admin'])
def edit_school_message(request, message_id):
    message = SchoolMessage.objects.get(id=message_id)
    if request.method == "POST":
        form = SchoolMessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            return redirect('message_list', message.school.id)
    else:
        form = SchoolMessageForm(instance=message)
    context = dict(form=form)
    return render(request, 'edit_school_message.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'school_admin'])
def delete_school_message(request, message_id):
    message = SchoolMessage.objects.get(id=message_id)
    school_id = message.school.id
    if request.method == 'POST':
        message.delete()
        return redirect('message_list', school_id)
    context = dict(message=message)
    return render(request, 'delete_school_message.html', context)


def get_subject(request):
    message_id = request.GET.get('message_id')
    subject = SchoolMessage.objects.get(id=message_id).subject
    return render(request, 'get_subject.html', {'subject': subject})


def get_message(request):
    message_id = request.GET.get('message_id')
    message = SchoolMessage.objects.get(id=message_id).message
    return render(request, 'get_message.html', {'message': message})


#sends an email using a form on a website filtering options for email addresses
@login_required(login_url='login')
@allowed_users(allowed_roles=['school_admin', 'vocational_coordinator', 'instructor', 'isei_admin'])
def send_email(request):
    school = request.user.profile.school
    form_used = EmailForm

    if school == "ISEI":
        users = User.objects.filter(is_active = True)
    else:
        users = User.objects.filter(is_active = True, profile__school=school)

    #filter
    user_filter =UserFilter(request.GET, queryset=users)
    users = user_filter.qs

    user_emails = users.values_list('email', flat=True)

    if request.method == "GET":
        form = form_used
        message_names = SchoolMessage.objects.filter(school=school)
        return render(request, 'sendemail.html',
                      {'email_form': form, 'user_emails':user_emails,
                       'user_filter': user_filter, 'users': users,
                       'message_names': message_names,
                       })

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
                for user in users:
                    send_email_school(request, subject, message, user, school)
                    #email = mail.EmailMessage(subject, message, school.email_address , [e], connection=connection, auth_user=school.email_address, auth_password=password,)
                    #for f in files:
                        #email.attach(f.name, f.read(), f.content_type)
                    #email.send()
                #connection.close()

                return render(request, 'sendemail.html',
                              {'error_message': 'Email(s) sent'})
            except SMTPException as e:
                return render(request, 'sendemail.html',
                              {'email_form': form, 'error_message': 'Unable to send email. Please contact the website administrator. \n' + e})

        return render(request, 'sendemail.html',
                      {'email_form': form,
                       'error_message': 'Attachment too big or corrupt', })
