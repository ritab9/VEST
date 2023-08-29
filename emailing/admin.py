from django.contrib import admin
from .models import *


class CustomizedSystemMessageInLine(admin.StackedInline):
    model = CustomizedSystemMessage
    can_delete = True
    extra = 0


@admin.register(SystemMessage)
class SystemMessage(admin.ModelAdmin):
    model = SystemMessage
    inlines = [CustomizedSystemMessageInLine]
    list_display = ('name', 'subject')


@admin.register(LocalMessage)
class LocalMessage(admin.ModelAdmin):
    model = LocalMessage
    list_display = ('school', 'name', 'subject')
