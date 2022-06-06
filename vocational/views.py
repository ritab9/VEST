from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from users.decorators import allowed_users
from .models import *
from .forms import *
from .filters import *



# School Admin Views
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

    if request.method == "POST":
        quarter_formset = QuarterFormSet(request.POST, instance=schoolyear)
        if quarter_formset.is_valid():
            quarter_formset.save()
            return redirect('school_year', schoolid)
    else:
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
    SkillFormSet = inlineformset_factory(Department, VocationalSkill, fields=('name', 'description', 'level', 'code'),
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
        '-quarter__school_year', '-quarter__name')
    quarter = Quarter.objects.filter(id__in=studentassignment.values_list('quarter', flat=True))

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

    if request.method == "POST":
        student_formset = StudentAssignmentFormSet(request.POST, instance=quarter, form_kwargs={'school': school})
        if student_formset.is_valid():
            student_formset.save()
            if request.POST.get("add"):
                return redirect('manage_student_assignment', schoolid)
            return redirect('student_assignment', schoolid)

    else:
        student_formset = StudentAssignmentFormSet(instance=quarter, initial=[{'school': school, }],
                                                   form_kwargs={'school': school})

    context = dict(student_formset=student_formset, quarter=quarter)
    return render(request, 'vocational/manage_student_assignment.html', context)


# Manage Grades
@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'instructor'])
def grade_list(request, schoolid):
    grades = EthicsGrade.objects.filter(quarter__school_year__school__id=schoolid, instructor_id=request.user.id)

    filter = GradeFilter(request.GET, request=request, queryset=grades)
    grades = filter.qs

    context = dict(grades=grades, schoolid=schoolid, filter=filter)
    return render(request, 'vocational/grade_list.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'instructor'])
def initiate_grade_entry(request, schoolid):
    if request.method == 'POST':
        deparmentid = request.POST.get('department')
        quarterid = request.POST.get('quarter')
        type = request.POST.get('type')
        return redirect('add_grade', quarterid, type, deparmentid, request.user.id)

    assignments = InstructorAssignment.objects.filter(instructor__id=request.user.id)
    department = Department.objects.filter(school__id=schoolid, is_active=True, instructorassignment__in=assignments)

    # quarter_with_grades = Quarter.objects.filter(id__in=grades.values_list('quarter', flat=True))
    # new_quarter = Quarter.objects.filter(school_year__school_id=schoolid, school_year__active=True).exclude(
    #    id__in=grades.values_list('quarter', flat=True)).order_by('name
    active_quarter = Quarter.objects.filter(school_year__school_id=schoolid, school_year__active=True).order_by('name')
    print(active_quarter)
    context = dict(active_quarter=active_quarter, department=department)
    return render(request, 'vocational/initiate_grade_entry.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['isei_admin', 'vocational_coordinator', 'instructor'])
def add_grade(request, quarterid, type, departmentid, instructorid):
    quarter = Quarter.objects.get(id=quarterid)
    instructor = User.objects.get(id=instructorid)
    department = Department.objects.get(id=departmentid)
    student = Student.objects.filter(student_assignment__department=department, student_assignment__quarter= quarter)
    grade = EthicsGrade()
    grade.quarter = quarter
    grade.instructor = instructor
    grade.department = department
    grade.type = type
    grade_form = EthicsGradeInstructorForm(instance=grade)
    grade_form.fields["student"].queryset = student

    if request.method == "POST":
        grade_form = EthicsGradeInstructorForm(request.POST, instance=grade)
        if grade_form.is_valid():
            grade = grade_form.save()
            return redirect('finalize_grade', grade.id)
        else:
            print("Not valid")

    grades=EthicsGrade.objects.filter()

    context = dict(grade_form=grade_form, grade=grade)
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
    grade = EthicsGrade.objects.get(id=gradeid)

    if request.method == "POST":
        if grade.type == "S":
            indicator_form = IndicatorSummativeGradeFormSet(request.POST, instance=grade)
        else:
            indicator_form = IndicatorFormativeGradeFormSet(request.POST, instance=grade)
            comments_form = FormativeCommentsForm(request.POST)
            if comments_form.is_valid():
                com= comments_form.cleaned_data["commendation"]
                recom = comments_form.cleaned_data["recommendation"]
                grade.commendation = com
                grade.recommendation = recom
                grade.save()

        if indicator_form.is_valid():
            indicator_form.save()
            return redirect('add_grade', grade.quarter.id, grade.type, grade.department.id, grade.instructor.id)
        else:
            print(indicator_form.errors)
            print("Not valid")


    indicator = EthicsIndicator.objects.filter(level= grade.level)
    if grade.type=="S":
        if not IndicatorSummativeGrade.objects.filter(grade=grade):
            for i in indicator:
                IndicatorSummativeGrade(indicator=i, grade=grade).save()
        indicator_formset = IndicatorSummativeGradeFormSet(instance=grade)

    else:
        if not IndicatorFormativeGrade.objects.filter(grade=grade):
            for i in indicator:
               IndicatorFormativeGrade(indicator=i, grade=grade).save()
        indicator_formset = IndicatorFormativeGradeFormSet(instance=grade)

    formative_comments_form = FormativeCommentsForm()

    context = dict(grade=grade, indicator_formset = indicator_formset,
                   formative_comments_form = formative_comments_form)
    return render(request, 'vocational/finalize_grade.html', context)