from django.contrib.auth.models import User
from django.db.models import Q


# from .models import *

def in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

def get_active_school_staff(school):
    school_staff = User.objects.filter(
        Q(profile__school=school) & Q(
            groups__name__in=["school_admin", "instructor", "vocational_coordinator"])).order_by('last_name').distinct()
    return school_staff


def get_inactive_school_staff(school):
    school_staff = User.objects.filter(
        Q(profile__school=school) & Q(groups__name="inactive_staff")).order_by('last_name').distinct()
    return school_staff


def has_children(user):
    children = user.children.all().exists()
    return children

def has_other_children(parent, child):
    children = parent.children.exclude(user=child).filter(user__is_active=True)
    return children.exists()


def is_active_school_staff(user):
    is_active_school_staff = user.groups.filter(
        name__in=["school_admin", "instructor", "vocational_coordinator"]).exists()
    return is_active_school_staff
