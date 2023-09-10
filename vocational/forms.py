from django import forms
from django.forms import ModelForm
from django.forms.models import inlineformset_factory, modelformset_factory
import datetime
from django.core.exceptions import ValidationError


from django.contrib.auth.models import User
from .models import *



class GradeSettingsForm(forms.ModelForm):
    class Meta:
        model = GradeSettings
        fields = ('progress_ratio', 'summative_ratio', 'track_time', 'time_unit')


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
        self.fields['instructor'].queryset = Profile.objects.filter(school=school, user__groups__name='instructor')

    class Meta:
        model = InstructorAssignment
        fields = ('department', 'instructor')

    instructor = forms.ModelMultipleChoiceField(queryset=None,  required = False, widget=forms.CheckboxSelectMultiple)


InstructorAssignmentFormSet = modelformset_factory(InstructorAssignment, form=InstructorAssignmentForm,
                                                   can_delete=True, can_order=True, extra=2)


class StudentAssignmentForm(forms.ModelForm):
    def __init__(self, school, graduation_year = None, *args, **kwargs):
        super(StudentAssignmentForm, self).__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.filter(school=school, is_active=True)
        if not graduation_year:
            self.fields['student'].queryset = Student.objects.filter(user__profile__school=school,
                                                               user__is_active=True).order_by('user__last_name')
        else:
            self.fields['student'].queryset = Student.objects.filter(user__profile__school=school, graduation_year__in = graduation_year,
                                                                     user__is_active=True).order_by('user__last_name')

    class Meta:
        model = StudentAssignment
        fields = ('department', 'student',)

    student = forms.ModelMultipleChoiceField(queryset=None, required = False, widget=forms.CheckboxSelectMultiple)


StudentAssignmentFormSet = inlineformset_factory(Quarter, StudentAssignment, form=StudentAssignmentForm,
                                                 can_delete=True, can_order=True, extra=2)


class EthicsGradeInstructorForm(forms.ModelForm):
    class Meta:
        model = EthicsGradeRecord
        fields = ('student', 'level',)
        widgets = {
            'level': forms.Textarea(attrs={'readonly': True, 'rows': 1, 'cols': 2}),
        }


class EthicsGradeTimeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['suggested_level'].queryset = EthicsLevel.objects.order_by('name')

    class Meta:
        model = EthicsGradeRecord
        fields = ('time', "suggested_level")
        widgets = {
            'time': forms.Textarea(attrs={'rows': 1, 'cols': 2,}),
        }


class EthicsSummativeGradeForm(forms.ModelForm):
    class Meta:
        model = EthicsSummativeGrade
        fields = ('score', 'comment',)
        widgets = {
            'score': forms.NumberInput(attrs={'rows': 1, 'cols': 3, 'max': 5, 'min': 0}),
            'comment': forms.Textarea(attrs={'rows': 1, 'cols': 45})

        }

    def clean(self):
        cleaned_data = super().clean()
        score = cleaned_data.get('score')
        comment = cleaned_data.get('comment')

        #if score in [1, 2, 5] and not comment:
        #    raise ValidationError("Comments are required for scores of 1, 2, or 5.")


EthicsSummativeGradeFormSet = inlineformset_factory(EthicsGradeRecord, EthicsSummativeGrade,
                                                    form=EthicsSummativeGradeForm, extra=0, max_num=10)

class EthicsFormativeGradeForm(forms.ModelForm):
    class Meta:
        model = EthicsFormativeGrade
        fields = ('score',)
        widgets = {
            'score': forms.NumberInput(attrs={'rows':1, 'cols': 3, 'max': 5, 'min': 0}),
        }


EthicsFormativeGradeFormSet = inlineformset_factory(EthicsGradeRecord, EthicsFormativeGrade,
                                                    form=EthicsFormativeGradeForm, extra=10, max_num=10)


class FormativeCommentsForm(forms.ModelForm):
    class Meta:
        model = EthicsGradeRecord
        fields = ('commendation', 'recommendation')
        widgets = {
            'commendation': forms.Textarea(attrs={'rows': 6, 'cols': 30, 'required': True}),
            'recommendation': forms.Textarea(attrs={'rows': 6, 'cols': 30, 'required': True}),
        }
        # commendation = forms.CharField(widget=forms.Textarea(attrs={'rows': 6, 'cols': 30}))
        # recommendation = forms.CharField(widget=forms.Textarea(attrs={'rows': 6, 'cols': 30}))


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
        fields = ('vc_validated', 'vc_comment', 'accepted_level')
        widgets = {
            'vc_validated': forms.DateInput(
                attrs={'type': 'date', 'placeholder': "mm/dd/yyyy"}),
            'vc_comment': forms.Textarea(attrs={'rows': 1}),
        }
        labels = {
            'vc_validated': "Validated on:",
            'vc_comment': "Comment:"
        }
        edit_only = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Sort the 'accepted_level' queryset by 'name'
        self.fields['accepted_level'].queryset = EthicsLevel.objects.order_by('name')


VCValidationFormSet = modelformset_factory(EthicsGradeRecord, form=VCValidationForm, extra=0, )


class SkillGradeRecordInstructorForm(forms.ModelForm):
    class Meta:
        model = SkillGradeRecord
        fields = ('student', 'level')

class SkillGradeForm(forms.ModelForm):
    class Meta:
        model = SkillGrade
        fields = ('score',)

SkillGradeFormSet = inlineformset_factory(SkillGradeRecord, SkillGrade, form=SkillGradeForm, extra=0)
