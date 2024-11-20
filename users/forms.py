from django import forms
from django.forms import ModelForm, PasswordInput
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm

from .models import School, Profile, Student
from vocational.models import EthicsLevel, VocationalStatus

class CreateUserForm(ModelForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username',]

class SchoolForm(ModelForm):
    class Meta:
        model = School
        fields = ['name', 'abbreviation', 'email_address', 'country', 'phone_number', 'timezone' ]

class EmailSettingsForm(ModelForm):
    class Meta:
        model=School
        fields = ["email_address", "email_password"]
        widgets = {
            'email_password': PasswordInput(),
        }

class UserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name', 'last_name', 'email', 'username']


class UserFormStudent(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name', 'last_name', 'email','username', 'is_active',]

class ProfileForm (forms.ModelForm):
    class Meta:
        model = Profile
        fields =['phone_number', ]

class StudentForm (forms.ModelForm):
    vocational_level = forms.ModelChoiceField(queryset=EthicsLevel.objects.all().order_by('name'), required=False)
    class Meta:
        model = Student
        fields =['gender', 'birthday', 'graduation_year', 'vocational_level' ]
        widgets = {
            'birthday': forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'mm/dd/yyyy', }),
            'graduation_year': forms.NumberInput(
                attrs={'placeholder': 'yyyy', }),
        }

    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        # For an update form, set the initial value from related student's VocationalStatus.
        if kwargs.get('instance'):
            student_instance = kwargs.get('instance')
            try:
                self.fields['vocational_level'].initial = student_instance.vocationalstatus.vocational_level
            except VocationalStatus.DoesNotExist:
                # Handle the case where Student does not have associated VocationalStatus
                self.fields['vocational_level'].initial = EthicsLevel.objects.get(name='Level 1')
                pass

class StudentParentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['parent']