from statistics import mean
from vocational.models import GradeSettings, Quarter, SchoolYear
from django.utils import timezone


def current_quarter(school_year_id):
    q = Quarter.objects.filter(start_date__lt=timezone.now()+timezone.timedelta(days=5), end_date__gt=timezone.now()+timezone.timedelta(days=5), school_year_id=school_year_id).first()
    if not q:
        q=Quarter.objects.filter(school_year_id=school_year_id).first()
    return q


def average(grades, school_year=None):
    summative = grades.filter(type="S")
    a1=[]
    for s in summative:
        a1.append(s.percent())
    if a1:
        s1=mean(a1)
    else:
        s1=None

    formative=grades.filter(type="F")
    a2 = []
    for f in formative:
        a2.append(f.percent())
    if a2:
        s2=mean(a2)
    else:
        s2=None

    if school_year==None:
        sample_grade=grades.first()
        if sample_grade:
            school_year=sample_grade.quarter.school_year

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