from django.contrib.auth.models import User
from django.db.models import Q


# from .models import *

def get_active_school_staff(school):
    school_staff = User.objects.filter(
        Q(profile__school=school) & Q(groups__name__in=["school_admin", "instructor", "vocational_coordinator"]) & Q(
            is_active=True)).order_by('last_name').distinct()
    return school_staff


def get_inactive_school_staff(school):
    school_staff = User.objects.filter(
        Q(profile__school=school) & Q(groups__name__in=["school_admin", "instructor", "vocational_coordinator"]) & Q(
            is_active=False)).order_by('last_name').distinct()
    return school_staff
