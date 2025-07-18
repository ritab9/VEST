from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from .models import *
from vocational.models import VocationalStatus

# Register your models here.
@admin.register(Country)
class Country(admin.ModelAdmin):
    list_display = ('name', 'code', 'region')
    list_editable = ('code', 'region')

class AddressInLine(admin.StackedInline):
    model = Address
    can_delete = True
    extra = 0

@admin.register(School)
class School(admin.ModelAdmin):
    inlines = [AddressInLine,]
    list_display = ('name', 'abbreviation',)
    list_editable = ('abbreviation', )


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = True
    extra = 0

# class InstructorInline(admin.StackedInline):
#     model = Instructor
#     can_delete = True
#     extra = 0
# class VocationalCoordinatorInline(admin.StackedInline):
#     model = VocationalCoordinator
#     can_delete = True
#     extra = 0
# class SchoolAdminInline(admin.StackedInline):
#     model = SchoolAdmin
#     can_delete = True
#     e

class StudentInline(admin.StackedInline):
    model=Student
    can_delete=True
    extra=0

class UserAdmin(AuthUserAdmin):
    model = User
    inlines = [ProfileInline, StudentInline,]
    list_display = ('username', 'first_name', 'last_name', 'id','group', 'is_active')
    list_editable = ('is_active',)

    #def School(self, obj):
    #    return obj.teacher.school

    def group(self,obj):
        groups = []
        for group in obj.groups.all():
            groups.append(group.name)
            groups.append(" ")
        return ''.join(groups)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

class VocationalStatusInline(admin.StackedInline):
    model=VocationalStatus
    can_delete=True
    extra=0


@admin.register(Student)
class Student(admin.ModelAdmin):
    model= Student
    inlines = [VocationalStatusInline,]
    list_display = ('user','graduation_year', 'birthday', 'gender', 'is_active', "vocational_level")
    list_editable = ('gender', 'graduation_year')
    search_fields = ('user__first_name', 'user__last_name')

    def is_active(self, obj):
        return obj.user.is_active

    def vocational_level(self, obj):
        return obj.vocationalstatus.vocational_level


# @admin.register(Instructor)
# class Instructor(admin.ModelAdmin):
#     #inlines = [UserInline]
#     #list_display = ('name', 'school',)
#     #list_editable = ('school', )
#     #list_display_links = ('name',)
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         return qs.filter(user__is_active = True)
#
# @admin.register(SchoolAdmin)
# class SchoolAdmin(admin.ModelAdmin):
#     #inlines = [UserInline]
#     #list_display = ('name', 'school',)
#     #list_editable = ('school', )
#     #list_display_links = ('name',)
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         return qs.filter(user__is_active = True)
#
# @admin.register(VocationalCoordinator)
# class VocationalCoordinator(admin.ModelAdmin):
#     #inlines = [UserInline]
#     #list_display = ('name', 'school',)
#     #list_editable = ('school', )
#     #list_display_links = ('name',)
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         return qs.filter(user__is_active = True)