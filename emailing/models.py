from django.db import models
from users.models import School
import datetime

# Create your models here.
class DefaultMessage(models.Model):
    updated_at = models.DateTimeField(auto_now=True,)
    name = models.CharField(max_length=25, unique = True)
    subject =  models.CharField(max_length=225)
    message = models.CharField(max_length = 1800)
    def __str__(self):
        return self.name

class OverrideMessage(models.Model):
    updated_at = models.DateTimeField(auto_now=True,)
    name=models.ForeignKey(DefaultMessage, on_delete=models.PROTECT, related_name="overridden")
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    subject =  models.CharField(max_length=225)
    message = models.CharField(max_length = 1800)

    class Meta:
        unique_together=('name', 'school')

class SchoolMessage(models.Model):
    updated_at = models.DateTimeField(auto_now=True,)
    name = models.CharField(max_length=25, unique=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    subject =  models.CharField(max_length=225)
    message = models.CharField(max_length=1800)

