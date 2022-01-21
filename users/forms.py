from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm

from .models import School, Profile, Student

class CreateUserForm(UserCreationForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password1','password2' ]

    widgets = {
        'first_name': forms.DateInput(
            attrs={'type': 'date', 'placeholder': 'mm/dd/yyyy', 'autofocus': '', }),
    }

class SchoolForm (ModelForm):
    class Meta:
        model = School
        fields = ['name', 'abbreviation', 'foundation']

class UserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name', 'last_name', 'email', 'username',]


class UserFormStudent(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name', 'last_name', 'email','username', 'is_active',]

class ProfileForm (forms.ModelForm):
    class Meta:
        model = Profile
        fields =['phone_number', ]

class StudentForm (forms.ModelForm):
    class Meta:
        model = Student
        fields =['gender', 'birthday', 'graduation_year', ]
        widgets = {
            'birthday': forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'mm/dd/yyyy', }),
            'graduation_year': forms.NumberInput(
                attrs={'placeholder': 'yyyy', }),
        }

class StudentParentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['parent']