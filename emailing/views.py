from django.shortcuts import render, redirect
from users.models import User
from .forms import *
from .filters import *
from django.core import mail
from django.contrib.auth.decorators import login_required
from users.decorators import allowed_users
from smtplib import SMTPException
from .functions import send_email_school


#system messages views

#ToDo Evaluate if you want to keep the view below
#edit all system messages at the same time
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin'])
def system_messages_management(request):

    system_messages = SystemMessage.objects.all()
    if request.method=="POST":
        formset = SystemMessageFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('message_list')
    else:
        formset = SystemMessageFormSet(queryset=system_messages)

    context = dict(formset=formset)
    return render(request, 'system_messages_management.html', context)

#lists all system messages, link to open Edit, link to add
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'school_admin'])
def message_list(request, school_id=None):
    school = School.objects.filter(id=school_id).first()

    if school and (school.name != "ISEI"):
        system_messages = SystemMessage.objects.filter(overridden=None).order_by('name')
        customized_system_messages = CustomizedSystemMessage.objects.filter(school_id=school_id).order_by('name')
        local_messages = LocalMessage.objects.filter(school_id=school_id).order_by('name')
    else:
        system_messages = SystemMessage.objects.all().order_by('name')
        customized_system_messages = CustomizedSystemMessage.objects.all().order_by('name')
        local_messages = LocalMessage.objects.all().order_by('name')


    context = dict(system_messages=system_messages, customized_system_messages=customized_system_messages,
                   local_messages = local_messages)
    return render(request, 'message_list.html', context)

#create system message with given link
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'school_admin'])
def create_system_message(request):

    if request.method=="POST":
        form = SystemMessageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('message_list')
    else:
        form = SystemMessageForm()

    context = dict(form=form)
    return render(request, 'edit_system_message.html', context)

#edit the system message with given link
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'school_admin'])
def edit_system_message(request, message_id):
    message = SystemMessage.objects.get(id=message_id)
    if request.method=="POST":
        form = SystemMessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            return redirect('message_list')
    else:
        form = SystemMessageForm(instance=message)

    context = dict(form=form)
    return render(request, 'edit_system_message.html', context)



@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'school_admin'])
def delete_system_message(request, message_id):
    message = SystemMessage.objects.get(id=message_id)

    if request.method == 'POST':
        message.delete()
        return redirect('message_list')

    context = dict(message=message)
    return render(request, 'delete_system_message.html', context)

#customized_system message
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'school_admin'])
def create_customized_system_message(request, message_id):
    message = SystemMessage.objects.get(id=message_id)
    school = School.objects.get(id=request.user.profile.school_id)
    customized_system_message = CustomizedSystemMessage(name=message, school=school)

    if request.method=="POST" and 'save' in request.POST:
        form = CustomizedSystemMessageForm(request.POST, instance = customized_system_message)
        if form.is_valid():
            form.save()
            return redirect('message_list', school.id)
        else:
            print("not valid")
    else:
        form = CustomizedSystemMessageForm(instance=customized_system_message)

    context = dict(form=form)
    return render(request, 'create_customized_system_message.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'school_admin'])
def edit_customized_system_message(request, message_id):
    message = CustomizedSystemMessage.objects.get(id=message_id)
    if request.method == "POST":
        form = CustomizedSystemMessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            return redirect('message_list', message.school.id)
    else:
        form = CustomizedSystemMessageForm(instance=message)
    context = dict(form=form)
    return render(request, 'edit_customized_system_message.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'school_admin'])
def delete_customized_system_message(request, message_id):
    message = CustomizedSystemMessage.objects.get(id=message_id)
    school_id=message.school.id
    if request.method == 'POST':
        message.delete()
        return redirect('message_list', school_id)
    context = dict(message=message)
    return render(request, 'delete_customized_system_message.html', context)

#customized_system system message
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'school_admin'])
def create_local_message(request, school_id):

    school = School.objects.get(id=school_id)
    local_message = LocalMessage(school=school)

    if request.method=="POST" and 'save' in request.POST:
        form = LocalMessageForm(request.POST, instance = local_message)
        if form.is_valid():
            form.save()
            return redirect('message_list', school.id)
        else:
            print("not valid")
    else:
        form = LocalMessageForm(instance=local_message)

    context = dict(form=form)
    return render(request, 'create_local_message.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'school_admin'])
def edit_local_message(request, message_id):
    message = LocalMessage.objects.get(id=message_id)
    if request.method == "POST":
        form = LocalMessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            return redirect('message_list', message.school.id)
    else:
        form = LocalMessageForm(instance=message)
    context = dict(form=form)
    return render(request, 'edit_local_message.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'school_admin'])
def delete_local_message(request, message_id):
    message = LocalMessage.objects.get(id=message_id)
    school_id = message.school.id
    if request.method == 'POST':
        message.delete()
        return redirect('message_list', school_id)
    context = dict(message=message)
    return render(request, 'delete_local_message.html', context)


def get_subject(request):
    message_id = request.GET.get('message_id')
    try:
        subject = LocalMessage.objects.get(id=message_id).subject
    except:
        subject=SystemMessage.objects.get(id=message_id).subject
    return render(request, 'get_subject.html', {'subject': subject})


def get_message(request):
    message_id = request.GET.get('message_id')
    try:
        message = LocalMessage.objects.get(id=message_id).message
    except:
        message = SystemMessage.objects.get(id=message_id).message
    return render(request, 'get_message.html', {'message': message})


#sends an email using a form on a website filtering options for email addresses
@login_required(login_url='login')
@allowed_users(allowed_roles=['school_admin', 'vocational_coordinator', 'instructor', 'isei_admin'])
def send_email(request):
    school = request.user.profile.school
    form_used = EmailForm

    if school.name == "ISEI":
        users = User.objects.filter(is_active = True)
    else:
        users = User.objects.filter(is_active = True, profile__school=school)

    #filter
    user_filter =UserFilter(request.GET, queryset=users)
    users = user_filter.qs

    user_emails = users.values_list('email', flat=True)

    if request.method == "GET":
        form = form_used

        message_names = LocalMessage.objects.filter(school=school)
        if not message_names:
            message_names = SystemMessage.objects.all()

        return render(request, 'sendemail.html',
                      {'email_form': form, 'user_emails':user_emails,
                       'user_filter': user_filter, 'users': users,
                       'message_names': message_names,
                       })

    if request.method == "POST":
        form = form_used(request.POST, request.FILES)
        selected_users = request.POST.getlist('user_selection')
        users = User.objects.filter(id__in=selected_users)


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

                return render(request, 'email_success_message.html',
                              {'users':users})
            except SMTPException as e:
                return render(request, 'sendemail.html',
                              {'email_form': form, 'error_message': 'Unable to send email. Please contact the website administrator. \n' + e})

        return render(request, 'sendemail.html',
                      {'email_form': form,
                       'error_message': 'Attachment too big or corrupt', })
