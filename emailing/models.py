from django.db import models
from users.models import School

# Create your models here.
class DefaultMessage(models.Model):
    name = models.CharField(max_length=25, unique = True)
    subject =  models.CharField(max_length=225)
    message = models.CharField(max_length = 1800)

class OverrideMessage(models.Model):
    name=models.ForeignKey(DefaultMessage, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    subject =  models.CharField(max_length=225)
    message = models.CharField(max_length = 1800)

class SchoolMessage(models.Model):
    name = models.CharField(max_length=25, unique=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    subject =  models.CharField(max_length=225)
    message = models.CharField(max_length=1800)

