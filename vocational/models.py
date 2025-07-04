from users.models import *
from django.core.exceptions import ValidationError
from django.utils import timezone
import pytz
from pytz import timezone as pytz_timezone
from django.conf import settings
from django.db.models import Func
from datetime import timedelta



# isei_admin managed
class EthicsLevel(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100, blank=True, null=True)
    ordering = ['name']
    def __str__(self):
        return self.name

class EthicsDefinition(models.Model):
    level = models.ForeignKey(EthicsLevel, on_delete=models.CASCADE)
    number = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    name = models.CharField(max_length=30, )
    description = models.CharField(max_length=300, blank=True, null=True)
    #school = models.Foreignkey(School)
    class Meta:
        unique_together = (('number', 'level'), ('name', 'level',))
    def __str__(self):
        return self.name + ", " + self.level.name

#Ethics, Skills, Leadership
class VocationalClass(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100, null=True, blank=True)
    ordering = ['name']
    def __str__(self):
        return self.name


# school_admin managed
class SchoolYear(models.Model):
    updated_at = models.DateTimeField(auto_now=True,)
    name = models.CharField(max_length=9, verbose_name="School Year (ex:2024-2025)")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    active = models.BooleanField(default=True, )
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        super(SchoolYear, self).save(*args, **kwargs)
        if self.active:
            SchoolYear.objects.filter(school = self.school).exclude(id=self.id).update(active=False)

    class Meta:
        unique_together = (('name', 'school'),)


class Quarter(models.Model):
    updated_at = models.DateTimeField(auto_now=True,)
    CHOICES = (
        ('1', 'Quarter 1'),
        ('2', 'Quarter 2'),
        ('3', 'Quarter 3'),
        ('4', 'Quarter 4')
    )
    name = models.CharField(max_length=1, choices=CHOICES, null=False, blank=False)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    class Meta:
        unique_together=('school_year', 'name')

    def __str__(self):
        return self.get_name_display() + ", " + self.school_year.name


class GradeSettings(models.Model):
    updated_at = models.DateTimeField(auto_now=True,)
    school_year = models.OneToOneField(SchoolYear, on_delete=models.CASCADE)
    progress_ratio = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], default=20)
    summative_ratio = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], default=80)
    track_time=models.BooleanField(default=False)
    CHOICES = (
        ('h', 'Hours'),
        ('d', 'Days'),
        ('w', 'Weeks'),
    )
    time_unit = models.CharField(max_length=1, choices=CHOICES, null=True, blank=True)


