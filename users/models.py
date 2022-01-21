from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


class Country(models.Model):
    name = models.CharField(max_length=25, unique = True)
    code = models.CharField(max_length=3, unique = True)
    REGIONS = {
        ('a', 'Asia'),
        ('e', 'Europe'),
        ('n', 'North America'),
    }
    region = models.CharField(max_length=1, choices=sorted(REGIONS), null=False, blank=False)

    def __str__(self):
        return self.code

class School(models.Model):
    name = models.CharField(max_length=50, help_text='Enter the name of the school', unique=True, blank=False,
                            null=False)
    abbreviation = models.CharField(max_length=4, default=" ", help_text=' Enter the abbreviation for this school', unique= True)
    ordering = ['name']
    foundation = models.BooleanField(default=False)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

# User Model is automatically created by Django and we will extend it to add phone number
class Profile(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    school = models.ForeignKey(School, null = True, blank = True, on_delete= models.PROTECT)


    def __str__(self):
        return self.user.last_name + ", " + self.user.first_name

# class Instructor(models.Model):
#     user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
#     #school = models.ForeignKey(School, null = True, blank = True, on_delete= models.CASCADE)
#
#     def __str__(self):
#         return self.user.first_name +" " + self.user.last_name
#
# class SchoolAdmin(models.Model):
#     user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
#     #school = models.ForeignKey(School, null = True, blank = True, on_delete= models.CASCADE)
#
#     def __str__(self):
#         return self.user.first_name +" " + self.user.last_name
#
# class VocationalCoordinator(models.Model):
#     user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
#     #school = models.ForeignKey(School, null = True, blank = True, on_delete= models.CASCADE)
#
#     def __str__(self):
#         return self.user.first_name +" " + self.user.last_name


class Student(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    birthday = models.DateField()
    CHOICES = (
        ('f', 'Female'),
        ('m', 'Male'),
    )
    gender = models.CharField(max_length=1, choices=CHOICES, null=False, blank=False, default = 'f')
    graduation_year = models.PositiveSmallIntegerField(validators=[MinValueValidator(2022), MaxValueValidator(2100)])
    parent = models.ManyToManyField(User, related_name="children", blank=True)
    def __str__(self):
        return self.user.last_name + ", " + self.user.first_name


class Address(models.Model):
    address_1 = models.CharField(verbose_name="address", max_length=128)
    address_2 = models.CharField(verbose_name="address cont'd", max_length=128, blank=True)
    city = models.CharField(verbose_name="city", max_length=64, default="")
    state = models.CharField(verbose_name="state or province", max_length=4, default="")
    zip_code = models.CharField(verbose_name="zip/postal code", max_length=8, default="")
    country = models.ForeignKey(Country, on_delete=models.PROTECT)

    school = models.ForeignKey(School, on_delete = models.CASCADE, null=True, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.city + "," + self.country.name
