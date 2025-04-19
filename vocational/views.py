from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.db import IntegrityError
from users.decorators import allowed_users
from users.functions import in_group
from .functions import *
from .models import *
from .forms import *
from .filters import *
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponseRedirect
from emailing.functions import send_system_email_from_school
now=timezone.now()
from django.contrib.auth import logout
from django.views import generic
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.forms import formset_factory, BaseFormSet
from django.db.models import Q, Sum, ExpressionWrapper, F, fields, Prefetch
from django.db.models.functions import ExtractWeek

from django.db.models import OuterRef, FloatField, Subquery
from django.db.models.functions import ExtractHour, ExtractMinute, ExtractSecond

# School Admin Views
# School Settings
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin', 'vocational_coordinator'])
def grade_settings(request, schoolid):
    school_year = SchoolYear.objects.filter(school__id=schoolid, active=True).first()

    grade_settings = GradeSettings.objects.filter(school_year=school_year).first()
    if not grade_settings:
        grade_settings = GradeSettings()
        grade_settings.school_year=school_year
        grade_settings.save()

    if request.method == "POST":
        s_form = GradeSettingsForm(request.POST, instance=grade_settings)
        if s_form.is_valid():
            s_form.save()
            messages.info(request, 'Changes have been saved!')
            return redirect('grade_settings', schoolid)
    else:
        s_form = GradeSettingsForm(instance=grade_settings)

    arr = []
    for a in GradeSettings.objects.filter(school_year__school_id=schoolid).order_by("-school_year__name"):
        a_info = [a.school_year, a.progress_ratio, a.summative_ratio, a.track_time, a.get_time_unit_display(),]
        arr.append(a_info)

    context = dict(school_year=school_year, schoolid=schoolid,
                   s_form=s_form, arr=arr)
    return render(request, 'vocational/grade_settings.html', context)

# School Year
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def school_year(request, schoolid):
    schoolyear = SchoolYear.objects.filter(school__id=schoolid).order_by('-name')
    # current_year = school_year.get()
    context = dict(school_year=schoolyear, schoolid=schoolid)
    return render(request, 'vocational/school_year.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def add_school_year(request, schoolid):
    if request.method == "POST":
        form = SchoolYearForm(request.POST)
        if form.is_valid():
            try:
                schoolyear = form.save(commit=False)
                schoolyear.school = School.objects.get(id=schoolid)
                schoolyear.active = True
                schoolyear.save()
                return redirect('manage_school_year', schoolid, schoolyear.id)
            except IntegrityError:
                message= "A school year with this name already exists. \n Go to the School Year tab above to edit as needed."
                messages.info(request, message)

    else:
        form = SchoolYearForm()

    context = dict(form=form, schoolid=schoolid)
    return render(request, 'vocational/add_school_year.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def manage_school_year(request, schoolid, schoolyearid):
    schoolyear = SchoolYear.objects.get(id=schoolyearid)

    if request.method == "POST" and request.POST.get("save"):
        quarter_formset = QuarterFormSet(request.POST, instance=schoolyear)
        if quarter_formset.is_valid():
            quarter_formset.save()
            return redirect('school_year', schoolid)
    elif request.method =="POST" and request.POST.get("active"):
        schoolyear.active = True
        schoolyear.save()

    quarter_formset = QuarterFormSet(instance=schoolyear)

    context = dict(quarter_formset=quarter_formset, school_year=schoolyear, schoolid=schoolid,
                   schoolyearid=schoolyearid)
    return render(request, 'vocational/manage_school_year.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def delete_school_year(request, schoolid, schoolyearid):
    schoolyear = SchoolYear.objects.get(id=schoolyearid)
    school = School.objects.get(id=schoolid)

    if request.method == 'POST':
        schoolyear.delete()
        return redirect('school_year', school.id)

    context = dict(school_year=schoolyear, school=school)
    return render(request, 'vocational/delete_school_year.html', context)


# Vocational Coordinator Views
# Department
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator'])
def department_list(request, schoolid):
    department = Department.objects.filter(school__id=schoolid)
    context = dict(department=department, schoolid=schoolid)
    return render(request, 'vocational/department_list.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator'])
def manage_department(request, schoolid):
    school = School.objects.get(id=schoolid)
    DepartmentFormSet = inlineformset_factory(School, Department, fields=('name', 'is_active',), extra=3,
                                              can_delete=True)
    if request.method == "POST":
        department_formset = DepartmentFormSet(request.POST, instance=school)
        if department_formset.is_valid():
            department_formset.save()
            if request.POST.get("add"):
                return redirect('manage_department', school.id)
            return redirect('department_list', schoolid)
    else:
        department_formset = DepartmentFormSet(instance=school)

    context = dict(department_formset=department_formset, schoolid=schoolid)
    return render(request, 'vocational/manage_department.html', context)


# Skills
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator'])
def skill_list(request, schoolid):
    department = Department.objects.filter(school__id=schoolid)
    context = dict(department=department)
    return render(request, 'vocational/skill_list.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['instructor', 'isei_admin', 'vocational_coordinator'])
def instructor_skill_list(request, userid):
    user = User.objects.get(pk=userid)
    instructor_assignment = InstructorAssignment.objects.filter(instructor__user=user)
    department = [assignment.department for assignment in instructor_assignment]

    context = dict(department=department, userid=userid)
    return render(request, 'vocational/skill_list.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'instructor'])
def manage_skill(request, departmentid, userid=None):
    department = Department.objects.get(id=departmentid)
    schoolid = School.objects.get(id=department.school.id).id
    SkillFormSet = inlineformset_factory(Department, VocationalSkill, fields=('name', 'description', 'weight', 'level', 'code'),
                                         extra=3, can_delete=True)

    if request.method == "POST":
        skill_formset = SkillFormSet(request.POST, instance=department)
        if skill_formset.is_valid():
            skill_formset.save()
            if request.POST.get("add"):
                return redirect('manage_skill', departmentid)
            if not userid:
                return redirect('skill_list', schoolid)
            else:
                return redirect('instructor_skill_list', userid)
    else:
        skill_formset = SkillFormSet(instance=department)

    context = dict(skill_formset=skill_formset, department=department)
    return render(request, 'vocational/manage_skill.html', context)


# Instructor Assignment
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator'])
def instructor_assignment(request, schoolid):
    instructorassignment = InstructorAssignment.objects.filter(department__school__id=schoolid)

    context = dict(instructor_assignment=instructorassignment, schoolid=schoolid)
    return render(request, 'vocational/instructor_assignment.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator'])
def manage_instructor_assignment(request, schoolid):
    school = School.objects.get(id=schoolid)

    if request.method == "POST":
        instructor_formset = InstructorAssignmentFormSet(request.POST, queryset=InstructorAssignment.objects.filter(
            department__school=school), form_kwargs={'school': school})
        if instructor_formset.is_valid():
            instructor_formset.save()
            if request.POST.get("add"):
                return redirect('manage_instructor_assignment', schoolid)
            return redirect('instructor_assignment', schoolid)

    else:
        instructor_formset = InstructorAssignmentFormSet(
            queryset=InstructorAssignment.objects.filter(department__school=school), form_kwargs={'school': school})

    context = dict(instructor_formset=instructor_formset)
    return render(request, 'vocational/manage_instructor_assignment.html', context)


# Student Assignment to vocational areas
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator'])
def student_assignment(request, schoolid):
    studentassignment = StudentAssignment.objects.filter(department__school__id=schoolid,
                                                         quarter__school_year__active=True).order_by(
        'quarter__school_year', '-quarter__name')
    quarter = Quarter.objects.filter(id__in=studentassignment.values_list('quarter', flat=True)).order_by('-name')
    latest_quarter = quarter.first()

    new_quarter = Quarter.objects.filter(school_year__school_id=schoolid, school_year__active=True).exclude(
        id__in=studentassignment.values_list('quarter', flat=True)).order_by('-school_year', 'name')
    newest_quarter = new_quarter.first()

    # If this is a POST request, we've got some copying to do
    if request.method == 'POST':

        # Copy assignments from the latest to the new quarter
        assignments_to_copy = StudentAssignment.objects.filter(quarter=latest_quarter)
        for assignment in assignments_to_copy:
            # Create new assignment with the same values, but attach to the new quarter
            new_assignment = StudentAssignment.objects.create(
                quarter=newest_quarter,
                department=assignment.department,
                updated_at=assignment.updated_at
            )
            new_assignment.student.set(assignment.student.all())
        return redirect('student_assignment', schoolid=schoolid)



    context = dict(student_assignment=studentassignment,
                   quarter=quarter, new_quarter=new_quarter,
                   schoolid=schoolid)
    return render(request, 'vocational/student_assignment.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator'])
def student_assignment_student_filter(request, schoolid):
    studentassignment = StudentAssignment.objects.filter(department__school__id=schoolid).order_by(
        '-quarter__school_year', '-quarter__name')
    student = Student.objects.filter(id__in=studentassignment.values_list('student', flat=True), user__is_active=True)

    student_filter = StudentFilter(request.GET, queryset=student)
    student = student_filter.qs

    new_quarter = Quarter.objects.filter(school_year__school_id=schoolid, school_year__active=True).exclude(
        id__in=studentassignment.values_list('quarter', flat=True)).order_by('-school_year', 'name')

    context = dict(student=student, schoolid=schoolid, new_quarter=new_quarter,
                   student_filter=student_filter)
    return render(request, 'vocational/student_assignment_student_filter.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator'])
def student_assignment_department_filter(request, schoolid):
    studentassignment = StudentAssignment.objects.filter(department__school__id=schoolid, quarter__school_year__active=True)
    department_filter = StudentAssignmentFilter(request.GET, queryset=studentassignment)
    studentassignment = department_filter.qs

    department = Department.objects.filter(id__in=studentassignment.values_list('department', flat=True))

    new_quarter = Quarter.objects.filter(school_year__school_id=schoolid, school_year__active=True).exclude(
        id__in=studentassignment.values_list('quarter', flat=True)).order_by('name')


    active_school_year = SchoolYear.objects.get(school_id=schoolid, active=True)

    context = dict(department=department, schoolid=schoolid, new_quarter=new_quarter,
                   department_filter=department_filter, active_school_year = active_school_year)
    return render(request, 'vocational/student_assignment_department_filter.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator'])
