from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse
# from django.db.models import Q
from django.forms import modelformset_factory

from .decorators import unauthenticated_user, allowed_users
from .forms import *
from .functions import *
from .filters import *
import datetime
from vocational.models import SchoolYear, EthicsGradeRecord, \
    InstructorAssignment, StudentAssignment, GradeSettings, \
    Department, Quarter, VocationalStatus, EthicsLevel, VocationalClass
from emailing.functions import *
from emailing.models import *
from vocational.functions import current_quarter
from .models import Country

import pandas as pd
from django.http import HttpResponse
from django.contrib import messages


# landing page for everyone. Introduced it to allow for role transition
@login_required(login_url='login')
def crash(request):
    return render(request, 'users/crash.html')


# Login / Logout
@unauthenticated_user
def loginuser(request):
    if request.method == 'POST':
        code = request.POST.get("country_code")
        if not code:
            messages.info(request, 'Please select school.')
        else:
            username = code + "_" + request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                if request.GET.get('next'):
                    return redirect(request.GET.get('next'))
                else:
                    if request.user.is_active:
                        if request.user.groups.filter(name='isei_admin').exists():
                            return redirect('isei_data_summary')
                            #return redirect('isei_admin_dashboard')
                        elif request.user.groups.filter(name='school_admin').exists():
                            return redirect('school_admin_dashboard', user.profile.school.id)
                        elif request.user.groups.filter(name='vocational_coordinator').exists():
                            return redirect('vocational_coordinator_dashboard', user.profile.school.id)
                        elif request.user.groups.filter(name='instructor').exists():
                            if code == "US_TS":
                                return redirect('time_card_dashboard', user.id)
                            #return redirect('instructor_dashboard', user.id)
                            #return redirect('grade_list', user.id )
                            else:
                                return redirect('initiate_grade_entry', user.profile.school.id )
                        elif request.user.groups.filter(name='parent').exists():
                            return redirect('parent_page', user.id)
                        elif request.user.groups.filter(name='student').exists():
                            return redirect('student_page', user.id)
                        else:
                            messages.info(request, 'User not assigned to a group. Please contact the site administrator.')
                    else:
                        messages.info(request,
                                      'This account is not currently active. Please contact the site administrator.')
            else:
                messages.info(request, 'Username, Password, and School combination is incorrect')

    school = School.objects.all
    context = dict(school = school)
    return render(request, 'users/login.html', context)


def logoutuser(request):
    logout(request)
    return redirect('login')


# ISEI Admin Views
@login_required(login_url='login')
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


@login_required(login_url='login')
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



@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin'])
def add_school_admin(request):
    school = School.objects.all().order_by("name")

    # register school admin
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            school_code = request.POST['school_dropdown']
            new_user.username = school_code + "_" + request.POST["username"]
            new_user.password = "hjbjb3iohroibniion"
            new_user.save()
            school_abbreviation = school_code.rsplit('_', 1)[-1]
            school = School.objects.get(abbreviation = school_abbreviation)
            group = Group.objects.get(Q(name='school_admin'))
            new_user.groups.add(group)
            phone_number = request.POST['phone_number']
            # address = request.POST ['address']
            Profile.objects.create(user=new_user, phone_number=phone_number, school=school)
            # address=address)
            send_email_school_admin(request, new_user)
            return redirect('isei_data_summary')
        else:
            print("form not valid")
    else:
        form = CreateUserForm()

    context = dict(form=form, school=school)
    return render(request, 'users/add_school_admin.html', context)

#instructor coordinator
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'instructor'])
def instructor_dashboard(request, userid):

    #This is leftover from time card things
    profile=Profile.objects.get(user=userid)
    school_id=profile.school.id

    assignments = InstructorAssignment.objects.filter(instructor__id=profile.id)
    department = Department.objects.filter(school__id=school_id, is_active=True, instructorassignment__in=assignments)

    school_year_id = SchoolYear.objects.values_list('id', flat=True).filter(school_id=school_id, active=True).first()
    active_quarter = Quarter.objects.filter(school_year__school_id=school_id, school_year__active=True).order_by('name')

    q = current_quarter(school_year_id)
    if q:
        current_quarter_id = current_quarter(school_year_id).id
    else:
        messages.warning(request,
                         "This school year/quarter is not set up properly for grade entry. \n Please contact school administrator or vocational coordinator. ")
        return redirect('crash')


    context = dict(active_quarter=active_quarter, department=department,
                   current_quarter_id=current_quarter_id)
    return render(request, 'users/instructor_dashboard.html', context)



