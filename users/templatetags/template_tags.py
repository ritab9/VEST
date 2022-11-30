from django import template
from vocational.models import SchoolSettings
register = template.Library()


@register.filter('track_time')
def track_time(school_id):
    return SchoolSettings.objects.filter(school_year__school_id=school_id).exists()
