from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.contrib import messages
# from django.db.models import Q


from .decorators import unauthenticated_user, allowed_users

from .models import *
from .forms import *
from .functions import *


# Login / Logout
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
                if request.user.is_active:
                    if request.user.groups.filter(name='isei_admin').exists():
                        return redirect('isei_admin_dashboard')
                    elif request.user.groups.filter(name='school_admin').exists():
                        return redirect('school_admin_dashboard', user.profile.school.id)
                    elif request.user.groups.filter(name='vocational_coordinator').exists():
                        return redirect('school_admin_dashboard', user.profile.school.id)
                    # else:
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


# ISEI Admin Views
@allowed_users(allowed_roles=['isei_admin'])
def isei_admin_dashboard(request):
    context = dict()
    return render(request, 'users/isei_admin_dashboard.html', context)


@allowed_users(allowed_roles=['isei_admin'])
def isei_data_summary(request):
    school = School.objects.all().order_by("name")
    school_admin = User.objects.filter(groups__name='school_admin').order_by("profile__school__name")
    print(school_admin)

    context = dict(school=school, school_admin=school_admin)
    return render(request, 'users/isei_data_summary.html', context)


@allowed_users(allowed_roles=['isei_admin'])
def add_school(request):
    if request.method == 'POST':
        form = SchoolForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('isei_data_summary')
    else:
        form = SchoolForm()

    context = dict(form=form)
    return render(request, 'users/add_school.html', context)


@allowed_users(allowed_roles=['isei_admin'])
def add_school_admin(request):
    school = School.objects.all().order_by("name")
    # register school admin
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            school_abbreviation = request.POST['school_dropdown']
            school = School.objects.get(abbreviation=school_abbreviation)
            group = Group.objects.get(Q(name='school_admin'))
            new_user.groups.add(group)
            phone_number = request.POST['phone_number']
            # address = request.POST ['address']
            Profile.objects.create(user=new_user, phone_number=phone_number, school=school)
            # address=address)

            # email_school_admin(teacher, phone_digits)
            return redirect('isei_data_summary')

    else:
        form = CreateUserForm()

    #ut will be a variable represeting the user type to be added, to allow the usage of the same template
    context = dict(form=form, school=school, ut = "school_admin")
    return render(request, 'users/add_school_admin.html', context)


# School Admin Views
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def school_admin_dashboard(request, schoolid):
    school = School.objects.get(id=schoolid)
    user = User.objects.filter(profile__school=school)
    school_admin = user.filter(groups__name="school_admin")
    vocational_coordinator = user.filter(groups__name="vocational_coordinator")
    instructor = user.filter(groups__name="instructor")
    student = user.filter(groups__name="student")

    context = dict(school=school, school_admin=school_admin,
                   vocational_coordinator=vocational_coordinator,
                   instructor=instructor, student=student)
    return render(request, 'users/school_admin_dashboard.html', context)


# School staff Administration
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def manage_school_staff(request, schoolid):
    school = School.objects.get(id=schoolid)

    staff = get_active_school_staff(school)
    context = dict(school=school, staff=staff, active=True)
    return render(request, 'users/manage_school_staff.html', context)


@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def manage_inactive_school_staff(request, schoolid):
    school = School.objects.get(id=schoolid)

    staff = get_inactive_school_staff(school)
    context = dict(school=school, staff=staff, active=False)
    return render(request, 'users/manage_school_staff.html', context)


@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def add_school_staff(request, schoolid):
    school = School.objects.get(id=schoolid)
    # add new instructor
    if request.method == 'POST':

        if User.objects.filter(username=request.POST.get("username")):
            user = User.objects.get(username=request.POST.get("username"))
            form = CreateUserForm(instance=user)

            # ToDo How to handle a user transfer from one school to the other?
            context = dict(form=form, school=school, existing_user=True,
                           user=User.objects.filter(username=request.POST.get("username")))
            return render(request, 'users/add_school_staff.html', context)

        form = CreateUserForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            phone_number = request.POST.get('phone_number')
            Profile.objects.create(user=new_user, phone_number=phone_number, school=school)
            # address=address)
            if request.POST.get('instructor'):
                group = Group.objects.get(name='instructor')
                new_user.groups.add(group)
            if request.POST.get('vocational_coordinator'):
                group = Group.objects.get(name='vocational_coordinator')
                new_user.groups.add(group)
            if request.POST.get('school_admin'):
                group = Group.objects.get(name='school_admin')
                new_user.groups.add(group)
            # email_staff()
            return redirect('manage_school_staff', school.id)
    else:
        form = CreateUserForm()

    context = dict(form=form, school=school, existing_user=False, ut ="school_staff")
    return render(request, 'users/add_school_staff.html', context)