def manage_student_assignment(request, schoolid, quarterid, years_to_grad=None):
    school = School.objects.get(id=schoolid)
    quarter = Quarter.objects.get(id=quarterid)

    active_school_year= SchoolYear.objects.get(school_id=schoolid, active=True)
    start_year = active_school_year.start_date.year

    if years_to_grad:
        graduation_year = []
        for g in years_to_grad:
            g_y = int(start_year) + int(g)
            graduation_year.append(g_y)
    else:
        graduation_year = None

    if request.method == "POST" and request.POST.get("save"):
        student_formset = StudentAssignmentFormSet(request.POST, instance=quarter, form_kwargs={'school': school, 'graduation_year': graduation_year})
        if student_formset.is_valid():
            student_formset.save()
            if request.POST.get("add"):
                return redirect('manage_student_assignment', schoolid, quarterid)
            return redirect('student_assignment', schoolid)

    else:
        student_formset = StudentAssignmentFormSet(instance=quarter, initial=[{'school': school, }],
                                                   form_kwargs={'school': school, 'graduation_year': graduation_year})

    context = dict(student_formset=student_formset, quarter=quarter, schoolid=schoolid, quarterid=quarterid, years_to_grad = years_to_grad)
    return render(request, 'vocational/manage_student_assignment.html', context)



# Manage Grades
#just grades from current school year
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'instructor'])
def grade_list(request, userid):
    user = User.objects.get(id=userid)
    current_year = SchoolYear.objects.filter(school_id = user.profile.school.id, active=True).first()
    quarter = Quarter.objects.filter(school_year=current_year).order_by("name")

    if in_group(user,"vocational_coordinator"):
        grades = EthicsGradeRecord.objects.filter(quarter__school_year=current_year).order_by('-vc_validated','-quarter','student')
        filter = GradeFilterVocationalCoordinator(request.GET, request=request, queryset=grades)
        student_assignment = StudentAssignment.objects.filter(quarter__in =quarter).order_by("quarter")
    else:
        grades = EthicsGradeRecord.objects.filter(instructor_id=userid, quarter__school_year=current_year).order_by('-vc_validated','-quarter','student')
        filter = GradeFilterInstructor(request.GET, request=request, queryset=grades)
        department = InstructorAssignment.objects.filter(instructor=user.profile).values("department")
        student_assignment = StudentAssignment.objects.filter(quarter__in =quarter, department__in=department).order_by(quarter)

    for obj in grades:
        if (obj.score() == 0 and obj.created_at + timedelta(days=1) < now):
            obj.delete()

    grades = filter.qs
    all=False

    context = dict(grades=grades, filter=filter, all=all, quarter = quarter, student_assignment=student_assignment)

    return render(request, 'vocational/grade_list.html', context)

