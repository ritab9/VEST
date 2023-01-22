from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import IntegrityError
import datetime
from users.decorators import allowed_users
from users.functions import in_group
from .functions import *
from .models import *
from .forms import *
from .filters import *
from datetime import datetime, timedelta, date
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponseRedirect
from emailing.functions import send_default_email_from_school
now=timezone.now()



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
    studentassignment = StudentAssignment.objects.filter(department__school__id=schoolid, quarter__school_year__active=True).order_by(
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

    if years_to_grad:
        graduation_year = []
        now_year = date.today().year
        if date.today().month < 7:
            for g in years_to_grad:
                g_y = int(now_year) + int(g) - 1
                graduation_year.append(g_y)
        else:
            for g in years_to_grad:
                g_y = int(now_year) + int(g)
                graduation_year.append(g_y)
    else:
        graduation_year = None

    if request.method == "POST" and request.POST.get("save"):
        student_formset = StudentAssignmentFormSet(request.POST, instance=quarter, form_kwargs={'school': school,})
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
        grades = EthicsGradeRecord.objects.filter(quarter__school_year=current_year).order_by('-vc_validated','-evaluation_date','student')
        filter = GradeFilterVocationalCoordinator(request.GET, request=request, queryset=grades)
        student_assignment = StudentAssignment.objects.filter(quarter__in =quarter).order_by("quarter")
    else:
        grades = EthicsGradeRecord.objects.filter(instructor_id=userid, quarter__school_year=current_year).order_by('-evaluation_date','student')
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
    if request.method == 'POST':
        departmentid = request.POST.get('department')
        quarterid = request.POST.get('quarter')
        type = request.POST.get('type')
        evaluation_date = request.POST.get('date')
        if type=="K":
            return redirect('add_skill_grade', quarterid, departmentid, evaluation_date, request.user.id)
        else:
            return redirect('add_grade', quarterid, type, departmentid, evaluation_date, request.user.id)

    assignments = InstructorAssignment.objects.filter(instructor__id=request.user.profile.id)
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



    context = dict(active_quarter=active_quarter, department=department, current_quarter_id=current_quarter_id)
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

        if ethic_form.is_valid():
            ethic_form.save()
            if request.POST.get("save_c"):
                return redirect('add_grade', grade.quarter.id, grade.type, grade.department.id, grade.evaluation_date, grade.instructor.id)
            if request.POST.get("save_r"):
                return redirect('grade_list', grade.instructor.id )
        else:
            print(ethic_form.errors)

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
                   time_form=time_form)
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

    i_grades=EthicsGradeRecord.objects.filter(vc_validated=None, instructor__profile__school__id=schoolid).order_by("-evaluation_date")
    school = School.objects.get(id=schoolid)
    if request.method == 'POST':#
        formset = VCValidationFormSet(request.POST)
        if formset.is_valid():
            grades = formset.save()
            for g in grades:
                if g.vc_validated:
                    send_default_email_from_school(request, g.student.user,school,"GradePostedStudentMessage")
                    for p in g.student.parent.all():
                        send_default_email_from_school(request, p, school, "GradePostedParentMessage", g.student)

            return redirect('grade_list', request.user.id)
    else:
        formset = VCValidationFormSet(queryset=i_grades)

    context = dict(formset=formset)
    return render(request, 'vocational/vc_validate_grades.html', context)


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
@allowed_users(allowed_roles=['isei_admin', 'parent', 'student'])
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
@allowed_users(allowed_roles=['isei_admin', 'student'])
def student_page(request, studentid):
    student = Student.objects.get(user__id=studentid)

    context=dict(student=student)
    return render(request, 'vocational/student_page.html', context)