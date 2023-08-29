from django import forms
from django.forms import ModelForm
from django.forms.models import modelformset_factory
from .models import *

class EmailForm(forms.Form):
    subject = forms.CharField(max_length=100)
    #attach = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required = False)
    message = forms.CharField(widget = forms.Textarea)


class SystemMessageForm(ModelForm):
    class Meta:
        model= SystemMessage
        fields = "__all__"

        widgets = {
            'message': forms.Textarea(attrs={'cols': 80, 'rows': 10})
        }

SystemMessageFormSet = modelformset_factory(SystemMessage, form=SystemMessageForm,
                                             can_delete=True, extra=1)


class CustomizedSystemMessageForm(ModelForm):
    class Meta:
        model= CustomizedSystemMessage
        fields = ('subject', 'message')
        widgets = {
            'message': forms.Textarea(attrs={'cols': 80, 'rows': 10})
        }


class LocalMessageForm(ModelForm):
    class Meta:
        model= LocalMessage
        fields = ('name', 'subject', 'message')
        widgets = {
            'message': forms.Textarea(attrs={'cols': 80, 'rows': 10})
        }