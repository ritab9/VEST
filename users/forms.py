from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import School, Profile, Student

class CreateUserForm(UserCreationForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1','password2' ]

class SchoolForm (ModelForm):
    class Meta:
        model = School
        fields = ['name', 'abbreviation', 'foundation']

class UserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name', 'last_name', 'email', 'username','is_active', 'groups']

class ProfileForm (forms.ModelForm):
    class Meta:
        model = Profile
        fields =['phone_number', 'school']

class StudentForm (forms.ModelForm):
    class Meta:
        model = Student
        fields =['birthday', 'graduation_year', ]
