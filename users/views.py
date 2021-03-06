from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.contrib import messages
# from django.http import HttpResponseRedirect
# from django.db.models import Q
from django.forms import modelformset_factory

from .decorators import unauthenticated_user, allowed_users

from .models import *
from .forms import *
from .functions import *
from .filters import *

#landing page for everyone. Introduced it to allow for role transition
def crash(request):
    return render(request, 'users/crash.html')

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
                    if request.user.groups.filter().exists():
                        return redirect('crash')
                    # if request.user.groups.filter(name='isei_admin').exists():
                    #     return redirect('isei_admin_dashboard')
                    # elif request.user.groups.filter(name='school_admin').exists():
                    #     return redirect('school_admin_dashboard', user.profile.school.id)
                    # elif request.user.groups.filter(name='vocational_coordinator').exists():
                    #     return redirect('school_admin_dashboard', user.profile.school.id)
                    else:
                        messages.info(request, 'User not assigned to a group. Please contact the site administrator.')
                else:
                    messages.info(request, 'This account is not currently active. Please contact the site administrator.')
        else:
            messages.info(request, 'Username OR password is incorrect')
    context = dict()
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

    context = dict(form=form, school=school)
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

    context = dict(form=form, school=school)
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
            profile = form_profile.save()

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

        group = Group.objects.get(name='inactive_staff')
        if request.POST.get('inactive_staff'):
            user.groups.add(group)
            if not user.groups.filter(name='parent').exists():
                user.is_active= False
                user.save()
        else:
            user.groups.remove(group)
            user.is_active = True
            user.save()

        if request.user.groups.filter(name="isei_admin"):
            return redirect('isei_data_summary')
        else:
            if request.user.groups.filter(name='inactive_staff').exists():
                return redirect('manage_inactive_school_staff', school.id)
            else:
                return redirect('manage_school_staff', school.id)

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
    if user.groups.filter(name="parent"):
        is_parent = True
    else:
        is_parent = False

    if request.method == 'POST':
        if user.groups.filter(name="parent"):
            group = Group.objects.filter(name__in=['school_admin','instructor','vocational_coordinator'])
            for g in group:
                user.groups.remove(g)
        else:
            user.delete()
        if request.user.groups.filter(name="isei_admin"):
            return redirect('isei_data_summary')
        else:
            return redirect('manage_school_staff', school.id)

    context = dict(user=user, school=school, is_parent=is_parent)
    return render(request, 'users/delete_school_staff.html', context)


# Student Data Administration
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def manage_students(request, schoolid):
    school = School.objects.get(id=schoolid)

    student = Student.objects.filter(user__profile__school=school, user__is_active=True,
                                     user__groups__name="student").order_by('user__last_name')
    student_filter = StudentFilter(request.GET, queryset=student)
    student = student_filter.qs

    context = dict(school=school, student=student, active=True, student_filter = student_filter)
    return render(request, 'users/manage_students.html', context)


@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def manage_inactive_students(request, schoolid):
    school = School.objects.get(id=schoolid)

    student = Student.objects.filter(user__profile__school=school, user__is_active=False,
                                     user__groups__name="student").order_by('graduation_year', 'user__last_name')

    context = dict(school=school, student=student, active=False)
    return render(request, 'users/manage_students.html', context)


@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def mark_inactive_students(request, schoolid):
    school = School.objects.get(id=schoolid)

    student = User.objects.filter(profile__school=school, is_active=True, groups__name="student").order_by('student__graduation_year', 'last_name')
    student_filter = StudentUserFilter(request.GET, queryset=student)
    student = student_filter.qs

    StudentFormset = modelformset_factory(User, fields = ('is_active',), extra=0, can_delete=True)
    student_formset = StudentFormset (queryset=student)

    if request.method=='POST':
        student_formset = StudentFormset(request.POST,)
        if student_formset.is_valid():
            student_formset.save()
            return redirect('manage_students', school.id)


    context = dict(school=school, student=student, student_formset = student_formset, student_filter=student_filter)
    return render(request, 'users/mark_inactive_students.html', context)



@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def add_student(request, schoolid):
    school = School.objects.get(id=schoolid)
    # add new student
    if request.method == 'POST':
        form_user = CreateUserForm(request.POST)
        form_student = StudentForm (request.POST)
        if form_user.is_valid() and form_student.is_valid():
            new_user = form_user.save()
            new_student = form_student.save()
            new_student.user = new_user
            new_student.save()
            group = Group.objects.get(name='student')
            new_user.groups.add(group)
            profile = Profile.objects.create(user=new_user, school=school)
            # email_student()

            if request.POST.get("save_back"):
                return redirect('manage_students', school.id)
            if request.POST.get("save_add_parent"):
                return redirect('add_parent', new_user.id)
            if request.POST.get("save_new"):
                form_user = CreateUserForm()
                form_student = StudentForm()
    else:
        form_user = CreateUserForm()
        form_student = StudentForm()

    context = dict(form_user=form_user, form_student = form_student,
                   school=school)
    return render(request, 'users/add_student.html', context)


