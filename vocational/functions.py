from statistics import mean
from vocational.models import GradeSettings, EthicsGradeRecord, Quarter, SchoolYear
from users.models import Student
from django.utils import timezone
from django.db.models import Prefetch


def current_quarter(school_year_id):
    q = Quarter.objects.filter(start_date__lt=timezone.now()+timezone.timedelta(days=5), end_date__gt=timezone.now()+timezone.timedelta(days=5), school_year_id=school_year_id).first()
    if not q:
        q=Quarter.objects.filter(school_year_id=school_year_id).first()
    return q

#calculates summative and formative grades average for a given set of numbers, and school year
def average(grades, school_year=None):

    if school_year==None:
        sample_grade=grades.first()
        if sample_grade:
            school_year=sample_grade.quarter.school_year

    try:
        grade_settings = GradeSettings.objects.filter(school_year_id=school_year).first()
        time = grade_settings.track_time if grade_settings else False
    except:
        time = False


    summative = grades.filter(type="S")
    if time:
        summative_percent_time_pairs = [(s.percent(), s.time) for s in summative if s.time is not None]
        if summative_percent_time_pairs:
            s1 = sum(percent * float(time) for percent, time in summative_percent_time_pairs) / sum(
                float(time) for _, time in summative_percent_time_pairs)
        else:
            s1 = None
    else:
        a1=[]
        for s in summative:
            a1.append(s.percent())
        if a1:
            s1=mean(a1)
        else:
            s1=None

    formative=grades.filter(type="F")
    if time:
        formative_percent_time_pairs = [(f.percent(), f.time) for f in formative if f.time is not None]
        if formative_percent_time_pairs:
            s2 = sum(percent * float(time) for percent, time in formative_percent_time_pairs) / sum(
                float(time) for _, time in formative_percent_time_pairs)
        else:
            s2 = None
    else:
        a2 = []
        for f in formative:
            a2.append(f.percent())
        if a2:
            s2=mean(a2)
        else:
            s2=None



   #Default settings 80% Summative and 20% Formative
    settings=GradeSettings.objects.filter(school_year=school_year).first()
    if s1 and s2:
        if settings:
            sr = settings.summative_ratio
            fr = settings.progress_ratio
            a=round((s1*sr+s2*fr)/100,2)
        else:
            a=round(s1*0.8+s2*0.2,2)
    elif s1: a=round(s1,2)
    elif s2: a=round(s2,2)
    else:
        a=None

    return a

class DepartmentSummary:
    def __init__(self, department, average, department_time):
        self.department = department
        self.average = average
        self.department_time = department_time
class StudentSummary:
    def __init__(self, student, department_summaries, total_time, total_average):
        self.student = student
        self.department_summaries = department_summaries
        self.total_time = total_time
        self.total_average =total_average

def calculate_quarter_averages(school, quarter):
    # Get all users (profiles) related to the school
    profiles = school.profile_set.filter(user__is_active=True)

    # Extract the user from each profile (this gives us a list of users)
    users = [profile.user for profile in profiles]

    # Get all students related to these users
    students = Student.objects.filter(user__in=users)

    students = students.prefetch_related(
        Prefetch(
            'ethicsgraderecord_set',
            queryset=EthicsGradeRecord.objects.filter(quarter=quarter, vc_validated__isnull=False),
            to_attr='grades_for_quarter'
        )
    )

    student_summaries=[]

    for student in students:
        student_grades = EthicsGradeRecord.objects.filter(id__in=[grade.id for grade in student.grades_for_quarter])

        if not student_grades.exists():
            continue

        student_averages = {}
        student_total_time = {}
        for grade in student_grades:
            department = grade.department
            if department not in student_averages:
                student_averages[department] = EthicsGradeRecord.objects.none()
            if department not in student_total_time:
                student_total_time[department] = 0

            # Add a grade to the department query set for the student
            student_averages[department] |= EthicsGradeRecord.objects.filter(id=grade.id)
            student_total_time[department] += grade.time or 0

        department_summaries = []
        total_time =0
        total_weighted_sum = 0
        time=True

        for department, grades in student_averages.items():
            department_average = average(grades)
            department_time = student_total_time[department]

            department_summary = DepartmentSummary(department, department_average, department_time)
            department_summaries.append(department_summary)

            total_time += department_time
            if department_time > 0:
                total_weighted_sum += department_average * float(department_time)
            else:
                time=False

        if time and total_time > 0:
            weighted_average = total_weighted_sum / float(total_time)
            total_average = round(weighted_average,2)
        else:
            count = len(student_averages.items())
            filtered_averages = (average(grades) for grades in student_averages.values() if average(grades) is not None)
            straight_average = sum(filtered_averages) / count if count else 0
            #straight_average = sum([average(grades) for grades in student_averages.values()]) / count if count else 0
            total_average = round(straight_average,2)

        student_summary = StudentSummary(student, department_summaries, total_time, total_average)
        student_summaries.append(student_summary)

    return student_summaries
