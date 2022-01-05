from django.db import models
from users.models import *

# Create your models here.


class VocationalLevel(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100)
    ordering = ['name']
    def __str__(self):
        return self.name

class VocationalClass(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100)
    ordering = ['name']
    def __str__(self):
        return self.name


class VocationalStatus(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    vocational_level = models.ForeignKey(VocationalLevel, on_delete=models.CASCADE )
    vocational_class = models.ForeignKey(VocationalClass, on_delete=models.CASCADE)

