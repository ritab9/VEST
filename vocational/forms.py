from django import forms
from django.forms import ModelForm
from django.forms.models import inlineformset_factory, modelformset_factory

from django.contrib.auth.models import User
from .models import *


class SchoolYearForm(forms.ModelForm):
    class Meta:
        model = SchoolYear
        fields = ('name', 'start_date', 'end_date')
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'placeholder': "mm/dd/yyyy"}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'placeholder': "mm/dd/yyyy"})
        }


class QuarterForm(forms.ModelForm):
    class Meta:
        model = Quarter
        fields = ('name', 'start_date', 'end_date')
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'placeholder': "mm/dd/yyyy"}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'placeholder': "mm/dd/yyyy"})
        }


QuarterFormSet = inlineformset_factory(SchoolYear, Quarter, form=QuarterForm,
                                       extra=4, max_num=4, can_delete=True)


class InstructorAssignmentForm(forms.ModelForm):
    def __init__(self, school, *args, **kwargs):
        super(InstructorAssignmentForm, self).__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.filter(school= school, is_active=True)
        self.fields['instructor'].queryset = User.objects.filter(profile__school= school, groups__name='instructor')

    class Meta:
        model = InstructorAssignment
        fields = ('department', 'instructor')

    instructor = forms.ModelMultipleChoiceField(queryset=None, widget=forms.CheckboxSelectMultiple)


InstructorAssignmentFormSet = modelformset_factory(InstructorAssignment, form=InstructorAssignmentForm,
                                                   can_delete= True, can_order=True, extra=5)


class StudentAssignmentForm(forms.ModelForm):
    def __init__(self, school, *args, **kwargs):
        super(StudentAssignmentForm, self).__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.filter(school= school, is_active=True)
        self.fields['student'].queryset = Student.objects.filter(user__profile__school= school, user__is_active= True)

    class Meta:
        model = StudentAssignment
        fields = ('department', 'student', )


    student = forms.ModelMultipleChoiceField(queryset=None, widget=forms.CheckboxSelectMultiple)


StudentAssignmentFormSet = inlineformset_factory(Quarter, StudentAssignment, form=StudentAssignmentForm,
                                                   can_delete= True, can_order=True, extra=5)

class EthicsGradeInstructorForm(forms.ModelForm):
    class Meta:
        model = EthicsGrade
        fields = ('student','level')

class IndicatorSummativeGradeForm(forms.ModelForm):
    class Meta:
        model = IndicatorSummativeGrade
        fields = ('value', 'comment')
        widgets = {
            'value':forms.Textarea(attrs={'rows':1, 'cols':3}),
            'comment': forms.Textarea(attrs={'rows': 1, 'cols': 45})

        }

IndicatorSummativeGradeFormSet = inlineformset_factory(EthicsGrade, IndicatorSummativeGrade, form = IndicatorSummativeGradeForm, extra=0, max_num = 10)

class IndicatorFormativeGradeForm(forms.ModelForm):
    class Meta:
        model = IndicatorFormativeGrade
        fields = ('value',)

IndicatorFormativeGradeFormSet = inlineformset_factory(EthicsGrade, IndicatorFormativeGrade, form = IndicatorFormativeGradeForm, extra=10, max_num = 10)

class FormativeCommentsForm(forms.Form):
    commendation = forms.CharField(widget=forms.Textarea(attrs={'rows': 6, 'cols': 30}))
    recommendation = forms.CharField(widget=forms.Textarea(attrs={'rows': 6, 'cols': 30}))

class SkillGradeInstructorForm(forms.ModelForm):
    class Meta:
        model = SkillGrade
        fields = ('student','level')

class IndicatorSkillGradeForm(forms.ModelForm):
    class Meta:
        model = IndicatorSkillGrade
        fields = ('value',)
        widgets = {
            'value':forms.Textarea(attrs={'rows':1, 'cols':3}),
        }

IndicatorSkillGradeFormSet = inlineformset_factory(SkillGrade, IndicatorSkillGrade, form = IndicatorSkillGradeForm, extra=10)
