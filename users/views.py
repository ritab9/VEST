from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.contrib import messages


from .decorators import unauthenticated_user, allowed_users

from .models import *
from .forms import *



# Create your views here.
@unauthenticated_user
def loginuser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            else:
                if request.user.is_active == True:
                    if request.user.groups.filter(name='isei_admin').exists():
                        return redirect('isei_admin_dashboard')
                    elif request.user.groups.filter(name='school_admin').exists():
                        return redirect('school_admin_dashboard', user.profile.school.id)
                    elif request.user.groups.filter(name='vocational_coordinator').exists():
                         return redirect('school_admin_dashboard', user.profile.school.id)
                    #else:
                    messages.info(request, 'User not assigned to a group. Please contact the site administrator.')
                else:
                    messages.info(request, 'This account is not currently active. Please contact ISEI.')
        else:
            messages.info(request, 'Username OR password is incorrect')
    context = {}
    return render(request, 'users/login.html', context)


def logoutuser(request):
    logout(request)
    return redirect('login')


#ISEI Admin Views
@allowed_users(allowed_roles=['isei_admin'])
def isei_admin_dashboard(request):

    context = dict()
    return render(request,'users/isei_admin_dashboard.html', context)

@allowed_users(allowed_roles=['isei_admin'])
def isei_data_summary(request):

    school = School.objects.all().order_by("name")
    school_admin = SchoolAdmin.objects.all().order_by("school__name")

    context = dict(school=school, school_admin=school_admin)
    return render(request,'users/isei_data_summary.html', context)

@allowed_users(allowed_roles=['isei_admin'])
def add_school(request):
    if request.method == 'POST':
        form = SchoolForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('isei_data_summary')
    else:
        form = SchoolForm()

    context = dict(form = form)
    return render(request,'users/add_school.html', context)

@allowed_users(allowed_roles=['isei_admin'])
def add_school_admin(request):

    school = School.objects.all().order_by("name")
#register school admin
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            school_id = request.POST['school_dropdown']
            school= School.objects.get(id=school_id)
            group = Group.objects.get(name='school_admin')
            new_user.groups.add(group)
            school_admin = SchoolAdmin.objects.create(user=new_user,)
            username = form.cleaned_data.get('username')
            phone_number = request.POST['phone_number']
            # address = request.POST ['address']
            profile = Profile.objects.create(user=new_user, phone_number=phone_number, school=school)
            #address=address)
            # flash message (only appears once)
            #messages.success(request, 'Account was created for ' + username)

            #email_school_admin(teacher, phone_digits)
            return redirect('isei_data_summary')


    else:
        form = CreateUserForm()

    context = dict(form = form, school=school)
    return render(request,'users/add_school_admin.html', context)


# School Admin Views
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def school_admin_dashboard(request, schoolID):

    #user=User.objects.get(id=userID)
    #school = user.schooladmin.school
    school=School.objects.get(id=schoolID)
    school_admin = SchoolAdmin.objects.filter(school=school)
    vocational_coordinator = VocationalCoordinator.objects.filter(user__profile__school = school)
    instructor = Instructor.objects.filter(user__profile__school=school)
    student = Student.objects.filter(user__profile__school=school)

    context = dict(school=school, school_admin=school_admin,
                   vocational_coordinator=vocational_coordinator,
                   instructor=instructor, student = student)
    return render(request,'users/school_admin_dashboard.html', context)


@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def manage_school_staff(request, schoolID):

    school=School.objects.get(id=schoolID)

    staff = User.objects.filter(profile__school=school).order_by('-is_active', 'last_name')
    school_admin=SchoolAdmin.objects.filter(user__profile__school=school)
    vocational_coordinator = VocationalCoordinator.objects.filter(user__profile__school=school)
    instructor = Instructor.objects.filter(user__profile__school=school).order_by('-user__is_active')

    context = dict(school=school, school_admin=school_admin, staff = staff,
                   vocational_coordinator=vocational_coordinator, instructor=instructor)
    return render(request, 'users/manage_school_staff.html', context)


@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def manage_students(request, schoolID):

    school=School.objects.get(id=schoolID)
    school_admin = SchoolAdmin.objects.filter(school=school)
    vocational_coordinator = VocationalCoordinator.objects.filter(school=school)
    instructor = Instructor.objects.filter(school=school)
    student = Student.objects.filter(school=school)

    context = dict(school=school, school_admin=school_admin,
                   vocational_coordinator=vocational_coordinator,
                   instructor=instructor, student = student)
    return render(request,'users/school_admin_dashboard.html', context)


@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def add_school_staff(request, schoolID):

    school = School.objects.get(id=schoolID)
#add new instructor
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            # username = form.cleaned_data.get('username')
            phone_number = request.POST.get('phone_number')
            # address = request.POST ['address']
            profile = Profile.objects.create(user=new_user, phone_number=phone_number, school=school)
            # address=address)
            if request.POST.get('instructor'):
                group = Group.objects.get(name='instructor')
                new_user.groups.add(group)
                instructor = Instructor.objects.create(user=new_user, school=school)
            if request.POST.get('vocational_coordinator'):
                group = Group.objects.get(name='vocational_coordinator')
                new_user.groups.add(group)
                vocational_coordiantor = VocationalCoordinator.objects.create(user=new_user, school=school)
            if request.POST.get('school_admin'):
                group = Group.objects.get(name='school_admin')
                new_user.groups.add(group)
                school_admin = SchoolAdmin.objects.create(user=new_user, school=school)

            # flash message (only appears once)
            #messages.success(request, 'Account was created for ' + username)

            #email_staff()
            return redirect('manage_school_staff', school.id)
    else:
        form = CreateUserForm()

    context = dict(form = form, school=school)
    return render(request, 'users/add_school_staff.html', context)


@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def update_school_staff(request, userID):

    user = User.objects.get(id=userID)
    profile = Profile.objects.get(user=user)
    school = School.objects.get(id=user.instructor.school.id)

    if request.method == 'POST':
        form_user = UserForm(request.POST, instance=user)
        form_profile = ProfileForm(request.POST, instance = profile)
        if form_user.is_valid() and form_profile.is_valid():
            user = form_user.save()
            form_profile.save()

        group = Group.objects.get(name='instructor')
        if request.POST.get('instructor'):
            user.groups.add(group)
        else:
            user.groups.remove(group)

        group = Group.objects.get(name='vocational_coordinator')
        if request.POST.get('vocational_coordinator'):
            user.groups.add(group)
        else:
            user.groups.remove(group)

        group = Group.objects.get(name='school_admin')
        if request.POST.get('school_admin'):
            user.groups.add(group)
        else:
            user.groups.remove(group)
        return redirect('manage_school_staff', school.id)

    else:
        form_user = UserForm(instance=user)
        form_profile = ProfileForm (instance = profile)

    context = dict(form_user = form_user, user=user,
                   form_profile = form_profile,
                   school=school)

    return render(request, 'users/update_school_staff.html', context)


@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def delete_school_staff(request, userID):

    user = User.objects.get(id=userID)
    profile = Profile.objects.get(user=user)
    school = School.objects.get(id=user.instructor.school.id)

    if request.method == 'POST':
        form_user = UserForm(request.POST)
        form_profile = ProfileForm(request.POST)
        if form_user.is_valid() and form_profile.is_valid():
            user = form_user.save()
            profile = form_profile.save()
            return redirect('manage_school_staff', school.id)
    else:
        form_user = UserForm(instance=user)
        form_profile = ProfileForm (instance = profile)

    context = dict(form_user = form_user,
                   form_profile = form_profile,
                   school=school)

    return render(request,'users/delete_school_staff.html', context)
