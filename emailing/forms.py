from django import forms
from django.forms import ModelForm
from django.forms.models import modelformset_factory
from .models import *

class EmailForm(forms.Form):
    subject = forms.CharField(max_length=100)
    #attach = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required = False)
    message = forms.CharField(widget = forms.Textarea)


class DefaultMessageForm(ModelForm):
    class Meta:
        model= DefaultMessage
        fields = "__all__"

        widgets = {
            'message': forms.Textarea(attrs={'cols': 80, 'rows': 10})
        }

DefaultMessageFormSet = modelformset_factory(DefaultMessage, form=DefaultMessageForm,
                                                   can_delete=True, extra=1)


class OverrideMessageForm(ModelForm):
    class Meta:
        model= OverrideMessage
        fields = ('subject', 'message')
        widgets = {
            'message': forms.Textarea(attrs={'cols': 80, 'rows': 10})
        }


class SchoolMessageForm(ModelForm):
    class Meta:
        model= SchoolMessage
        fields = ('name', 'subject', 'message')
        widgets = {
            'message': forms.Textarea(attrs={'cols': 80, 'rows': 10})
        }