from django.contrib import admin
from .models import *

class OverrideMessageInLine(admin.StackedInline):
    model=OverrideMessage
    can_delete = True
    extra = 0

@admin.register(DefaultMessage)
class DefaultMessage(admin.ModelAdmin):
    model = DefaultMessage
    inlines=[OverrideMessageInLine]
    list_display = ('name','subject')


@admin.register(SchoolMessage)
class SchoolMessage(admin.ModelAdmin):
    model=SchoolMessage
    list_display = ('school','name','subject')



