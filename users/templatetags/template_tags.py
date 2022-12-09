from django import template
from vocational.models import SchoolSettings, SchoolYear
register = template.Library()


@register.filter('track_time')
def track_time(school_id):
    return SchoolSettings.objects.filter(school_year__school_id=school_id).exists()

@register.filter('school_year')
def school_year(user):
    return SchoolYear.objects.filter(school = user.profile.school, active=True).first()