
import django_filters
from django_filters import *
from django.db.models import Q

import vocational.models
from .models import StudentAssignment, EthicsGrade, Department, Quarter

class StudentAssignmentFilter(django_filters.FilterSet):
    class Meta:
        model = StudentAssignment
        fields = ['department']

class StudentFilter(django_filters.FilterSet):
    first_name = CharFilter(field_name = "user__first_name", label ="First Name")
    last_name = CharFilter(field_name="user__last_name", label="Last Name")
    graduation_year = NumberFilter(field_name="graduation_year", label="Graduation Year")

    CHOICES = (
        ('f', 'Female'),
        ('m', 'Male'),
    )
    gender = ChoiceFilter(field_name="gender", label="Gender", choices=CHOICES)





class GradeFilter(django_filters.FilterSet):
    def departments(request):
        if request is None: return Department.objects.none()
        school = request.user.profile.school
        return Department.objects.filter(school=school, is_active=True)
    def quarters(request):
        if request is None: return Quarter.objects.none()
        school = request.user.profile.school
        return Quarter.objects.filter(school_year__school=school, school_year__active=True)


    student = CharFilter(method='s_first_last_name_filter', label='Student')
    instructor = CharFilter(method='i_first_last_name_filter', label='Instructor')
    department = ModelChoiceFilter(queryset=departments)
    quarter = ModelChoiceFilter(queryset=quarters)

    class Meta:
        model= EthicsGrade
        fields = ['type']


    def s_first_last_name_filter(self, queryset, name, value):
        return queryset.filter(
            Q(student__user__first_name__icontains=value) | Q(student__user__last_name__icontains=value))

    def i_first_last_name_filter(self, queryset, name, value):
        return queryset.filter(
            Q(instructor__first_name__icontains=value) | Q(instructor__last_name__icontains=value))