#all grades ever entered
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'instructor'])
def grade_list_all(request, userid):
    user = User.objects.get(id=userid)
    if in_group(user,"vocational_coordinator"):
        grades = EthicsGradeRecord.objects.filter(quarter__school_year__school__id=user.profile.school.id).order_by('-vc_validated','-evaluation_date','student')
        filter = GradeFilterVocationalCoordinator(request.GET, request=request, queryset=grades)
    else:
        grades = EthicsGradeRecord.objects.filter(instructor_id=userid).order_by('-evaluation_date','student')
        filter = GradeFilterInstructor(request.GET, request=request, queryset=grades)

    for obj in grades:
        if (obj.score() == 0 and obj.created_at + timedelta(days=1) < now):
            obj.delete()

    grades = filter.qs
    all=True
    context = dict(grades=grades, filter=filter, all=all)
    return render(request, 'vocational/grade_list.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'instructor'])
def initiate_grade_entry(request, schoolid):
    error_message=None

    role = request.GET.get('role', None)


    if request.method == 'POST':
        departmentid = request.POST.get('department')
        quarterid = request.POST.get('quarter')
        if not departmentid: error_message = "No departments have been assigned to you yet. Please contact " \
                                             "Vocational Supervisor "
        else:
            if not quarterid: error_message = "There is no quarter selected or set up. Please contact " \
                                              "Vocational Supervisor"
            else:
                type = request.POST.get('type')
                evaluation_date = request.POST.get('date')
                if type=="K":
                    department = Department.objects.get(id=departmentid)
                    if VocationalSkill.objects.filter(department=department).exists():
                        return redirect('add_skill_grade', quarterid, departmentid, evaluation_date, request.user.id)
                    else:
                        error_message = 'There are no skills entered for this department. Please contact Vocational Coordinator'
                else:
                    if role == 'vocational_coordinator':
                        profile_id = request.POST.get('instructor')
                        user = User.objects.get(profile__id=profile_id)
                        return redirect('add_grade', quarterid, type, departmentid, evaluation_date, user.id)
                    else:
                        return redirect('add_grade', quarterid, type, departmentid, evaluation_date, request.user.id)


    assignments = InstructorAssignment.objects.filter(instructor__id=request.user.profile.id)
    if role =='vocational_coordinator':
        department = Department.objects.filter(school__id=schoolid, is_active=True)
    else:
        department = Department.objects.filter(school__id=schoolid, is_active=True, instructorassignment__in=assignments)

    # quarter_with_grades = Quarter.objects.filter(id__in=grades.values_list('quarter', flat=True))
    # new_quarter = Quarter.objects.filter(school_year__school_id=schoolid, school_year__active=True).exclude(
    #    id__in=grades.values_list('quarter', flat=True)).order_by('name
    school_year_id=SchoolYear.objects.values_list('id', flat=True).filter(school_id=schoolid, active=True).first()
    active_quarter = Quarter.objects.filter(school_year__school_id=schoolid, school_year__active=True).order_by('name')

    q=current_quarter(school_year_id)
    if q:
        current_quarter_id=current_quarter(school_year_id).id
    else:
        messages.warning(request, "This school year/quarter is not set up properly for grade entry. \n Please contact school administrator or vocational coordinator. ")
        return redirect('crash')

    if role =='vocational_coordinator':
        instructor = Profile.objects.filter(user__is_active=True, school_id=schoolid, user__groups__name='instructor')
    else:
        instructor=None


    context = dict(active_quarter=active_quarter, department=department, current_quarter_id=current_quarter_id,
                   error_message=error_message, role=role, instructor=instructor)
    return render(request, 'vocational/initiate_grade_entry.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'instructor'])
def add_grade(request, quarterid, type, departmentid, evaluation_date, instructorid):

    quarter = Quarter.objects.get(id=quarterid)
    instructor = User.objects.get(id=instructorid)
    department = Department.objects.get(id=departmentid)
    #TODO filter out students that have been graded within a certain time frame
    # existing_grade below brings up an existing grade if one has been entered the same day (same department + student)
    student = Student.objects.filter(student_assignment__department=department, student_assignment__quarter= quarter)

    if not student:
        messages.error(request, "There are no students assigned to this department for this quarter. " \
                        "Please contact Vocational Coordinator")


    grade = EthicsGradeRecord()
    grade.quarter = quarter
    grade.evaluation_date =datetime.strptime(evaluation_date, "%Y-%m-%d").date()

    grade.instructor = instructor
    grade.department = department
    grade.type = type
    grade_form = EthicsGradeInstructorForm(instance=grade)
    grade_form.fields["student"].queryset = student

    latest_grades = EthicsGradeRecord.objects.filter(department=department, evaluation_date__gt=datetime.strptime(evaluation_date, '%Y-%m-%d').date() - timedelta(days=63)).order_by('-evaluation_date')

    if request.method == "POST":
        grade_form = EthicsGradeInstructorForm(request.POST, instance=grade)
        if grade_form.is_valid():
            existing_grade = EthicsGradeRecord.objects.filter(department=grade.department, student = grade_form.cleaned_data['student'], evaluation_date = grade.evaluation_date).first()
            if existing_grade:
                grade = existing_grade
            else:
                grade = grade_form.save()
            return redirect('finalize_grade', grade.id)
        else:
            print("Not valid")

    #grades=EthicsGradeRecord.objects.filter()
    context = dict(grade_form=grade_form, grade=grade, latest_grades = latest_grades)
    return render(request, 'vocational/add_grade.html', context)


# AJAX used in add_grade
def get_level(request):
    student_id = request.GET.get('student', None)
    student = Student.objects.get(id=student_id)
    if VocationalStatus.objects.filter(student=student):
        response = {
            'level_id': student.vocationalstatus.vocational_level.id
        }
    else:
        response = {'level_id': 1}
    return JsonResponse(response)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'instructor'])
