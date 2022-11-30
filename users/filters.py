import django_filters
from django_filters import *
from .models import Student, User

class StudentFilter(django_filters.FilterSet):
    first_name = CharFilter(field_name = "user__first_name", label ="First Name")
    last_name = CharFilter(field_name="user__last_name", label="Last Name")
    class Meta:
        model = Student
        fields = ['gender', 'graduation_year', ]

class StudentUserFilter(django_filters.FilterSet):
    graduation_year = NumberFilter(field_name="student__graduation_year", label="Graduation Year")

    class Meta:
        model = User
        fields = ['first_name', 'last_name']

    CHOICES = (
        ('f', 'Female'),
        ('m', 'Male'),
    )
    gender = ChoiceFilter(field_name="student__gender", label="Gender", choices= CHOICES)

