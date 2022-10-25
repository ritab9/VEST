from django import forms
from django.forms import ModelForm
from django.forms.models import inlineformset_factory, modelformset_factory

from django.contrib.auth.models import User
from .models import *
import datetime


class SchoolSettingsForm(forms.ModelForm):
    class Meta:
        model=SchoolSettings
        fields = ('progress_ratio', 'summative_ratio', 'track_time','time_unit')



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
        self.fields['department'].queryset = Department.objects.filter(school=school, is_active=True)
        self.fields['instructor'].queryset = User.objects.filter(profile__school=school, groups__name='instructor')

    class Meta:
        model = InstructorAssignment
        fields = ('department', 'instructor')

    instructor = forms.ModelMultipleChoiceField(queryset=None, widget=forms.CheckboxSelectMultiple)


InstructorAssignmentFormSet = modelformset_factory(InstructorAssignment, form=InstructorAssignmentForm,
                                                   can_delete=True, can_order=True, extra=5)


class StudentAssignmentForm(forms.ModelForm):
    def __init__(self, school, *args, **kwargs):
        super(StudentAssignmentForm, self).__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.filter(school=school, is_active=True)
        self.fields['student'].queryset = Student.objects.filter(user__profile__school=school,
                                                                 user__is_active=True).order_by('graduation_year')

    class Meta:
        model = StudentAssignment
        fields = ('department', 'student',)

    student = forms.ModelMultipleChoiceField(queryset=None, widget=forms.CheckboxSelectMultiple)


StudentAssignmentFormSet = inlineformset_factory(Quarter, StudentAssignment, form=StudentAssignmentForm,
                                                 can_delete=True, can_order=True, extra=2)


class EthicsGradeInstructorForm(forms.ModelForm):
    class Meta:
        model = EthicsGradeRecord
        fields = ('student', 'level',)
        widgets = {
            'level': forms.Textarea(attrs={'readonly': True, 'rows': 1, 'cols': 2}),
        }


class EthicsSummativeGradeForm(forms.ModelForm):
    class Meta:
        model = EthicsSummativeGrade
        fields = ('score', 'comment')
        widgets = {
            'score': forms.Textarea(attrs={'rows': 1, 'cols': 3}),
            'comment': forms.Textarea(attrs={'rows': 1, 'cols': 45})

        }


EthicsSummativeGradeFormSet = inlineformset_factory(EthicsGradeRecord, EthicsSummativeGrade,
                                                    form=EthicsSummativeGradeForm, extra=0, max_num=10)


class EthicsFormativeGradeForm(forms.ModelForm):
    class Meta:
        model = EthicsFormativeGrade
        fields = ('score',)
        widgets = {
            'score': forms.NumberInput(attrs={'cols':3, 'max':5, 'min':0 }),
        }


EthicsFormativeGradeFormSet = inlineformset_factory(EthicsGradeRecord, EthicsFormativeGrade,
                                                    form=EthicsFormativeGradeForm, extra=10, max_num=10)


class FormativeCommentsForm(forms.ModelForm):
    class Meta:
        model = EthicsGradeRecord
        fields = ('commendation', 'recommendation')
        widgets = {
            'commendation': forms.Textarea(attrs={'rows': 6, 'cols': 30, 'required':True}),
            'recommendation': forms.Textarea(attrs={'rows': 6, 'cols': 30, 'required':True}),
        }
        # commendation = forms.CharField(widget=forms.Textarea(attrs={'rows': 6, 'cols': 30}))
        # recommendation = forms.CharField(widget=forms.Textarea(attrs={'rows': 6, 'cols': 30}))


class SkillGradeRecordInstructorForm(forms.ModelForm):
    class Meta:
        model = SkillGradeRecord
        fields = ('student', 'level')


class SkillGradeForm(forms.ModelForm):
    class Meta:
        model = SkillGrade
        fields = ('score',)
        widgets = {
            'score': forms.Textarea(attrs={'rows': 1, 'cols': 3}),
        }


SkillGradeFormSet = inlineformset_factory(SkillGradeRecord, SkillGrade, form=SkillGradeForm, extra=10)


class StudentDiscussionForm(forms.ModelForm):
    class Meta:
        model = EthicsGradeRecord
        fields = ('student_discussed', 'student_discussion_comment')
        widgets = {
            'student_discussed': forms.DateInput(attrs={'type': 'date', 'placeholder': "mm/dd/yyyy"}),
            'student_discussion_comment': forms.Textarea(attrs={'rows': 6, 'cols': 30}),
        }


class VCValidationForm(forms.ModelForm):
    class Meta:
        model = EthicsGradeRecord
        fields = ('vc_validated', 'vc_comment')
        widgets = {
                      'vc_validated': forms.DateInput(
                          attrs={'type': 'date', 'placeholder': "mm/dd/yyyy"}),
                      'vc_comment': forms.Textarea(attrs={'rows': 1}),
                  }
        labels ={
            'vc_validated':"Validated on:",
            'vc_comment': "Comment:"
        }
        edit_only = True


VCValidationFormSet = modelformset_factory(EthicsGradeRecord, form=VCValidationForm, extra=0, )
