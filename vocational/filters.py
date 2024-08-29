import django_filters
from django_filters import *
from django.db.models import Q
from django.shortcuts import render
from django import forms
import vocational.models
from .models import StudentAssignment, EthicsGradeRecord, Department, Quarter
from users.models import User, Student
from users.functions import in_group
import datetime


class DateInput(forms.DateInput):
    input_type = 'date'

class StudentAssignmentFilter(django_filters.FilterSet):
    class Meta:
        model = StudentAssignment
        fields = ['department']


class StudentFilter(django_filters.FilterSet):
    first_name = CharFilter(field_name="user__first_name", label="First Name")
    last_name = CharFilter(field_name="user__last_name", label="Last Name")
    graduation_year = NumberFilter(field_name="graduation_year", label="Graduation Year")

    CHOICES = (
        ('f', 'Female'),
        ('m', 'Male'),
    )
    gender = ChoiceFilter(field_name="gender", label="Gender", choices=CHOICES)


class GradeFilterVocationalCoordinator(django_filters.FilterSet):
    def departments(request):
        if request is None: return Department.objects.none()
        school = request.user.profile.school
        return Department.objects.filter(school=school, is_active=True)

    def quarters(request):
        if request is None: return Quarter.objects.none()
        school = request.user.profile.school
        return Quarter.objects.filter(school_year__school=school, school_year__active=True).order_by('-name')

    # def instructors(request):
    #     if request is None: return User.objects.none()
    #     school = request.user.profile.school
    #     return User.objects.filter(profile__school=school, is_active=True, groups__name='instructor')

    instructor = CharFilter(method='i_first_last_name_filter', label='Instructor')
    #instructor = ModelChoiceFilter(queryset=instructors)
    department = ModelChoiceFilter(queryset=departments)
    quarter = ModelChoiceFilter(queryset=quarters)
    student = CharFilter(method='s_first_last_name_filter', label='Student')

    start_evaluation_date = DateFilter(field_name="evaluation_date", lookup_expr='gte', label='Graded after:',
                               widget=DateInput(attrs={'type': 'date', 'placeholder': 'mm/dd/yyyy'}))
    end_evaluation_date = DateFilter(field_name="evaluation_date", lookup_expr='lte', label='Graded before:',
                             widget=DateInput(attrs={'type': 'date'}))

    class Meta:
        model = EthicsGradeRecord
        fields = ['instructor', 'department', 'type', 'quarter', 'student', ]

    def s_first_last_name_filter(self, queryset, name, value):
        return queryset.filter(
            Q(student__user__first_name__icontains=value) | Q(student__user__last_name__icontains=value))

    def i_first_last_name_filter(self, queryset, name, value):
         return queryset.filter(
             Q(instructor__first_name__icontains=value) | Q(instructor__last_name__icontains=value))


class GradeFilterInstructor(django_filters.FilterSet):
    def departments(request):
        if request is None: return Department.objects.none()
        school = request.user.profile.school
        return Department.objects.filter(school=school, is_active=True)

    def quarters(request):
        if request is None: return Quarter.objects.none()
        school = request.user.profile.school
        return Quarter.objects.filter(school_year__school=school, school_year__active=True).order_by('-name')

    department = ModelChoiceFilter(queryset=departments)
    quarter = ModelChoiceFilter(queryset=quarters)
    student = CharFilter(method='s_first_last_name_filter', label='Student')

    class Meta:
        model = EthicsGradeRecord
        fields = ['department', 'type', 'quarter', 'student']

    def s_first_last_name_filter(self, queryset, name, value):
        return queryset.filter(
            Q(student__user__first_name__icontains=value) | Q(student__user__last_name__icontains=value))

    # def i_first_last_name_filter(self, queryset, name, value):
    #     return queryset.filter(
    #         Q(instructor__first_name__icontains=value) | Q(instructor__last_name__icontains=value))


class GradeFilterStudentParent(django_filters.FilterSet):
#ToDo: Parent filtering is clunky (add all departments from a school, and only current school-year's quarters)
    def departments(self):
        if self is None: return Department.objects.none()
        if in_group(self.user, 'student'):
            departments = StudentAssignment.objects.values_list('department').filter(student__user=self.user)
        else:
            departments = Department.objects.filter(school=self.user.profile.school)
        return Department.objects.filter(id__in=departments)

    def quarters(self):
        if self is None: return Quarter.objects.none()
        if in_group(self.user, 'student'):
            quarters = StudentAssignment.objects.values_list('quarter').filter(student__user=self.user)
        else:
            quarters= Quarter.objects.filter(school_year__school=self.user.profile.school, school_year__active=True)
        return Quarter.objects.filter(id__in=quarters).order_by('-name')

    department = ModelChoiceFilter(queryset=departments)
    quarter = ModelChoiceFilter(queryset=quarters)

    class Meta:
        model = EthicsGradeRecord
        fields = ['department', 'type', 'quarter', ]


class TimeCardFilterForm(forms.Form):
    department = forms.ModelChoiceField(queryset=Department.objects.none(), required=False)
    quarter = forms.ModelChoiceField(queryset=Quarter.objects.none(), required=False)
    from_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    to_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    student = forms.ModelChoiceField(queryset=Student.objects.none(), required=False)

    def __init__(self, *args, department_qs=None, quarter_qs=None, student_qs=None, **kwargs):
        super().__init__(*args, **kwargs)
        if department_qs is not None:
            self.fields['department'].queryset = department_qs
        if quarter_qs is not None:
            self.fields['quarter'].queryset = quarter_qs
        if student_qs is not None:
            self.fields['student'].queryset = student_qs

        #today = datetime.date.today()
        #last_week = today - datetime.timedelta(days=7)
        #self.fields['from_date'].initial = last_week
        #self.fields['to_date'].initial = today