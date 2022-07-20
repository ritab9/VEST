from users.models import *


# isei_admin managed
class EthicsLevel(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100, blank=True, null=True)
    ordering = ['name']

    def __str__(self):
        return self.name

#todo Ethics Definition
class EthicsIndicator(models.Model):
    level = models.ForeignKey(EthicsLevel, on_delete=models.CASCADE)
    number = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    name = models.CharField(max_length=30, )
    description = models.CharField(max_length=300, blank=True, null=True)
    #school = models.Foreignkey(School)

    class Meta:
        unique_together = (('number', 'level'), ('name', 'level',))

    def __str__(self):
        return self.name + ", " + self.level.name


class VocationalClass(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100, null=True, blank=True)
    ordering = ['name']

    def __str__(self):
        return self.name


# school_admin managed

class SchoolYear(models.Model):
    name = models.CharField(max_length=9)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    active = models.BooleanField(default=True, )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(SchoolYear, self).save(*args, **kwargs)
        if self.active:
            SchoolYear.objects.exclude(id=self.id).update(active=False)


class Quarter(models.Model):
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

    def __str__(self):
        return self.get_name_display() + ", " + self.school_year.name


# vocational instructor managed

class Department(models.Model):
    name = models.CharField(max_length=20, null=False, blank=False)
    is_active = models.BooleanField(default=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE)

    class Meta:
        ordering = ('school', '-is_active', 'name')

    def __str__(self):
        return self.name


class VocationalSkill(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    weight = models.DecimalField(decimal_places=2, max_digits=4, default=1)
    # TODO these are optional, need to ask school if they want those fields or not
    level = models.ForeignKey(EthicsLevel, on_delete=models.CASCADE, null=True, blank=True)
    code = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.name


class VocationalStatus(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    vocational_level = models.ForeignKey(EthicsLevel, on_delete=models.CASCADE)
    vocational_class = models.ForeignKey(VocationalClass, on_delete=models.CASCADE)


class InstructorAssignment(models.Model):
    department = models.OneToOneField(Department, on_delete=models.CASCADE)
    instructor = models.ManyToManyField(User, related_name="instructor_assignments", blank=True)


class StudentAssignment(models.Model):
    quarter = models.ForeignKey(Quarter, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    student = models.ManyToManyField(Student, related_name="student_assignment", blank=True)
    class Meta:
        unique_together = ('quarter', 'department')

#unused
# class VocationalAssignment(models.Model):
#     quarter = models.ForeignKey(Quarter, on_delete=models.CASCADE)
#     department = models.ForeignKey(Department, on_delete=models.CASCADE)
#     student = models.ManyToManyField(Student, related_name="s_assignment", blank=True)
#     instructor = models.ManyToManyField(User, related_name="i_assignments", blank=True)
#
#     class Meta:
#         unique_together = ('quarter', 'department')
#         index_together = ('quarter', 'department')


#todo rename to EthicsGradeRecord
class EthicsGrade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=False, null=False)
    level = models.ForeignKey(EthicsLevel, on_delete=models.PROTECT, blank=False, null=False)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, blank=False, null=False)
    instructor = models.ForeignKey(User, on_delete=models.PROTECT, blank=False, null=False)
    quarter = models.ForeignKey(Quarter, on_delete=models.PROTECT, blank=False, null=False)

    CHOICES = (
        ('F', 'Formative'),
        ('S', "Summative")
    )
    type = models.CharField(max_length=1, choices=CHOICES, null=False, blank=False, default='F')

    created_at = models.DateField(auto_now=True)
    student_discussed = models.DateField(null=True, blank=True)
    vc_validated = models.DateField(null=True, blank=True)
    updated_at = models.DateField(auto_now=True)

    commendation = models.CharField(max_length=300, null=True, blank=True)
    recommendation = models.CharField(max_length=300, null=True, blank=True)

    #todo rename value to score
    def value(self):
        n = 0
        total_value = 0
        if self.type == "F":
            for i in self.indicatorformativegrade_set.all():
                if int(i.value or 0) >0:
                    n = n + 1
                    total_value = total_value + i.value
        if self.type == "S":
            for i in self.indicatorsummativegrade_set.all():
                if int(i.value or 0) >0:
                    n = n + 1
                    total_value = total_value + i.value
        if n > 0:
            value = round(total_value / n, 2)
        else:
            value = 0
        return value

    def percent(self):
        percent = round(48.0294 * (1.1571 ** float(self.value())) + 0.4, 1)
        return percent

#Todo rename EthicSummativeGrade
class IndicatorSummativeGrade(models.Model):
    #todo ethic instead of indicator
    indicator = models.ForeignKey(EthicsIndicator, blank=False, null=False, on_delete=models.PROTECT)
    #todo rename value to score
    value = models.DecimalField(decimal_places=2, max_digits=3, null=True, blank=True)
    comment = models.CharField(max_length=300, null=True, blank=True)
    # todo rename to grade_record
    grade = models.ForeignKey(EthicsGrade, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('indicator', 'grade')
        ordering = ('id',)

#Todo rename EthicFormativeGrade
class IndicatorFormativeGrade(models.Model):
    #todo ethic instead of indicator
    indicator = models.ForeignKey(EthicsIndicator, blank=False, null=False, on_delete=models.PROTECT)
    #todo rename value to score
    value = models.DecimalField(decimal_places=2, max_digits=3, null=True, blank=True)
    # todo rename to grade_record
    grade = models.ForeignKey(EthicsGrade, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('indicator', 'grade')


class GradeMessages(models.Model):
    grade = models.ForeignKey(EthicsGrade, on_delete=models.CASCADE)
    message = models.CharField(max_length=300)
    to = models.ForeignKey(User, on_delete=models.PROTECT)
    #from = models.ForeignKey(User, on_delete=models.PROTECT)
    read = models.BooleanField(default="False")
    date = models.DateTimeField(auto_now=True)

class SkillValue(models.Model):
    number = models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    description = models.CharField(max_length=100)
    value=models.DecimalField(decimal_places=2, max_digits=3, validators=[MinValueValidator(0), MaxValueValidator(1.5)])

    class Meta:
        ordering = ('value',)
    def __str__(self):
        return str(self.value) + " " + self.description


class SkillGrade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=False, null=False)
    level = models.ForeignKey(EthicsLevel, on_delete=models.PROTECT, blank=False, null=False)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, blank=False, null=False)
    instructor = models.ForeignKey(User, on_delete=models.PROTECT, blank=False, null=False)
    quarter = models.ForeignKey(Quarter, on_delete=models.PROTECT, blank=False, null=False)

    student_discussed = models.DateField(null=True, blank=True)
    created_at = models.DateField(auto_now=True)
    updated_at = models.DateField(auto_now=True)

    commendation = models.CharField(max_length=300, null=True, blank=True)
    recommendation = models.CharField(max_length=300, null=True, blank=True)


class IndicatorSkillGrade(models.Model):
    skill = models.ForeignKey(VocationalSkill, blank=False, null=False, on_delete=models.PROTECT)
    value = models.ForeignKey(SkillValue, on_delete=models.PROTECT, blank=True, null=True)
    grade = models.ForeignKey(SkillGrade, on_delete=models.CASCADE, blank=False, null=False)

    class Meta:
        unique_together = ('skill', 'grade')


class SchoolOptions(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    CHOICES = (
        ('N', "None"),
        ('H', 'Hours'),
        ('D', "Days"),
        ('W', "Weeks"),
    )
    timebased = models.CharField(max_length=1, choices=CHOICES, null=False, blank=False, default='N')