#vocational coordinator
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator'])
def vocational_coordinator_dashboard(request, schoolid):
    school = School.objects.get(id=schoolid)

    try:
        active_school_year = SchoolYear.objects.get(school=school, active=True)
    except SchoolYear.DoesNotExist:
        active_school_year = None

    # Get all quarters for the active school year
    quarters = Quarter.objects.filter(school_year=active_school_year)

    school_year_update = Quarter.objects.values_list('updated_at', flat=True).filter(school_year__school=school).order_by("-updated_at").first()
    instructor_update = Profile.objects.values_list('updated_at', flat=True).filter(school=school,
                                user__groups__name__in=["instructor", "vocational_coordinator","school_admin", "inactive_staff"]).order_by("-updated_at").first()
    student_update = Student.objects.values_list('updated_at', flat=True).filter(user__profile__school=school,).order_by("-updated_at").first()
    department_update = Department.objects.values_list('updated_at', flat=True).filter(school=school).order_by("-updated_at").first()


    instructor_assignment_update = InstructorAssignment.objects.values_list('updated_at', flat=True).filter(instructor__school=school).order_by(
        "-updated_at").first()
    student_assignment_update = StudentAssignment.objects.values_list('updated_at', flat=True).filter(student__user__profile__school=school).order_by(
        "-updated_at").first()
    grade_settings_update = GradeSettings.objects.values_list('updated_at', flat=True).filter(school_year__school=school).order_by(
        "-updated_at").first()
    customized_system_message_update = CustomizedSystemMessage.objects.values_list('updated_at', flat=True).filter(school=school).order_by(
        "-updated_at").first()
    local_message_update = LocalMessage.objects.values_list('updated_at', flat=True).filter(school=school).order_by(
        "-updated_at").first()
    system_message_update = SystemMessage.objects.values_list('updated_at', flat=True).order_by("-updated_at").first()
    message_update = max(filter(None.__ne__, [customized_system_message_update,local_message_update]), default=None)


    context = dict(school_id=schoolid, school=school, instructor_update = instructor_update, student_update = student_update,
                   department_update = department_update,
                   school_year_update= school_year_update,grade_settings_update = grade_settings_update,
                   instructor_assignment_update = instructor_assignment_update, student_assignment_update = student_assignment_update,
                   message_update=message_update,
                   active_school_year=active_school_year, quarters=quarters,
                   )
    return render(request, 'users/vocational_coordinator_dashboard.html', context)