def finalize_grade(request, gradeid):
    grade = EthicsGradeRecord.objects.get(id=gradeid)
    error_messages=None
    if request.method == "POST":
        time_form=EthicsGradeTimeForm(request.POST, instance=grade)
        if time_form.is_valid(): time_form.save()
        student_discussion_form = StudentDiscussionForm(request.POST, instance=grade)
        if grade.type == "S":
             ethic_form = EthicsSummativeGradeFormSet(request.POST, instance=grade)
        else:
            ethic_form = EthicsFormativeGradeFormSet(request.POST, instance=grade)
            comments_form = FormativeCommentsForm(request.POST, instance=grade)
            if comments_form.is_valid():
                comments_form.save()

        student_discussion_form=StudentDiscussionForm(request.POST, instance=grade)
        if student_discussion_form.is_valid():
            student_discussion_form.save()

        for form in ethic_form:
            form.full_clean()  # Explicitly call full_clean on each form
        if ethic_form.is_valid():
            ethic_form.save()
            if request.POST.get("save_c"):
                return redirect('add_grade', grade.quarter.id, grade.type, grade.department.id, grade.evaluation_date, grade.instructor.id)
            if request.POST.get("save_r"):
                return redirect('grade_list', grade.instructor.id )
        else:
            error_messages = ethic_form.errors

    if request.method == "GET" and (request.GET.get("delete_add") or request.GET.get("delete_list")):
        if request.GET.get("delete_add"):
            grade.delete()
            return redirect('initiate_grade_entry', grade.quarter.school_year.school_id )
            #return redirect('add_grade', grade.quarter.id, grade.type, grade.department.id, grade.evaluation_date,
            #            grade.instructor.id)
        else:
            grade.delete()
            return redirect('grade_list', grade.instructor.id)

    ethic = EthicsDefinition.objects.filter(level= grade.level)
    if grade.type=="S":
        if not EthicsSummativeGrade.objects.filter(grade_record=grade):
            for i in ethic:
                EthicsSummativeGrade(ethic=i, grade_record=grade).save()
        ethic_formset = EthicsSummativeGradeFormSet(instance=grade)

    else:
        if not EthicsFormativeGrade.objects.filter(grade_record=grade):
            for i in ethic:
               EthicsFormativeGrade(ethic=i, grade_record=grade).save()
        ethic_formset = EthicsFormativeGradeFormSet(instance=grade)

    formative_comments_form = FormativeCommentsForm(instance=grade)
    student_discussion_form = StudentDiscussionForm(instance=grade)
    time_form=EthicsGradeTimeForm(instance=grade)

    context = dict(grade=grade, ethic_formset = ethic_formset,
                   formative_comments_form = formative_comments_form,
                   student_discussion_form = student_discussion_form,
                   time_form=time_form, error_messages=error_messages)
    return render(request, 'vocational/finalize_grade.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'instructor'])
def add_skill_grade(request, quarterid, departmentid, evaluation_date, instructorid):
    quarter = Quarter.objects.get(id=quarterid)
    instructor = User.objects.get(id=instructorid)
    department = Department.objects.get(id=departmentid)
    student = Student.objects.filter(student_assignment__department=department, student_assignment__quarter= quarter)
    grade = SkillGradeRecord()
    grade.quarter = quarter
    grade.instructor = instructor
    grade.department = department
    grade.evaluation_date = datetime.strptime(evaluation_date, '%Y-%m-%d').date()
    grade_form = SkillGradeRecordInstructorForm(instance=grade)
    grade_form.fields["student"].queryset = student

    if request.method == "POST":
        grade_form = SkillGradeRecordInstructorForm(request.POST, instance=grade)
        if grade_form.is_valid():
            grade = grade_form.save()
            return redirect('finalize_skill_grade', grade.id)
        else:
            print("Not valid")

    #grades = SkillGradeRecord.objects.filter()

    context = dict( grade_form=grade_form, grade=grade)
    return render(request, 'vocational/add_skill_grade.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'instructor'])
def finalize_skill_grade(request, gradeid):
    grade = SkillGradeRecord.objects.get(id=gradeid)
    student=grade.student

    skill_grade_records = SkillGradeRecord.objects.filter(department=grade.department, student=student)
    selected_grade_record_ids = [record.id for record in skill_grade_records]

    vocational_skills = VocationalSkill.objects.filter(skillgrade__grade_record__id__in=selected_grade_record_ids).distinct().order_by('id')
    #print(vocational_skills)

    result_dict ={}

    for skill in vocational_skills:
        skill_grades=SkillGrade.objects.filter(skill=skill, grade_record__student = student)
        skill_data= {
            'skill_name':skill.name,
            'grades':[]
        }
        for skill_grade in skill_grades:
            if skill_grade.score:
                grade_data = {
                    'score':skill_grade.score,
                    'evaluation_date':skill_grade.grade_record.evaluation_date
                }
                skill_data['grades'].append(grade_data)

        result_dict[skill.id]=skill_data

    if request.method == "POST":
        skill_form = SkillGradeFormSet(request.POST, instance=grade)
        if skill_form.is_valid():
            has_scores = any(form.cleaned_data.get('score') for form in skill_form.forms)
            if has_scores:
                # Scores are entered, proceed with saving
                skill_form.save()
            else:
                grade.delete()
            if request.POST.get("save_c"):
                return redirect('add_skill_grade', grade.quarter.id, grade.department.id, grade.evaluation_date, grade.instructor.id)
            #ToDo create skill grade list of some sort
            if request.POST.get("save_r"):
                #return redirect('skill_grade_list_selection', grade.instructor.id )
                return redirect('skill_grade_list_by_skill', grade.department.id)
        else:
            print(skill_form.errors)

    if request.method == "GET" and (request.GET.get("delete_add") or request.GET.get("delete_list")):
        if request.GET.get("delete_add"):
            grade.delete()
            return redirect('initiate_grade_entry', grade.quarter.school_year.school_id )
        else:
            grade.delete()
            #ToDo create skill grade list of some sort
            return redirect('initiate_grade_entry', grade.quarter.school_year.school_id )
            #return redirect('grade_list', grade.instructor.id)


    skill = VocationalSkill.objects.filter(department=grade.department)
    if not SkillGrade.objects.filter(grade_record=grade):
        for s in skill:
               SkillGrade(skill=s, grade_record=grade).save()
    skill_formset = SkillGradeFormSet(instance=grade)

    context = dict(grade=grade, skill_formset = skill_formset, result_dict=result_dict)
    return render(request, 'vocational/finalize_skill_grade.html', context)



@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'instructor'])
def skill_grade_list_selection(request, userid):

    departments = Department.objects.filter(instructorassignment__instructor__user_id=userid)
    error_message =None
    if departments:
        skills = VocationalSkill.objects.filter(department__in=departments)
        if not skills:
            error_message = "There are no skills entered for this department(s) yet. Please add skills or contact Vocational Coordinator"

        if departments and request.method == 'POST':
            department_id = request.POST.get('department_id')
            if "by_skill" in request.POST:
                return skill_grade_list_by_skill(request, department_id)
            else:
                return skill_grade_list_by_student(request, department_id)
    else:
        error_message=" There are no departments assigned. Please contact vocational coordinator"

    context = {
        'departments': departments,
        'error_message':error_message,
        'userid': userid,
    }
    return render(request, 'vocational/skill_grade_list_selection.html', context)



