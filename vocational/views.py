from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from users.decorators import allowed_users
from users.functions import in_group
from .functions import *
from .models import *
from .forms import *
from .filters import *
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib import messages

now=timezone.now()



# School Admin Views
# School Settings
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def school_settings(request, schoolid):
    school_year = SchoolYear.objects.filter(school__id=schoolid, active=True).first()

    school_settings = SchoolSettings.objects.filter(school_year=school_year).first()
    if not school_settings:
        school_settings = SchoolSettings()
        school_settings.school_year=school_year
        school_settings.save()

    if request.method == "POST":
        s_form = SchoolSettingsForm(request.POST, instance=school_settings)
        if s_form.is_valid():
            s_form.save()
            messages.info(request, 'Changes have been saved!')
            return redirect('school_settings', schoolid)
    else:
        s_form = SchoolSettingsForm(instance=school_settings)

    arr = []
    for a in SchoolSettings.objects.filter(school_year__school_id=schoolid):
        a_info = [a.school_year, a.progress_ratio, a.summative_ratio, a.track_time, a.get_time_unit_display()]
        arr.append(a_info)

    context = dict(school_year=school_year, schoolid=schoolid,
                   s_form=s_form, arr=arr)
    return render(request, 'vocational/school_settings.html', context)

# School Year
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def school_year(request, schoolid):
    schoolyear = SchoolYear.objects.filter(school__id=schoolid)
    # current_year = school_year.get()
    context = dict(school_year=schoolyear, schoolid=schoolid)
    return render(request, 'vocational/school_year.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'school_admin'])
def add_school_year(request, schoolid):
    if request.method == "POST":
        form = SchoolYearForm(request.POST)
        if form.is_valid():
            schoolyear = form.save(commit=False)
            schoolyear.school = School.objects.get(id=schoolid)
            schoolyear.active = True
            schoolyear.save()
            return redirect('manage_school_year', schoolid, schoolyear.id)
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
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator'])
def manage_skill(request, departmentid):
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
            return redirect('skill_list', schoolid)
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
        instructor_formset = InstructorAssignmentFormSet(request.POST, form_kwargs={'school': school})
        if instructor_formset.is_valid():
            instructor_formset.save()
            if request.POST.get("add"):
                return redirect('manage_instructor_assignment', schoolid)
            return redirect('instructor_assignment', schoolid)

    else:
        instructor_formset = InstructorAssignmentFormSet(initial=[{'department__school': school}],
                                                         form_kwargs={'school': school})

    context = dict(instructor_formset=instructor_formset)
    return render(request, 'vocational/manage_instructor_assignment.html', context)


# Student Assignment to vocational areas
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator'])
def student_assignment(request, schoolid):
    studentassignment = StudentAssignment.objects.filter(department__school__id=schoolid).order_by(
        'quarter__school_year', '-quarter__name')
    quarter = Quarter.objects.filter(id__in=studentassignment.values_list('quarter', flat=True)).order_by('-name')

    new_quarter = Quarter.objects.filter(school_year__school_id=schoolid, school_year__active=True).exclude(
        id__in=studentassignment.values_list('quarter', flat=True)).order_by('-school_year', 'name')

    context = dict(student_assignment=studentassignment,
                   quarter=quarter, new_quarter=new_quarter,
                   schoolid=schoolid)
    return render(request, 'vocational/student_assignment.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator'])
def student_assignment_student_filter(request, schoolid):
    studentassignment = StudentAssignment.objects.filter(department__school__id=schoolid).order_by(
        '-quarter__school_year', '-quarter__name')
    student = Student.objects.filter(id__in=studentassignment.values_list('student', flat=True))

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
    studentassignment = StudentAssignment.objects.filter(department__school__id=schoolid).order_by('department')
    department_filter = StudentAssignmentFilter(request.GET, queryset=studentassignment)
    studentassignment = department_filter.qs

    department = Department.objects.filter(id__in=studentassignment.values_list('department', flat=True))

    new_quarter = Quarter.objects.filter(school_year__school_id=schoolid, school_year__active=True).exclude(
        id__in=studentassignment.values_list('quarter', flat=True)).order_by('name')

    context = dict(department=department, schoolid=schoolid, new_quarter=new_quarter,
                   department_filter=department_filter)
    return render(request, 'vocational/student_assignment_department_filter.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator'])