@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def update_student(request, userid):
    user = User.objects.get(id=userid)
    #profile = Profile.objects.get(user=user)
    student = Student.objects.get(user=user)
    school = School.objects.get(id=user.profile.school.id)

    if request.method == 'POST':
        form_user = UserFormStudent(request.POST, instance=user)
        form_student = StudentForm(request.POST, instance=student)
        #form_profile = ProfileForm(request.POST, instance=profile)
        if form_user.is_valid() and form_student.is_valid():
            user = form_user.save()
            #form_profile.save()
            form_student.save()
            if user.is_active:
                return redirect('manage_students', school.id)
            else:
                return redirect('manage_inactive_students', school.id)

    else:
        form_user = UserFormStudent(instance=user)
        #form_profile = ProfileForm(instance=profile)
        form_student = StudentForm(instance=student)

    context = dict(form_user=form_user, user=user, form_student =form_student,
                   school=school)

    return render(request, 'users/update_student.html', context)


@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def delete_student(request, userid):
    user = User.objects.get(id=userid)
    profile = Profile.objects.get(user=user)
    #student = Student.objects.get(user=user)
    school = profile.school
    #parent = student.parent

    #TODO should I delete parents along with students?
    # if yes, need to check if the students has other parents, or is a staff at the school
    if request.method == 'POST':
        #g = Group.objects.get(name='parent')
        #for p in parent:
        #    g.user_set.remove(p)
        user.delete()
        return redirect('manage_students', school.id)

    context = dict(user=user, school=school)
    return render(request, 'users/delete_student.html', context)


# Parent Data Administration

@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def add_parent(request, userid):

    student = Student.objects.get(user__id = userid)
    school = School.objects.get(id =student.user.profile.school.id)
    # add new parent
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            group = Group.objects.get(name='parent')
            new_user.groups.add(group)
            student.parent.add(new_user)
            phone_number = request.POST.get('phone_number')
            Profile.objects.create(user=new_user, phone_number=phone_number, school=school)
            # email_student()
            if request.POST.get("save_back"):
                return redirect('manage_students', school.id)
            if request.POST.get("save_new"):
                form = CreateUserForm()
    else:
        form= CreateUserForm()

    context = dict(form=form, school=school, student=student, userid=userid)
    return render(request, 'users/add_parent.html', context)


@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def add_parent_from_list(request, userid, list):

    student = Student.objects.get(user__id = userid)
    school = School.objects.get(id =student.user.profile.school.id)

    if request.method == 'POST':
        parent_id = request.POST.getlist('parent')
        g=Group.objects.get(name='parent')
        for p in parent_id:
            parent= User.objects.get(id=p)
            student.parent.add(parent)
            parent.groups.add(g)

        return redirect('manage_students', school.id)

    else:
        if list == "parent":
            parent_list = User.objects.filter(groups__name="parent", profile__school=school).order_by('last_name')
        elif list=="staff":
            parent_list = User.objects.filter(groups__name__in=["instructor", "vocational_coordinator", "school_admin"], profile__school=school).order_by('last_name').distinct()

    context = dict(school=school, student=student, parent_list= parent_list)
    return render(request, 'users/add_parent_from_list.html', context)



@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def update_parent(request, userid):
    user = User.objects.get(id=userid)
    profile = Profile.objects.get(user=user)
    school = School.objects.get(id=user.profile.school.id)

    if request.method == 'POST':
        form_user = UserForm(request.POST, instance=user)
        form_profile = ProfileForm(request.POST, instance=profile)
        if form_user.is_valid() and form_profile.is_valid():
            user = form_user.save()
            profile = form_profile.save()
            return redirect('manage_students', school.id)
    else:
        form_user = UserForm(instance=user)
        form_profile = ProfileForm(instance=profile)

    context = dict(form_user=form_user, user=user,
                   form_profile=form_profile,
                   school=school,)

    return render(request, 'users/update_parent.html', context)


@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def delete_parent(request, userid, studentid):
    user = User.objects.get(id=userid)
    student = Student.objects.get(id=studentid)
    school = user.profile.school

    if request.method == 'POST':
        if request.POST.get('delete_user'):
            user.delete()
        elif request.POST.get('remove_parent_keep_staff'):
            student.parent.remove(user)
            if has_children(user) == False:
                group = Group.objects.get(name='parent')
                user.groups.remove(group)
        elif request.POST.get('remove_parent'):
            student.parent.remove(user)
            if has_children(user) == False:
                user.delete()

        return redirect('manage_students', school.id)

    context = dict(user=user, school=school, student=student)
    return render(request, 'users/delete_parent.html', context)
