from django.contrib import admin
from .models import *


# Register your models here.

@admin.register(GradeSettings)
class GradeSettings(admin.ModelAdmin):
    model=GradeSettings
    list_display = ('school_year','progress_ratio','summative_ratio','track_time','time_unit',)


class EthicsDefinitionInLine(admin.StackedInline):
    model = EthicsDefinition
    can_delete = True
    extra = 10
    max_num = 10


@admin.register(EthicsLevel)
class EthicsLevel(admin.ModelAdmin):
    inlines = [EthicsDefinitionInLine, ]
    model = EthicsLevel
    list_display = ('id', 'name', 'description')
    list_editable = ('name', 'description',)
    ordering = ('id',)


@admin.register(VocationalClass)
class VocationalClass(admin.ModelAdmin):
    model = VocationalClass
    list_display = ('id', 'name', 'description')
    list_editable = ('name', 'description',)
    ordering = ('id',)


@admin.register(VocationalStatus)
class VocationalStatus(admin.ModelAdmin):
    model = VocationalStatus
    list_display = ('student', 'vocational_level', 'vocational_class')
    list_editable = ('vocational_level', 'vocational_class')


@admin.register(Department)
class Department(admin.ModelAdmin):
    model = Department
    list_display = ('name', 'is_active', 'school')


@admin.register(VocationalSkill)
class VocationalSkill(admin.ModelAdmin):
    model = VocationalSkill


class QuarterInLine(admin.StackedInline):
    model = Quarter
    can_delete = True
    extra = 4
    max_num = 4


@admin.register(SchoolYear)
class SchoolYear(admin.ModelAdmin):
    inlines = [QuarterInLine, ]
    model = SchoolYear
    list_display = ('name', 'start_date', 'end_date', 'school','active')
    list_editable = ('start_date', 'end_date','active')
    ordering = ('school',)

@admin.register(InstructorAssignment)
class InstructorAssignment(admin.ModelAdmin):
    model=InstructorAssignment
    list_display = ('department', )


@admin.register(StudentAssignment)
class StudentAssignment(admin.ModelAdmin):
    model=StudentAssignment
    list_display = ('quarter','department', )

# @admin.register(VocationalAssignment)
# class VocationalAssignment(admin.ModelAdmin):
#     model=VocationalAssignment
#     list_display = ('quarter','department', )


# Grades
class EthicSummativeGradeInLine(admin.StackedInline):
    model = EthicsSummativeGrade
    can_delete = True
    extra = 0
    max_num = 10

class EthicFormativeGradeInLine(admin.StackedInline):
    model = EthicsFormativeGrade
    can_delete = True
    extra = 0
    max_num = 10



@admin.register(EthicsGradeRecord)
class EthicsGradeRecord(admin.ModelAdmin):
    inlines = [EthicSummativeGradeInLine, EthicFormativeGradeInLine]
    model = EthicsGradeRecord
    list_display = ('school', 'quarter', 'instructor', 'student', 'department', 'score', 'evaluation_date')
    list_filter = ('department', 'quarter',  'instructor',  'student')
    #list_editable = ('date',)
    ordering = ('evaluation_date',)
    def school(self, obj):
        return obj.student.user.profile.school


@admin.register(SkillValue)
class SkillValue(admin.ModelAdmin):
    model = SkillValue
    list_display = ('number', 'description', 'value' )
    list_editable = ('description', 'value')
    ordering = ('number',)


class SkillGradeInLine(admin.StackedInline):
    model = SkillGrade
    can_delete = True
    extra = 3


@admin.register(SkillGradeRecord)
class SkillGradeRecord(admin.ModelAdmin):
    inlines = [SkillGradeInLine, ]
    model = SkillGradeRecord
    list_display = ('school', 'quarter', 'instructor', 'student', 'department')
    list_filter = ('department', 'quarter',  'instructor',  'student')
    #list_editable = ('start_date', 'end_date',)
    #ordering = ('school',)
    def school(self, obj):
        return obj.student.user.profile.school