# vocational instructor managed
class Department(models.Model):
    updated_at = models.DateTimeField(auto_now=True,)
    name = models.CharField(max_length=20, null=False, blank=False)
    is_active = models.BooleanField(default=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    class Meta:
        ordering = ('school', '-is_active', 'name')
        unique_together =('school', 'name' )
    def __str__(self):
        return self.name



class VocationalStatus(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    vocational_level = models.ForeignKey(EthicsLevel, on_delete=models.CASCADE)
    vocational_class = models.ForeignKey(VocationalClass, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.vocational_level.name


class InstructorAssignment(models.Model):
    updated_at = models.DateTimeField(auto_now=True,)
    department = models.OneToOneField(Department, on_delete=models.CASCADE)
    instructor = models.ManyToManyField(Profile, related_name="instructor_assignments", blank=True)
    def __str__(self):
        return self.department.name

class StudentAssignment(models.Model):
    updated_at = models.DateTimeField(auto_now=True,)
    quarter = models.ForeignKey(Quarter, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    student = models.ManyToManyField(Student, related_name="student_assignment", blank=True,)
    class Meta:
        unique_together = ('quarter', 'department')
    def __str__(self):
        return str(self.quarter) + ", " + self.department.name

class TimeCard(models.Model):
    student_assignment = models.ForeignKey(StudentAssignment, on_delete=models.CASCADE)
    student=models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    time_in = models.DateTimeField(null=True, blank=True)
    time_out = models.DateTimeField(null=True, blank=True)
    timezone = models.CharField(max_length=255, null=True, blank=True)
    week_range = models.CharField(max_length=30, blank=True, null=True)

    def update_week_range(self):
        if self.time_in:
            start = self.time_in - timedelta(days=self.time_in.weekday())
            start_date = start.date()
            end_date = start_date + timedelta(days=6)

            if start_date.month == end_date.month:
                # If it's the same month, format the end date as just the day
                self.week_range = f'{start_date.strftime("%B %-d")}-{end_date.strftime("%-d")}'
            else:
                # If it's different months, include the month name in the end date
                self.week_range = f'{start_date.strftime("%B %-d")}-{end_date.strftime("%B %-d")}'
        else:
            self.week_range = None

    @property
    def tz(self):
        return pytz_timezone(self.timezone or settings.TIME_ZONE)

    def save(self, *args, **kwargs):
        self.update_week_range()
        if self.student and self.student.user and self.student.user.profile and self.student.user.profile.school:
            self.timezone = self.student.user.profile.school.timezone
        super().save(*args, **kwargs)

    def duration(self):
        if self.time_in and self.time_out:
            duration = self.time_out - self.time_in
            duration_in_s = duration.total_seconds()
            hours, remainder = divmod(duration_in_s, 3600)
            hours=int(hours)
            minutes, _ = divmod(remainder, 60)
            minutes = round(minutes)
            if minutes == 60:
                hours += 1
                minutes = 0
            return hours, minutes
        else:
            return None

    def duration_in_hours(self):
        if self.time_in and self.time_out:
            duration = self.time_out - self.time_in
            duration_in_s = duration.total_seconds()
            hours = round(duration_in_s/ 3600, 2)
            return hours
        else:
            return None


    def get_time_in(self):
        if self.time_in:
            return timezone.localtime(self.time_in, self.tz).strftime('%I:%M %p')

    def get_time_out(self):
        if self.time_out:
            return timezone.localtime(self.time_out, self.tz).strftime('%I:%M %p')

    def get_date(self):
        if self.time_in:
            return timezone.localtime(self.time_in, self.tz).strftime('%B %d, %Y')

    def get_date_no_year(self):
        if self.time_in:
            return timezone.localtime(self.time_in, self.tz).strftime('%B %-d')


    def __str__(self):
        department = str(self.student_assignment.department) if self.student_assignment else "No department"
        student = str(self.student) if self.student else "No student"
        date = self.get_date() or "No date"
        time_in = self.get_time_in() or "?"
        time_out = self.get_time_out() or "?"
        return f"{student} - {department} - {date} ({time_in}-{time_out})"


#Grades
class EthicsGradeRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=False, null=False)
    level = models.ForeignKey(EthicsLevel, on_delete=models.PROTECT, blank=False, null=False)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, blank=False, null=False)
    instructor = models.ForeignKey(User, on_delete=models.PROTECT, blank=False, null=False)
    quarter = models.ForeignKey(Quarter, on_delete=models.PROTECT, blank=False, null=False)
    time = models.DecimalField(decimal_places=2, max_digits=5, blank=True, null=True)
    suggested_level = models.ForeignKey(EthicsLevel, related_name="suggested_level", on_delete=models.PROTECT, blank=True, null=True)
    accepted_level = models.ForeignKey(EthicsLevel, related_name="accepted_level", on_delete=models.PROTECT, blank=True, null=True)

    CHOICES = (
        ('F', 'Formative'),
        ('S', "Summative")
    )
    type = models.CharField(max_length=1, choices=CHOICES, null=False, blank=False, default='F')

    created_at = models.DateTimeField(auto_now=True)
    evaluation_date = models.DateField(null=False, blank=False)
    student_discussed = models.DateField(null=True, blank=True, verbose_name="Student Discussed Date")
    student_discussion_comment = models.CharField(max_length=300, null=True, blank=True)
    vc_validated = models.DateField(null=True, blank=True)
    vc_comment= models.CharField(max_length=300, null=True, blank=True)
    updated_at = models.DateField(auto_now=True)

    commendation = models.CharField(max_length=300, null=True, blank=True)
    recommendation = models.CharField(max_length=300, null=True, blank=True)

    class Meta:
        unique_together = ('student', 'department', 'evaluation_date')


    def score(self):
        n = 0
        total_score = 0
        if self.type == "F":
            for i in self.ethicsformativegrade_set.all():
                if int(i.score or 0) >0:
                    n = n + 1
                    total_score = total_score + i.score
        if self.type == "S":
            for i in self.ethicssummativegrade_set.all():
                if int(i.score or 0) >0:
                    n = n + 1
                    total_score = total_score + i.score
        if n > 0:
            score = round(total_score / n, 2)
        else:
            score = 0
        return score

    def percent(self):
        percent = round(48.0294 * (1.1571 ** float(self.score())) + 0.4, 1)
        return percent

class EthicsSummativeGrade(models.Model):
    ethic = models.ForeignKey(EthicsDefinition, blank=False, null=False, on_delete=models.PROTECT)
    score = models.DecimalField(decimal_places=2, max_digits=3, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(5)])
    comment = models.CharField(max_length=300, null=True, blank=True)
    grade_record = models.ForeignKey(EthicsGradeRecord, on_delete=models.CASCADE)
    class Meta:
        unique_together = ( 'ethic', 'grade_record')
        ordering = ('id',)


class EthicsFormativeGrade(models.Model):
    ethic = models.ForeignKey(EthicsDefinition, blank=False, null=False, on_delete=models.PROTECT)
    score = models.DecimalField(decimal_places=2, max_digits=3, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(5)])
    grade_record = models.ForeignKey(EthicsGradeRecord, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('ethic', 'grade_record')
        ordering = ('id',)

# class GradeMessages(models.Model):
#     grade_record = models.ForeignKey(EthicsGradeRecord, on_delete=models.CASCADE)
#     message = models.CharField(max_length=300)
#     #to = models.ForeignKey(User, on_delete=models.PROTECT)
#     #from = models.ForeignKey(User, on_delete=models.PROTECT)
#     read = models.BooleanField(default="False")
#     date = models.DateTimeField(auto_now=True)


class VocationalSkill(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    weight = models.DecimalField(decimal_places=2, max_digits=4, default=1)
    # TODO these are optional, need to ask school if they want those fields or not
    level = models.ForeignKey(EthicsLevel, on_delete=models.CASCADE, null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('department', 'name')
        ordering = ('id',)

class SkillValue(models.Model):
    score = models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    description = models.CharField(max_length=100)
    value = models.DecimalField(decimal_places=2, max_digits=3, validators=[MinValueValidator(0), MaxValueValidator(1.5)])
    class Meta:
        ordering = ('value',)
    def __str__(self):
        return str(self.score) + ". " + self.description


class SkillGradeRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=False, null=False)
    level = models.ForeignKey(EthicsLevel, on_delete=models.PROTECT, blank=False, null=False)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, blank=False, null=False)
    instructor = models.ForeignKey(User, on_delete=models.PROTECT, blank=False, null=False)
    quarter = models.ForeignKey(Quarter, on_delete=models.PROTECT, blank=False, null=False)

    evaluation_date = models.DateField(null=False, blank=False,)
    created_at = models.DateField(auto_now=True)
    updated_at = models.DateField(auto_now=True)

    commendation = models.CharField(max_length=300, null=True, blank=True)
    recommendation = models.CharField(max_length=300, null=True, blank=True)


class SkillGrade(models.Model):
    skill = models.ForeignKey(VocationalSkill, blank=False, null=False, on_delete=models.PROTECT)
    score = models.ForeignKey(SkillValue, on_delete=models.PROTECT, blank=True, null=True)
    grade_record = models.ForeignKey(SkillGradeRecord, on_delete=models.CASCADE, blank=False, null=False)
    class Meta:
        unique_together = ('skill', 'grade_record')