@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'instructor'])
def skill_grade_list_by_skill(request, department_id):

    department = Department.objects.get(id=department_id)
    skill_scores = {}
    error_message = None

    if not department:
        error_message="No departments have been assigned yet. Please contact the Vocational Supervisor."
    else:
        skills = VocationalSkill.objects.filter(department=department)
        if not skills:
            error_message= "There are no skills entered for this department yet. Please add skills or contact Vocational Coordinator"
        else:
            students = Student.objects.filter(user__is_active=True, student_assignment__department=department).distinct()

            # Create an empty dictionary to hold the scores and evaluation dates
            skill_scores = {}

            for skill in skills:
                skill_scores[skill] = {}
                for student in students:
                    # Retrieve all grade records for the skill, student, and department
                    grade_records = SkillGradeRecord.objects.filter(
                        student=student,
                        department=department,
                        skillgrade__skill=skill
                    )

                    scores_and_dates = []
                    for grade_record in grade_records:
                        skill_grade = SkillGrade.objects.get(grade_record=grade_record, skill=skill)
                        if skill_grade.score:
                            score = skill_grade.score
                            evaluation_date = grade_record.evaluation_date
                            scores_and_dates.append((score, evaluation_date))

                    if scores_and_dates:
                        # Store the scores and evaluation dates in the dictionary
                        skill_scores[skill][student] = scores_and_dates
                    else:
                        # Set None for scores and evaluation dates if no grade records exist
                        skill_scores[skill][student] = None

    context = {
        'skill_scores': skill_scores,
        'error_message':error_message,
        'department_id': department_id,
    }

    return render(request, 'vocational/skill_grade_list_by_skill.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'instructor'])
def skill_grade_list_by_student(request, department_id):

    department = Department.objects.get(id=department_id)
    skills = VocationalSkill.objects.filter(department=department)
    error_message=None

    if not skills:
        error_message = "There are no skills entered for this department yet. Please add skills or contact Vocational Coordinator"

    students = Student.objects.filter(user__is_active=True, student_assignment__department=department).distinct()

    # Create an empty dictionary to hold the scores and evaluation dates
    skill_scores = {}

    for student in students:
        skill_scores[student] = {}
        for skill in skills:
            # Retrieve all grade records for the skill, student, and department
            grade_records = SkillGradeRecord.objects.filter(
                student=student,
                department=department,
                skillgrade__skill=skill
            )

            scores_and_dates = []
            for grade_record in grade_records:
                skill_grade = SkillGrade.objects.get(grade_record=grade_record, skill=skill)
                if skill_grade.score:
                    score = skill_grade.score
                    evaluation_date = grade_record.evaluation_date
                    scores_and_dates.append((score, evaluation_date))

            if scores_and_dates:
                # Store the scores and evaluation dates in the dictionary
                skill_scores[student][skill] = scores_and_dates
            else:
                # Set None for scores and evaluation dates if no grade records exist
                skill_scores[student][skill] = None

    context = {
        'skill_scores': skill_scores, 'error_message':error_message, 'department_id':department_id,
    }

    return render(request, 'vocational/skill_grade_list_by_student.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'instructor', 'parent','student'])
def student_skill_grades(request, student_id):

    student = Student.objects.get(id=student_id)

    assigned_departments = Department.objects.filter(studentassignment__student=student)
    # Create an empty dictionary to hold the scores and evaluation dates
    skill_scores = {}

    for department in assigned_departments:
        skill_scores[department] = {}
        skills = VocationalSkill.objects.filter(department = department)
        for skill in skills:
            # Retrieve all grade records for the skill, student, and department
            grade_records = SkillGradeRecord.objects.filter(
                student=student,
                department=department,
                skillgrade__skill=skill
            )

            scores_and_dates = []
            for grade_record in grade_records:
                skill_grade = SkillGrade.objects.get(grade_record=grade_record, skill=skill)
                if skill_grade.score:
                    score = skill_grade.score
                    evaluation_date = grade_record.evaluation_date
                    scores_and_dates.append((score, evaluation_date))

            if scores_and_dates:
                # Store the scores and evaluation dates in the dictionary
                skill_scores[department][skill] = scores_and_dates
            else:
                # Set None for scores and evaluation dates if no grade records exist
                skill_scores[department][skill] = None

    context = { 'skill_scores': skill_scores }

    return render(request, 'vocational/student_skill_grades.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['vocational_coordinator'])
def vc_validate_grades(request, schoolid):

    i_grades = EthicsGradeRecord.objects.filter(vc_validated=None, instructor__profile__school__id=schoolid).order_by("evaluation_date")
    school = School.objects.get(id=schoolid)
    errors=None

    if request.method == 'POST':
        formset = VCValidationFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                ethics_grade_record = form.save(commit=False)
                accepted_level = form.cleaned_data['accepted_level']
                if accepted_level:
                    ethics_grade_record.student.vocationalstatus.vocational_level = accepted_level
                    ethics_grade_record.student.vocationalstatus.save()
                ethics_grade_record.save()

            #grades = formset.save()
            #for g in grades:
                if ethics_grade_record.vc_validated:
                    send_system_email_from_school(request, ethics_grade_record.student.user, school, "GradePostedStudent")
                    for p in ethics_grade_record.student.parent.all():
                        send_system_email_from_school(request, p, school, "GradePostedParent", ethics_grade_record.student)
                else:
                    if ethics_grade_record.vc_comment:
                        instructor = ethics_grade_record.instructor
                        send_system_email_from_school(request, instructor, school, "GradeNotValidated", ethics_grade_record.student, ethics_grade_record.vc_comment)

            #not_validated = EthicsGradeRecord.objects.filter(vc_validated=None, instructor__profile__school__id=schoolid)
            #instr_id = not_validated.values_list('instructor_id')
            #instructors = User.objects.filter(id__in = instr_id)
            #for i in instructors:
            #    send_system_email_from_school(request, i, school, "GradeNotValidated")

            return redirect('grade_list', request.user.id)
        else:
            errors = formset.non_form_errors()
    else:
        formset = VCValidationFormSet(queryset=i_grades)

    context = dict(formset=formset, errors=errors, schoolid=schoolid)
    return render(request, 'vocational/vc_validate_grades.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['vocational_coordinator'])
def vc_validate_all_grades(request, schoolid):
    i_grades = EthicsGradeRecord.objects.filter(vc_validated=None, instructor__profile__school__id=schoolid).order_by(
        "evaluation_date")

    for ethics_grade_record in i_grades:
        ethics_grade_record.vc_validated = datetime.today().date()
        ethics_grade_record.save()

    return redirect('grade_list', request.user.id)

@login_required(login_url='login')
@allowed_users(allowed_roles=['vocational_coordinator'])
def vc_unvalidate_grades(request, schoolid):

    i_grades= EthicsGradeRecord.objects.filter(~Q(vc_validated = None), instructor__profile__school__id=schoolid).order_by("-evaluation_date")

    if request.method == 'POST':
        formset = VCValidationFormSet(request.POST)
        if formset.is_valid():
            grades = formset.save()
            #for g in grades:
                #print(g.student.user.email)
            return redirect('grade_list', request.user.id)
    else:
        formset = VCValidationFormSet(queryset=i_grades)

    context = dict(formset=formset)
    return render(request, 'vocational/vc_unvalidate_grades.html', context)

#not used
# @login_required(login_url='login')
# @allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'instructor'])
# def student_discussion_list(request, userid=None):
#     if userid is None:
#         userid = request.user.id
#     grades = EthicsGradeRecord.objects.filter(instructor_id=userid, student_discussed=None)
#     context = dict(grades=grades,)
#     return render(request, 'vocational/student_discussion_list.html', context)
#
# @login_required(login_url='login')
# @allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'instructor'])
# def student_discussion(request, gradeid):
#     grade = EthicsGradeRecord.objects.get(id=gradeid)
#
#     if request.method == "POST":
#
#         form = StudentDiscussionForm(request.POST, instance=grade)
#         if form.is_valid():
#             form.save()
#             #return redirect('add_grade', grade.quarter.id, grade.type, grade.department.id, grade.evaluation_date, grade.instructor.id)
#         else:
#             print(form.errors)
#
#     form = FormativeCommentsForm(instance=grade)
#
#     context = dict(grade=grade, form = form )
#     return render(request, 'vocational/student_discussion.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'instructor', 'parent', 'student'])
def student_vocational_info(request, studentid):

    student=Student.objects.get(id=studentid)
    arr=[]
    for a in student.student_assignment.all().order_by('-quarter'):
        grades=EthicsGradeRecord.objects.filter(student=student, department=a.department, quarter=a.quarter, vc_validated__isnull=False)
        avg=average(grades, a.quarter.school_year)
        if grades.last():
            level=grades.last().level
        else:
            level=None
        a_info = [a.quarter.school_year, a.quarter.get_name_display, a.department, avg, level]
        arr.append(a_info)


    context=dict(student=student, arr=arr)
    return render(request, 'vocational/student_vocational_info.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'instructor', 'parent', 'student'])
def s_vocational_info(request, studentid):

    student=Student.objects.get(id=studentid)
    arr=[]
    for a in student.student_assignment.all().order_by('-quarter'):
        grades=EthicsGradeRecord.objects.filter(student=student, department=a.department, quarter=a.quarter)
        avg=average(grades, a.quarter.school_year)
        if grades.last():
            level=grades.last().level
        else:
            level=None
        a_info = [a.quarter.school_year, a.quarter.get_name_display, a.department, avg, level]
        arr.append(a_info)


    context=dict(student=student, arr=arr)
    return render(request, 'vocational/s_vocational_info.html', context)


#parent views
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'parent'])
def parent_page(request, parentid):
    children = Student.objects.filter(parent__id=parentid)

    context=dict(children=children)
    return render(request, 'vocational/parent_page.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'parent', 'student', 'school_admin', 'vocational_coordinator'])
def student_grades(request, studentid):

    #request.session['selected_student_id'] = Student.objects.filter(id=studentid).first()

    grades = EthicsGradeRecord.objects.filter(student_id=studentid, vc_validated__isnull=False).order_by('-evaluation_date')
    student=Student.objects.filter(id=studentid).first()
    filter = GradeFilterStudentParent(request.GET, request=request, queryset=grades)

    for obj in grades:
        if (obj.score() == 0 and obj.created_at + timedelta(days=1) < now):
            obj.delete()

    grades = filter.qs
    avg = average(grades)

    context = dict(student=student, grades=grades, filter=filter, avg=avg)
    return render(request, 'vocational/student_grades.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'school_admin', 'student'])
def student_page(request, userid):
    student = Student.objects.get(user__id=userid)

    context=dict(student=student)
    return render(request, 'vocational/student_page.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'parent', 'student', 'school_admin', 'vocational_coordinator'])
def average_quarter_grades(request, schoolid, quarterid):

    school = School.objects.get(id=schoolid)
    quarter = Quarter.objects.get(id=quarterid)

    student_summaries  = calculate_quarter_averages(school, quarter)

    context=dict(student_summaries=student_summaries, quarter=quarter)
    return render(request, 'vocational/average_quarter_grades.html', context)


#time card views

@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'instructor', 'vocational_coordinator', 'school_admin'])
def time_card_dashboard(request, userid, vc='no'):

    # Fetch the profile, assignments, departments, and active quarter as before
    profile = Profile.objects.get(user=userid)
    school_id = profile.school.id
    #school_year_id = SchoolYear.objects.values_list('id', flat=True).filter(school_id=school_id, active=True).first()


    if vc.lower() == "yes":
        departments = Department.objects.filter(school_id=school_id, is_active=True)
    else:
        assignments = InstructorAssignment.objects.filter(instructor__id=profile.id)
        departments = Department.objects.filter(school__id=school_id, is_active=True, instructorassignment__in=assignments)

    active_quarter = Quarter.objects.filter(
        school_year__school_id=school_id, school_year__active=True).order_by('name')

    # Fetch unique students directly without intermediary lists
    students_ids = StudentAssignment.objects.filter(quarter__in=active_quarter,
                                                    department__in=departments
                                                    ).values_list('student__id', flat=True).distinct()
    unique_students_qs = Student.objects.filter(id__in=students_ids)

    # Initialize the TimeCardFilterForm as before
    filter = TimeCardFilterForm(request.POST or None, department_qs=departments, quarter_qs=active_quarter,
                                student_qs=unique_students_qs)

    # If the form is submitted (POST request) and is valid, fetch the timecards
    if request.method == 'POST' and filter.is_valid():
        department = filter.cleaned_data.get('department')
        quarter = filter.cleaned_data.get('quarter')
        from_date = filter.cleaned_data.get('from_date')
        to_date = filter.cleaned_data.get('to_date')
        student = filter.cleaned_data.get('student')

        timecards = TimeCard.objects.filter(
            Q(student_assignment__quarter=quarter) if quarter else Q(),
            Q(student_assignment__department=department) if department else Q(),
            Q(student=student) if student else Q(),
            Q(time_in__range=(from_date, to_date)) if (from_date and to_date) else Q()
        ).order_by('-time_in','student_assignment__department')
    else:
        # This is the initial GET request, fetch only the last 7 day timecards
        #today = datetime.today()
        today=timezone.now()
        last_week = today - timedelta(days=7)

        timecards = TimeCard.objects.filter(
            student_assignment__quarter__in=active_quarter,
            student_assignment__department__in=departments,
            time_in__gte=last_week
        ).order_by('-time_in','student_assignment__department')

        # Accumulate total time as seconds
    total_seconds = sum([(t.time_out - t.time_in).total_seconds() for t in timecards if t.time_out])

    # Convert total_seconds to time delta
    total_time = timedelta(seconds=total_seconds)

    # Convert total_time to total hours, and total minutes
    total_hours = total_time.days * 24 + total_time.seconds // 3600
    total_minutes = (total_time.seconds // 60) % 60

    school_year_id=SchoolYear.objects.values_list('id', flat=True).filter(school_id=school_id, active=True).first()
    q = current_quarter(school_year_id)
    if q:
        current_quarter_id = current_quarter(school_year_id).id
    else:
        messages.warning(request,
                         "This school year/quarter is not set up properly for grade entry. \n Please contact school administrator or vocational coordinator. ")
        return redirect('crash')

    # Same as before
    context = dict(active_quarter=active_quarter, departments=departments,
                   timecards=timecards, filter=filter, userid=userid,
                   total_hours=total_hours, total_minutes=total_minutes,
                   school_id=school_id, current_quarter_id=current_quarter_id)
    return render(request, 'vocational/time_card_dashboard.html', context)


#automatic time card entry
class TimeCardView(generic.FormView):
    template_name = 'vocational/time_card.html'
    form_class = TimeCardForm

    def get(self, request, *args, **kwargs):

        department_id = kwargs.get('department_id', request.GET.get('department_id'))
        quarter_id = kwargs.get('quarter_id', request.GET.get('quarter_id'))
        self.kwargs.update({
            'department_id': department_id,
            'quarter_id': quarter_id,
        })
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quarter_id = self.kwargs['quarter_id']
        department_id = self.kwargs['department_id']

        today = timezone.now().date()

        try:
            assignment = StudentAssignment.objects.get(quarter_id=quarter_id, department_id=department_id)
        except StudentAssignment.DoesNotExist:
            assignment = None


        if assignment:
            assignment.students = assignment.student.all()
            for student in assignment.students:
                student.active_time_card = TimeCard.objects.filter(
                        student_assignment=assignment, student=student,
                        time_in__date=today, time_out=None).order_by('-time_in').first()
                student.today_time_card = TimeCard.objects.filter(
                    student_assignment=assignment, student=student,
                    time_in__date=today, time_out__date=today
                )

            context['assignment'] = assignment
        else:
            context['assignment'] = None

        quarter = get_object_or_404(Quarter, pk=quarter_id)
        context['quarter'] =quarter
        return context

    def form_valid(self, form):
        student_id = self.request.POST['student_id']
        quarter_id = self.kwargs['quarter_id']
        department_id = self.kwargs['department_id']
        action = self.request.POST['action']

        assignment = get_object_or_404(StudentAssignment, quarter_id=quarter_id, department_id=department_id)
        student = get_object_or_404(Student, pk=student_id)

        #time_card, created = TimeCard.objects.get_or_create(student_assignment=assignment, student=student)

        if action == 'checkin':
            #time_card.time_in = timezone.now()
            time_card = TimeCard.objects.create(
                student_assignment=assignment, student=student,
                time_in=timezone.now())
        elif action == 'checkout':
            #time_card.time_out = timezone.now()
            today = timezone.now().date()
            time_card = TimeCard.objects.filter(
                student_assignment=assignment,
                student=student, time_out=None,
                time_in__date=today).order_by('-time_in').first()
            if time_card:
                time_card.time_out = timezone.now()
                time_card.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('time_card',
                       kwargs={'quarter_id': self.kwargs['quarter_id'], 'department_id': self.kwargs['department_id']})

#manual time card entry by instructor or vocational coordinator
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin','instructor', 'vocational_coordinator'])
def time_card_manual(request, quarter_id, department_id):

    try:
        model_instance = StudentAssignment.objects.get(quarter=quarter_id, department=department_id)
        students_qs = model_instance.student.all()
        got_data=True
    except StudentAssignment.DoesNotExist:
        model_instance = None
        got_data = False
        students_qs = Student.objects.none()
        messages.info(request, "No assignments found for this quarter and department.")

    department=Department.objects.get(pk=department_id)
    quarter = Quarter.objects.get(pk=quarter_id)

    local_timezone=department.school.timezone
    # Create formset
    FormSet = formset_factory(ManualTimeCardForm, formset=BaseFormSet, extra=0)

    if request.method == "POST":
        formset = FormSet(request.POST, form_kwargs={'students': students_qs, 'timezone': local_timezone})
        if formset.is_valid():
            instances = []
            for single_form in formset:
                if single_form.cleaned_data.get('time_in') is not None:
                    instance = single_form.save(commit=False)
                    instance.student_assignment = model_instance
                    instance.update_week_range()
                    instance.timezone=local_timezone
                    instances.append(instance)
            TimeCard.objects.bulk_create(instances)
            messages.success(request, "Your time entries were successfully saved.")
    else:
        if model_instance is not None:
            data = [{'student': student} for student in model_instance.student.all()]
        else:
            data=[]
        formset = FormSet(initial=data, form_kwargs={'students': students_qs, 'timezone': local_timezone})


    context = dict(formset=formset, department=department, quarter=quarter, got_data=got_data)
    return render(request, 'vocational/time_card_manual.html', context)


#manual time card entry by instructor or vocational coordinator
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin','instructor', 'vocational_coordinator'])
def time_card_edit(request, pk):
    timecard = get_object_or_404(TimeCard, pk=pk)
    local_timezone=timecard.timezone
    if request.method == "POST":
        form = TimeCardEditForm(request.POST, instance=timecard, timezone=local_timezone)
        if form.is_valid():
            form.save()
            messages.success(request, "Your changes were successfully saved.")
    else:
        form = TimeCardEditForm(instance=timecard, timezone=local_timezone)

    context = dict(form=form, timecard=timecard)
    return render(request, 'vocational/time_card_edit.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin','instructor', 'vocational_coordinator'])
def time_card_delete(request, pk):
    time_card = TimeCard.objects.get(pk=pk)
    time_card.delete()
    return redirect(request.GET.get('next', 'default_redirect_url'))

@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin','instructor', 'vocational_coordinator'])
def student_time_card_summary(request, schoolid):
    # First we need to annotate each time card with its duration in hours
    timecards = TimeCard.objects.filter(
        student__user__profile__school__id=schoolid,student__user__is_active=True,
        time_in__isnull=False,time_out__isnull=False
    ).order_by( 'student__user__last_name', 'student_assignment__department__name', 'student_assignment__quarter')

    # We're going to convert the duration in hours and also annotate it with quarter and department
    timecards = [
        {
            'student': tc.student,
            'quarter': tc.student_assignment.quarter,
            'department': tc.student_assignment.department,
            'duration': round(tc.duration()[0] + tc.duration()[1] / 60.0, 2)  # Convert to hours
        } for tc in timecards
    ]

    # Now we'll prepare the aggregate data
    aggregate_data = {}

    for tc in timecards:
        if tc['student'] not in aggregate_data:
            aggregate_data[tc['student']] = {}

        if tc['department'] not in aggregate_data[tc['student']]:
            aggregate_data[tc['student']][tc['department']] = {'total': 0, 'quarters': {}}

        if tc['quarter'] not in aggregate_data[tc['student']][tc['department']]['quarters']:
            aggregate_data[tc['student']][tc['department']]['quarters'][tc['quarter']] = 0

        # Add the hours to the quarter and to the total
        aggregate_data[tc['student']][tc['department']]['quarters'][tc['quarter']] = round(
            aggregate_data[tc['student']][tc['department']]['quarters'][tc['quarter']] + tc['duration'],
            2)

        # Increment the total duration, rounding the result
        aggregate_data[tc['student']][tc['department']]['total'] = round(
            aggregate_data[tc['student']][tc['department']]['total'] + tc['duration'],
            2)



    formatted_data = []
    for student, departments in aggregate_data.items():
        student_rowspan = 0
        formatted_departments = []
        for department, details in departments.items():
            department_rowspan = len(details['quarters'])
            student_rowspan += department_rowspan
            formatted_departments.append({
                'name': department,
                'detail': details,
                'rowspan': department_rowspan
            })
        formatted_data.append({
            'name': student,
            'departments': formatted_departments,
            'rowspan': student_rowspan
        })


#calculating times from Ethics Grades
    ethicsgrades = EthicsGradeRecord.objects.filter(
        student__user__profile__school__id=schoolid,
        student__user__is_active=True, time__gt=0,
    ).order_by('student__user__last_name', 'department__name', 'quarter')


    # We're going to annotate it with quarter and department
    ethicsgrades = [
        {
            'student': eg.student,
            'quarter': eg.quarter,
            'department': eg.department,
            'time': eg.time or 0,  # no conversion necessary for this model
        } for eg in ethicsgrades
    ]

    # Now we'll prepare the aggregate data
    aggregate_data = {}

    for eg in ethicsgrades:
        if eg['student'] not in aggregate_data:
            aggregate_data[eg['student']] = {}

        if eg['department'] not in aggregate_data[eg['student']]:
            aggregate_data[eg['student']][eg['department']] = {'total': 0, 'quarters': {}}

        if eg['quarter'] not in aggregate_data[eg['student']][eg['department']]['quarters']:
            aggregate_data[eg['student']][eg['department']]['quarters'][eg['quarter']] = 0

        # Add the hours to the quarter and total
        aggregate_data[eg['student']][eg['department']]['quarters'][eg['quarter']] = round(
            aggregate_data[eg['student']][eg['department']]['quarters'][eg['quarter']] + (eg['time'] or 0),
            2)

        # Increment the total duration, rounding the result
        aggregate_data[eg['student']][eg['department']]['total'] = round(
            aggregate_data[eg['student']][eg['department']]['total'] + (eg['time'] or 0),
            2)


    #calculate times from Ethics Grades (entered weekly times)
    formatted_data_ethicsgrades = []
    for student, departments in aggregate_data.items():
        student_rowspan = 0
        formatted_departments = []
        for department, details in departments.items():
            department_rowspan = len(details['quarters'])
            student_rowspan += department_rowspan
            formatted_departments.append({
                'name': department,
                'detail': details,
                'rowspan': department_rowspan
            })
        formatted_data_ethicsgrades.append({
            'name': student,
            'departments': formatted_departments,
            'rowspan': student_rowspan
        })


    context = dict(formatted_data=formatted_data, formatted_data_ethicsgrades=formatted_data_ethicsgrades)

    return render(request, 'vocational/student_time_card_summary.html', context)


def get_student_timecards(student):
    timecards = TimeCard.objects.filter(student=student) \
        .order_by('student_assignment__quarter',
                  'student_assignment__department',
                  'week_range') \
        .select_related('student_assignment__quarter',
                        'student_assignment__department') \
        .order_by('-student_assignment__quarter',
                  '-time_in')


    return timecards


@login_required(login_url='login')
def time_card_individual_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    #timecards = get_student_timecards(student)

    timecards_queryset = TimeCard.objects.filter(student=student) \
        .order_by('-student_assignment__quarter', '-time_in') \
        .select_related('student_assignment__quarter', 'student_assignment__department')

    # Calculate `duration_in_minutes` for each timecard
    for timecard in timecards_queryset:
        timecard.duration_in_hours = timecard.duration_in_hours()

    # Group by week and calculate weekly totals
    weekly_totals = {}
    for timecard in timecards_queryset:
        week = timecard.week_range
        if week:
            # Accumulate total duration for the week
            weekly_totals[week] = weekly_totals.get(week, 0) + timecard.duration_in_hours

    context = {
        'student': student,
        'timecards': timecards_queryset,
        'weekly_totals': weekly_totals,
    }

    return render(request, 'vocational/time_card_individual_student.html', context)