from django import template
from functools import reduce
import operator
from vocational.models import GradeSettings, SchoolYear, School
register = template.Library()


@register.filter('track_time')
def track_time(school_id):
    return GradeSettings.objects.filter(school_year__school_id=school_id).exists()

@register.filter('school_year')
def school_year(user):
    return SchoolYear.objects.filter(school = user.profile.school, active=True).first()

@register.filter('school')
def school(user):
    return School.objects.get(id = user.profile.school.id)

@register.filter('shortened_username')
def shortened_username(username):
    return username.rsplit('_', 1)[-1]

@register.filter('get_nested_dict_value')
def get_nested_dict_value(dict, keys):
    keys = keys.split(",")
    return reduce(operator.getitem, keys, dict)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)