# School Admin Views
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def school_admin_dashboard(request, schoolid):
    school = School.objects.get(id=schoolid)

    try:
        active_school_year = SchoolYear.objects.get(school=school, active=True)
    except SchoolYear.DoesNotExist:
        active_school_year = None

    # Get all quarters for the active school year
    quarters = Quarter.objects.filter(school_year=active_school_year)

    school_year_update = Quarter.objects.values_list('updated_at', flat=True).filter(school_year__school=school).order_by(
        "-updated_at").first()
    instructor_update = Profile.objects.values_list('updated_at', flat=True).filter(school=school,
        user__groups__name__in=["instructor", "vocational_coordinator", "inactive_staff"]).order_by(
                                "-updated_at").first()
    student_update = Student.objects.values_list('updated_at', flat=True).filter(
        user__profile__school=school, ).order_by("-updated_at").first()
    department_update = Department.objects.values_list('updated_at', flat=True).filter(school=school).order_by(
        "-updated_at").first()

    instructor_assignment_update = InstructorAssignment.objects.values_list('updated_at', flat=True).filter(
        instructor__school=school).order_by("-updated_at").first()
    student_assignment_update = StudentAssignment.objects.values_list('updated_at', flat=True).filter(
        student__user__profile__school=school).order_by("-updated_at").first()
    grade_settings_update = GradeSettings.objects.values_list('updated_at', flat=True).filter(
        school_year__school=school).order_by("-updated_at").first()
    customized_system_message_update = CustomizedSystemMessage.objects.values_list('updated_at', flat=True).filter(
        school=school).order_by("-updated_at").first()
    local_message_update = LocalMessage.objects.values_list('updated_at', flat=True).filter(school=school).order_by(
        "-updated_at").first()
    system_message_update = SystemMessage.objects.values_list('updated_at', flat=True).order_by(
        "-updated_at").first()
    message_update = max(filter(None.__ne__, [customized_system_message_update, local_message_update]), default=None)

    context = dict(school_id=schoolid, school=school, instructor_update=instructor_update,
                   student_update=student_update,
                   department_update=department_update,
                   school_year_update=school_year_update, grade_settings_update=grade_settings_update,
                   instructor_assignment_update=instructor_assignment_update,
                   student_assignment_update=student_assignment_update,
                   message_update=message_update,
                   active_school_year=active_school_year, quarters=quarters,
                   )

    return render(request, 'users/school_admin_dashboard.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def email_settings(request, schoolid):

    school=School.objects.get(id=schoolid)

    if school.email_address and school.email_password:
        set_up=True
    else:
        set_up=False

    if request.method=="POST" and 'save' in request.POST:
        email_settings_form = EmailSettingsForm(request.POST, instance=school)
        if email_settings_form.is_valid():
            es = email_settings_form.save(commit=False)
            password = es.email_password[::-1]
            es.email_password = password
            es.save()
    else:
        email_settings_form = EmailSettingsForm(instance=school)

    if request.method=="POST" and 'send' in request.POST:
        if not send_email_school(request, "Trial Email", "Email service successfully set up for VEST", None, school):
            school.email_update = datetime.datetime.now().date()
            school.save()

    if request.method == "POST" and 'edit' in request.POST:
        set_up=False

    context = dict(email_settings_form = email_settings_form, set_up=set_up, email=school.email_address)
    return render(request, 'users/email_settings.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def school_users(request, schoolid):
    school = School.objects.get(id=schoolid)
    user = User.objects.filter(profile__school=school)
    school_admin = user.filter(groups__name="school_admin")
    vocational_coordinator = user.filter(groups__name="vocational_coordinator")
    instructor = user.filter(groups__name="instructor")
    student = user.filter(groups__name="student")

    context = dict(school=school, school_admin=school_admin,
                   vocational_coordinator=vocational_coordinator,
                   instructor=instructor, student=student)
    return render(request, 'users/school_users.html', context)


# School staff Administration
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def manage_school_staff(request, schoolid):
    school = School.objects.get(id=schoolid)

    staff = get_active_school_staff(school)
    context = dict(school=school, staff=staff, active=True)
    return render(request, 'users/manage_school_staff.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def manage_inactive_school_staff(request, schoolid):
    school = School.objects.get(id=schoolid)

    staff = get_inactive_school_staff(school)
    context = dict(school=school, staff=staff, active=False)
    return render(request, 'users/manage_school_staff.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def add_school_staff(request, schoolid):
    school = School.objects.get(id=schoolid)
    # add new instructor
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.username = str(school.country.code)+"_"+ str(school.abbreviation)+ "_" + request.POST["username"]
            new_user.password = "bduaguigadbuhujb"
            new_user.save()

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
            send_system_email_from_school(request, new_user, school, "NewStaff")
            return redirect('manage_school_staff', school.id)
    else:
        form = CreateUserForm()

    context = dict(form=form, school=school)
    return render(request, 'users/add_school_staff.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def add_staff_from_parent_list(request, schoolid):
    school = School.objects.get(id=schoolid)

    if request.method == 'POST':
        user_id = request.POST.get('parent')
        return redirect('update_school_staff', user_id)
    else:
        parent_list_including_staff_parents = User.objects.filter( Q(profile__school=school), Q(groups__name="parent"),).order_by('last_name')
        parent_list = parent_list_including_staff_parents.filter(~Q(groups__name="instructor"),~Q(groups__name="vocational_coordiantor"), ~Q(groups__name="school_admin"),)

    context = dict(school=school, parent_list=parent_list)
    return render(request, 'users/add_staff_from_parent_list.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def update_school_staff(request, userid):
    user = User.objects.get(id=userid)
    profile = Profile.objects.get(user=user)
    school = School.objects.get(id=user.profile.school.id)
    data_exists = user.ethicsgraderecord_set.all().exists()

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

        group = Group.objects.get(name='inactive_staff')
        if request.POST.get('inactive_staff'):
            user.groups.add(group)
            if not user.groups.filter(name='parent').exists():
                user.is_active = False
                user.save()
        else:
            user.groups.remove(group)
            user.is_active = True
            user.save()

        if request.user.groups.filter(name="isei_admin").exists():
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
                   school=school, data_exists = data_exists)

    return render(request, 'users/update_school_staff.html', context)


@login_required(login_url='login')
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
            group = Group.objects.filter(name__in=['school_admin', 'instructor', 'vocational_coordinator'])
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
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def manage_students(request, schoolid):
    school = School.objects.get(id=schoolid)

    student = Student.objects.filter(user__profile__school=school, user__is_active=True,
                                     user__groups__name="student").order_by('-graduation_year','user__last_name')
    student_filter = StudentFilter(request.GET, queryset=student)
    student = student_filter.qs

    context = dict(school=school, student=student, active=True, student_filter=student_filter)
    return render(request, 'users/manage_students.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def manage_inactive_students(request, schoolid):
    school = School.objects.get(id=schoolid)

    student = Student.objects.filter(user__profile__school=school, user__is_active=False,
                                     user__groups__name="student").order_by('graduation_year', 'user__last_name')
    student_filter = StudentFilter(request.GET, queryset=student)
    student = student_filter.qs

    context = dict(school=school, student=student, active=False, student_filter=student_filter)
    return render(request, 'users/manage_students.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def mark_inactive_students(request, schoolid):
    school = School.objects.get(id=schoolid)

    student = User.objects.filter(profile__school=school, is_active=True, groups__name="student").order_by(
        'student__graduation_year', 'last_name')
    student_filter = StudentUserFilter(request.GET, queryset=student)
    student = student_filter.qs

    studentformset = modelformset_factory(User, fields=('is_active',), extra=0, can_delete=True)
    student_formset = studentformset(queryset=student)

    if request.method == 'POST':
        student_formset = studentformset(request.POST, )
        if student_formset.is_valid():
            student_formset.save()
            return redirect('manage_students', school.id)

    grads_only = False

    context = dict(school=school, grads_only=grads_only, student=student, student_formset=student_formset,
                   student_filter=student_filter)
    return render(request, 'users/mark_inactive_students.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def graduate_students(request, schoolid):
    school = School.objects.get(id=schoolid)
    school_year = SchoolYear.objects.get(school=school, active=True)

    all_student = User.objects.filter(profile__school=school, is_active=True, groups__name="student").order_by(
        'student__graduation_year', 'last_name')

    student = all_student.filter(student__graduation_year__lte=datetime.date.today().year)
    for s in student:
        s.is_active = False
        s.save()

    studentformset = modelformset_factory(User, fields=('is_active',), extra=0, can_delete=True)
    student_formset = studentformset(queryset=student)

    if request.method == 'POST':
        student_formset = studentformset(request.POST, )
        if student_formset.is_valid():
            student_formset.save()
            return redirect('manage_students', school.id)

    grads_only = True

    context = dict(school=school, student=student, student_formset=student_formset, grads_only=grads_only)
    return render(request, 'users/mark_inactive_students.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def add_student(request, schoolid):
    school = School.objects.get(id=schoolid)

    # add new student
    if request.method == 'POST':
        form_user = CreateUserForm(request.POST)
        form_student = StudentForm(request.POST)
        if form_user.is_valid() and form_student.is_valid():
            new_user = form_user.save(commit=False)
            new_user.username = str(school.country.code)+"_"+ str(school.abbreviation)+ "_" + request.POST["username"]
            new_user.password="jdbjahbdjhhjdga"
            new_user.save()

            new_student = form_student.save()
            new_student.user = new_user
            new_student.save()

            group = Group.objects.get(name='student')
            new_user.groups.add(group)
            Profile.objects.create(user=new_user, school=school)
            send_system_email_from_school(request, new_user, school, "NewStudent")

            vocational_level = form_student.cleaned_data['vocational_level']
            if not vocational_level:
                vocational_level = EthicsLevel.objects.get(id=1)
            class_ethics = VocationalClass.objects.get(id=1)
            VocationalStatus.objects.create(student=new_student, vocational_level=vocational_level, vocational_class=class_ethics)


            if request.POST.get("save_back"):
                return redirect('manage_students', school.id)
            if request.POST.get("save_add_parent"):
                return redirect('add_parent', new_user.id)
            if request.POST.get("save_new"):
                form_user = CreateUserForm()
                form_student = StudentForm()
        else:
            print(form_student.errors)
    else:
        form_user = CreateUserForm()
        form_student = StudentForm()

    context = dict(form_user=form_user, form_student=form_student,
                   school=school)
    return render(request, 'users/add_student.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def update_student(request, userid):
    user = User.objects.get(id=userid)
    # profile = Profile.objects.get(user=user)
    student = Student.objects.get(user=user)
    school = School.objects.get(id=user.profile.school.id)

    has_grades = EthicsGradeRecord.objects.filter(student=student).exists()

#if student status changes parent status will change as well
    active = student.user.is_active
    parents = student.parent.distinct()

    if request.method == 'POST':
        form_user = UserFormStudent(request.POST, instance=user)
        form_student = StudentForm(request.POST, instance=student)
        # form_profile = ProfileForm(request.POST, instance=profile)
        if form_user.is_valid() and form_student.is_valid():
            user = form_user.save()
            # form_profile.save()
            student = form_student.save()
            vocational_status = VocationalStatus.objects.get(student=student)
            vocational_status.vocational_level = form_student.cleaned_data['vocational_level']
            vocational_status.vocational_class = form_student.cleaned_data['vocational_class']
            vocational_status.save()


#adjusting parent status based on students
            if user.is_active != active:
                if user.is_active == True:
                    for p in parents:
                        p.is_active = True
                        p.save()
                else:
                    for p in parents:
                        if not is_active_school_staff(p):
                            if not has_other_children(p,user):
                                p.is_active = False
                                p.save()

            if user.is_active:
                return redirect('manage_students', school.id)
            else:
                return redirect('manage_inactive_students', school.id)

    else:
        form_user = UserFormStudent(instance=user)
        # form_profile = ProfileForm(instance=profile)
        form_student = StudentForm(instance=student)

    context = dict(form_user=form_user, user=user, form_student=form_student,
                   school=school, has_grades=has_grades)

    return render(request, 'users/update_student.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def delete_student(request, userid):
    user = User.objects.get(id=userid)
    profile = Profile.objects.get(user=user)
    school = profile.school

    if request.method == 'POST':
        parent = user.student.parent.all()
        g = Group.objects.get(name='parent')
        for p in parent:
            if has_other_children(p, user) or is_active_school_staff(p):
                if not has_other_children(p, user):
                    p.groups.remove(g)
                    # not a parent, remove from parent group, keep p as user because if is staff
            else:
                # is neither a parent nor a school staff. Delete p
                p.delete()
        user.delete()
        return redirect('manage_students', school.id)

    context = dict(user=user, school=school)
    return render(request, 'users/delete_student.html', context)


# Parent Data Administration

@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def add_parent(request, userid):
    student = Student.objects.get(user__id=userid)
    school = School.objects.get(id=student.user.profile.school.id)
    # add new parent
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.username = str(school.country.code) + "_" + str(school.abbreviation) + "_" + request.POST[
                "username"]
            new_user.password = "bduaguidfagadbuhujb"
            new_user.save()

            group = Group.objects.get(name='parent')
            new_user.groups.add(group)
            student.parent.add(new_user)
            phone_number = request.POST.get('phone_number')
            Profile.objects.create(user=new_user, phone_number=phone_number, school=school)
            send_system_email_from_school(request, new_user, school, "NewParent")
            if request.POST.get("save_back"):
                return redirect('manage_students', school.id)
            if request.POST.get("save_new"):
                form = CreateUserForm()
    else:
        form = CreateUserForm()

    context = dict(form=form, school=school, student=student, userid=userid)
    return render(request, 'users/add_parent.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def add_parent_from_list(request, userid, listtype):
    student = Student.objects.get(user__id=userid)
    school = School.objects.get(id=student.user.profile.school.id)

    if request.method == 'POST':
        parent_id = request.POST.getlist('parent')
        g = Group.objects.get(name='parent')
        for p in parent_id:
            parent = User.objects.get(id=p)
            student.parent.add(parent)
            parent.groups.add(g)

        return redirect('manage_students', school.id)

    else:
        if listtype == "parent":
            parent_list = User.objects.filter(groups__name="parent", profile__school=school).order_by('last_name')
        elif listtype == "staff":
            parent_list = User.objects.filter(groups__name__in=["instructor", "vocational_coordinator", "school_admin"],
                                              profile__school=school).order_by('last_name').distinct()

    context = dict(school=school, student=student, parent_list=parent_list)
    return render(request, 'users/add_parent_from_list.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def update_parent(request, userid):
    user = User.objects.get(id=userid)
    profile = Profile.objects.get(user=user)
    school = School.objects.get(id=user.profile.school.id)

    if request.method == 'POST':
        form_user = UserForm(request.POST, instance=user)
        form_profile = ProfileForm(request.POST, instance=profile)
        if form_user.is_valid() and form_profile.is_valid():
            form_user.save()
            form_profile.save()
            return redirect('manage_students', school.id)
    else:
        form_user = UserForm(instance=user)
        form_profile = ProfileForm(instance=profile)

    context = dict(form_user=form_user, user=user,
                   form_profile=form_profile,
                   school=school, )

    return render(request, 'users/update_parent.html', context)


@login_required(login_url='login')
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
            if has_children(user) is False:
                group = Group.objects.get(name='parent')
                user.groups.remove(group)
        elif request.POST.get('remove_parent'):
            student.parent.remove(user)
            if has_children(user) is False:
                user.delete()

        return redirect('manage_students', school.id)

    context = dict(user=user, school=school, student=student)
    return render(request, 'users/delete_parent.html', context)


#import student and parent info from Excel
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def import_students(request, schoolid):
    school = School.objects.get(id=schoolid)

    student_group = Group.objects.get(name='student')
    parent_group = Group.objects.get(name='parent')

    if request.method == 'POST' and request.FILES['excel_file']:
        excel_file = request.FILES['excel_file']

        try:
            # Read the uploaded Excel file using pandas
            df = pd.read_excel(excel_file)

            # Process each row
            for _, row in df.iterrows():
                student_first_name = row['Student First Name']
                student_last_name = row['Student Last Name']
                student_username = str(school.country.code)+"_"+ str(school.abbreviation)+ "_" + student_first_name + student_last_name
                student_email = row['Student Email']
                student_graduation_year=row['Student Graduation Year']
                student_birthday = row['Student Birthday']
                student_birthday = pd.to_datetime(student_birthday, format='%m/%d/%Y').date()
                if isinstance(student_birthday, str):
                    student_birthday = pd.to_datetime(student_birthday).date()
                student_gender = row['Student Gender']
                vocational_level = EthicsLevel.objects.filter(name=row['Vocational Level']).first()
                vocational_class = VocationalClass.objects.filter(name=row['Vocational Class']).first()

                parent_first_name = str(row['Parent First Name']) if pd.notna(row['Parent First Name']) else ''
                parent_last_name = str(row['Parent Last Name']) if pd.notna(row['Parent Last Name']) else ''

                if parent_first_name and parent_last_name:
                    parent_username = f"{school.country.code}_{school.abbreviation}_{parent_first_name}{parent_last_name}"
                else:
                    parent_username = None

                parent_email = row['Parent Email']
                parent_phone_number = row['Parent Phone Number']
                if pd.isna(parent_phone_number):
                    parent_phone_number = ''

                if User.objects.filter(username=student_username).exists():
                    messages.warning(request, f"Student {student_username} already exists. Skipping.")
                    continue

                try:
                    student_user = User.objects.create(
                        username=student_username,
                        email=student_email,
                        first_name=student_first_name,
                        last_name=student_last_name,
                    )
                    student_user.set_password("temporary_password")
                    student_user.save()
                    # Add to student group
                    student_user.groups.add(student_group)
                    # Create student profile
                    if not hasattr(student_user, 'profile'):
                        Profile.objects.create(user=student_user, school=school)
                    # Send email to student
                    send_system_email_from_school(request, student_user, school, "NewStudent")

                    # Create student instance
                    try:
                        student_instance = Student.objects.create(
                            user=student_user,
                            birthday=student_birthday,
                            gender=student_gender,
                            graduation_year=student_graduation_year,
                        )

                        if not vocational_level:
                            vocational_level = EthicsLevel.objects.get(id=1)

                        if not vocational_class:
                            vocational_class = VocationalClass.objects.get(id=1)

                        VocationalStatus.objects.create(
                            student=student_instance,
                            vocational_level=vocational_level,
                            vocational_class=vocational_class
                        )

                    except Exception as e:
                        messages.error(request,
                                       f"Failed to create vocational status: {e}")
                    # Create the parent user
                    if parent_username:
                        if User.objects.filter(username=parent_username).exists():
                            parent_user = User.objects.get(username=parent_username)
                        else:
                            parent_user = User.objects.create(
                                username=parent_username,
                                email=parent_email,
                                first_name=parent_first_name,
                                last_name=parent_last_name,
                            )
                        # Set a temporary password
                        parent_user.set_password("temporary_password")  # Optional: you can use a more secure generated one
                        parent_user.save()
                        # Add to parent group
                        parent_user.groups.add(parent_group)
                        # Create Profile
                        if not hasattr(parent_user, 'profile'):
                            Profile.objects.create(user=parent_user, phone_number=parent_phone_number, school=school)
                        # Link parent to student
                        student_instance.parent.add(parent_user)
                        # Send email
                        send_system_email_from_school(request, parent_user, school, "NewParent")


                except Exception as e:
                    messages.error(f"Error: {e}")

            messages.success(request, 'Students and parents imported successfully!')
            return redirect('manage_students', schoolid)

        except Exception as e:
            messages.error(request, f"Error importing file: {e}")
            return redirect('import_students', schoolid)

    return render(request, 'users/import_students.html', {'school': school})


def download_template(request):
    # Create a simple Excel template
    data = {
        'Student First Name': ['John'],
        'Student Last Name': ['Doe'],
        'Student Email': ['jdoe@example.com'],
        'Student Graduation Year': [2027],
        'Student Birthday': ['06/23/2010'],
        'Student Gender': ['m'],
        'Vocational Level': ['Level 1'],
        'Vocational Class': ['Ethics'],
        'Parent First Name': ['Jane'],
        'Parent Last Name': ['Doe'],
        'Parent Email': ['janedoe@example.com'],
        'Parent Phone Number': ['+1234567890'],
    }

    df = pd.DataFrame(data)

    # Create an HTTP response with the content type for Excel files
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="student_parent_template.xlsx"'

    # Write the Excel file to the response
    df.to_excel(response, index=False, sheet_name='VEST Data Template')
    return response