@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def update_school_staff(request, userid):
    user = User.objects.get(id=userid)
    profile = Profile.objects.get(user=user)
    school = School.objects.get(id=user.profile.school.id)

    if request.method == 'POST':
        form_user = UserForm(request.POST, instance=user)
        form_profile = ProfileForm(request.POST, instance=profile)
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

        if user.is_active:
            return redirect('manage_school_staff', school.id)
        else:
            return redirect('manage_inactive_school_staff', school.id)

    else:
        form_user = UserForm(instance=user)
        form_profile = ProfileForm(instance=profile)

    context = dict(form_user=form_user, user=user,
                   form_profile=form_profile,
                   school=school)

    return render(request, 'users/update_school_staff.html', context)


@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def delete_school_staff(request, userid):
    user = User.objects.get(id=userid)
    profile = Profile.objects.get(user=user)
    school = profile.school

    if request.method == 'POST':
        if user.groups.filter(name="parent"):
            profile.school.delete()
            print('User will remain in the system as a parent')
        else:
            user.delete()
            return redirect('manage_school_staff', school.id)

    context = dict(user=user, school=school)

    return render(request, 'users/delete_school_staff.html', context)


# Student Data Administration
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def manage_students(request, schoolid):
    school = School.objects.get(id=schoolid)

    student = Student.objects.filter(user__profile__school=school, user__is_active=True,
                                     user__groups__name="student").order_by('graduation_year', 'user__last_name')

    context = dict(school=school, student=student, active=True)
    return render(request, 'users/manage_students.html', context)


@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def manage_inactive_students(request, schoolid):
    school = School.objects.get(id=schoolid)

    # staff = get_inactive_student(school)
    context = dict(school=school, active=False)
    return render(request, 'users/manage_students.html', context)


@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def add_student(request, schoolid):
    school = School.objects.get(id=schoolid)
    # add new student
    if request.method == 'POST':
        #print("Post")
        qs = User.objects.filter(username=request.POST.get("username"))
        if qs.exists():
            user = User.objects.get(username=request.POST.get("username"))
            #print(user)
            #print("Existing User")
            form = CreateUserForm(instance=user)
            # ToDo How to handle a user transfer from one school to the other?
            context = dict(form=form, school=school, existing_user=True,
                           user=User.objects.filter(username=request.POST.get("username")))
            return render(request, 'users/add_student.html', context)

        form_user = CreateUserForm(request.POST)
        form_student = StudentForm (request.POST)
        #print("got here")
        if form_user.is_valid() and form_student.is_valid():
            #print("valid forms")
            new_user = form_user.save()
            new_student = form_student.save()
            new_student.user = new_user
            new_student.save()
            group = Group.objects.get(name='student')
            new_user.groups.add(group)
            profile = Profile.objects.create(user=new_user, school=school)
            # email_student()
            return redirect('manage_students', school.id)
    else:
        form_user = CreateUserForm()
        form_student = StudentForm()

    context = dict(form_user=form_user, form_student = form_student,
                   school=school, existing_user = False, ut="student")
    return render(request, 'users/add_student.html', context)


@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def update_student(request, userid):
    user = User.objects.get(id=userid)
    profile = Profile.objects.get(user=user)
    school = School.objects.get(id=user.profile.school.id)

    if request.method == 'POST':
        form_user = UserForm(request.POST, instance=user)
        form_profile = ProfileForm(request.POST, instance=profile)
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

        if user.is_active:
            return redirect('manage_students', school.id)
        else:
            return redirect('manage_inactive_students', school.id)

    else:
        form_user = UserForm(instance=user)
        form_profile = ProfileForm(instance=profile)

    context = dict(form_user=form_user, user=user,
                   form_profile=form_profile,
                   school=school)

    return render(request, 'users/update_student.html', context)


@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def delete_student(request, userid):
    user = User.objects.get(id=userid)
    profile = Profile.objects.get(user=user)
    school = profile.school

    if request.method == 'POST':
        if user.groups.filter(name="parent"):
            profile.school.delete()
            print('User will remain in the system as a parent')
        else:
            user.delete()
            return redirect('manage_students', school.id)

    context = dict(user=user, school=school)

    return render(request, 'users/delete_student.html', context)