def manage_student_assignment(request, schoolid, quarterid):
    school = School.objects.get(id=schoolid)
    quarter = Quarter.objects.get(id=quarterid)

    # students = Student.objects.filter(user__profile__school=school, user__is_active=True)
    # student_filter = StudentFilter(request.GET, queryset=students)
    # students = student_filter.qs

    if request.method == "POST":
        student_formset = StudentAssignmentFormSet(request.POST, instance=quarter, form_kwargs={'school': school,})
        if student_formset.is_valid():
            student_formset.save()
            if request.POST.get("add"):
                return redirect('manage_student_assignment', schoolid, quarterid)
            return redirect('student_assignment', schoolid)

    else:
        student_formset = StudentAssignmentFormSet(instance=quarter, initial=[{'school': school }],
                                                   form_kwargs={'school': school})

    context = dict(student_formset=student_formset, quarter=quarter)
    return render(request, 'vocational/manage_student_assignment.html', context)



# Manage Grades
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'instructor'])
def grade_list(request, userid):
    user = User.objects.get(id=userid)
    if in_group(user,"vocational_coordinator"):
        grades = EthicsGradeRecord.objects.filter(quarter__school_year__school__id=user.profile.school.id).order_by('-vc_validated','-student_discussed','-evaluation_date','student')
        filter = GradeFilterVocationalCoordinator(request.GET, request=request, queryset=grades)
    else:
        grades = EthicsGradeRecord.objects.filter(instructor_id=userid).order_by('-evaluation_date','student')
        filter = GradeFilterInstructor(request.GET, request=request, queryset=grades)

    for obj in grades:
        if (obj.score() == 0 and obj.created_at + timedelta(days=1) < now):
            obj.delete()

    grades = filter.qs

    context = dict(grades=grades, filter=filter)
    return render(request, 'vocational/grade_list.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'instructor'])
def initiate_grade_entry(request, schoolid):
    if request.method == 'POST':
        departmentid = request.POST.get('department')
        quarterid = request.POST.get('quarter')
        type = request.POST.get('type')
        evaluation_date = request.POST.get('date')
        if type=="K":
            return redirect('add_skill_grade', quarterid, departmentid, evaluation_date, request.user.id)
        else:
            return redirect('add_grade', quarterid, type, departmentid, evaluation_date, request.user.id)

    assignments = InstructorAssignment.objects.filter(instructor__id=request.user.id)
    department = Department.objects.filter(school__id=schoolid, is_active=True, instructorassignment__in=assignments)

    # quarter_with_grades = Quarter.objects.filter(id__in=grades.values_list('quarter', flat=True))
    # new_quarter = Quarter.objects.filter(school_year__school_id=schoolid, school_year__active=True).exclude(
    #    id__in=grades.values_list('quarter', flat=True)).order_by('name
    active_quarter = Quarter.objects.filter(school_year__school_id=schoolid, school_year__active=True).order_by('name')

    context = dict(active_quarter=active_quarter, department=department)
    return render(request, 'vocational/initiate_grade_entry.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'instructor'])
def add_grade(request, quarterid, type, departmentid, evaluation_date, instructorid):

    quarter = Quarter.objects.get(id=quarterid)
    instructor = User.objects.get(id=instructorid)
    department = Department.objects.get(id=departmentid)
    student = Student.objects.filter(student_assignment__department=department, student_assignment__quarter= quarter)
    grade = EthicsGradeRecord()
    grade.quarter = quarter
    grade.evaluation_date = datetime.strptime(evaluation_date, '%Y-%m-%d').date()
    grade.instructor = instructor
    grade.department = department
    grade.type = type
    grade_form = EthicsGradeInstructorForm(instance=grade)
    grade_form.fields["student"].queryset = student

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

    context = dict(grade_form=grade_form, grade=grade)
    return render(request, 'vocational/add_grade.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'instructor'])
def add_skill_grade(request, quarterid, date, departmentid, instructorid):
    quarter = Quarter.objects.get(id=quarterid)
    instructor = User.objects.get(id=instructorid)
    department = Department.objects.get(id=departmentid)
    student = Student.objects.filter(student_assignment__department=department, student_assignment__quarter= quarter)
    grade = SkillGradeRecord()
    grade.quarter = quarter
    grade.instructor = instructor
    grade.department = department
    grade.date=date
    grade_form = SkillGradeInstructorForm(instance=grade)
    grade_form.fields["student"].queryset = student

    if request.method == "POST":
        grade_form = SkillGradeInstructorForm(request.POST, instance=grade)
        if grade_form.is_valid():
            grade = grade_form.save()
            return redirect('finalize_skill_grade', grade.id)
        else:
            print("Not valid")

    #grades = SkillGradeRecord.objects.filter()

    context = dict( grade_form=grade_form, grade=grade)
    return render(request, 'vocational/add_skill_grade.html', context)



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

    if request.method == "POST":
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

        if ethic_form.is_valid():
            ethic_form.save()
            if request.POST.get("save_c"):
                return redirect('add_grade', grade.quarter.id, grade.type, grade.department.id, grade.evaluation_date, grade.instructor.id)
            if request.POST.get("save_r"):
                return redirect('grade_list', grade.instructor.id )
        else:
            print(ethic_form.errors)

    if request.method == "GET" and request.GET.get("delete"):
        grade.delete()
        return redirect('add_grade', grade.quarter.id, grade.type, grade.department.id, grade.evaluation_date,
                        grade.instructor.id)

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

    context = dict(grade=grade, ethic_formset = ethic_formset,
                   formative_comments_form = formative_comments_form,
                   student_discussion_form = student_discussion_form)
    return render(request, 'vocational/finalize_grade.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'instructor'])
def finalize_skill_grade(request, gradeid):
    grade = SkillGradeRecord.objects.get(id=gradeid)

    if request.method == "POST":

        skill_form = SkillGradeFormSet(request.POST, instance=grade)
        if skill_form.is_valid():
            skill_form.save()
            return redirect('add_skill_grade', grade.quarter.id, grade.department.id, grade.instructor.id)
        else:
            print(skill_form.errors)

    skill = VocationalSkill.objects.filter()
    if not SkillGrade.objects.filter(grade=grade):
        for s in skill:
               SkillGrade(skill=s, grade=grade).save()
    skill_formset = SkillGradeFormSet(instance=grade)

    #formative_comments_form = FormativeCommentsForm()

    context = dict(grade=grade, skill_formset = skill_formset,)
                   #formative_comments_form = formative_comments_form)
    return render(request, 'vocational/finalize_skill_grade.html', context)



@login_required(login_url='login')
@allowed_users(allowed_roles=['vocational_coordinator'])
def vc_validate_grades(request, schoolid):

    i_grades=EthicsGradeRecord.objects.filter(vc_validated=None, instructor__profile__school__id=schoolid)

    if request.method == 'POST':
        formset = VCValidationFormSet(request.POST)
        if formset.is_valid():
            formset.save()
    else:
        formset = VCValidationFormSet(queryset=i_grades)

    context = dict(formset=formset)
    return render(request, 'vocational/vc_validate_grades.html', context)


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
        grades=EthicsGradeRecord.objects.filter(student=student, department=a.department, quarter=a.quarter)
        avg=average(grades, a.quarter.school_year)
        if grades.last():
            level=grades.last().level
        else:
            level=None
        a_info = [a.quarter.school_year, a.quarter.get_name_display, a.department, avg, level]
        arr.append(a_info)


    context=dict(student=student, arr=arr)
    return render(request, 'vocational/student_vocational_info.html', context)


#parent views
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'parent'])
def parent_page(request, parentid):
    children = Student.objects.filter(parent__id=parentid)


    context=dict(children=children)
    return render(request, 'vocational/parent_page.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'parent', 'student'])
def student_grades(request, studentid):

    grades = EthicsGradeRecord.objects.filter(student_id=studentid, vc_validated__isnull=False).order_by('-evaluation_date')
    student=Student.objects.filter(id=studentid).first()
    filter = GradeFilterStudentParent(request.GET, request=request, queryset=grades)

    for obj in grades:
        if (obj.score() == 0 and obj.created_at + timedelta(days=1) < now):
            obj.delete()

    grades = filter.qs

    context = dict(student=student, grades=grades, filter=filter)
    return render(request, 'vocational/student_grades.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'student'])
def student_page(request, studentid):
    student = Student.objects.get(user__id=studentid)

    context=dict(student=student)
    return render(request, 'vocational/student_page.html', context)