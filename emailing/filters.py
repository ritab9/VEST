import django_filters
from django_filters import ModelChoiceFilter, MultipleChoiceFilter
from django.contrib.auth.models import Group

class UserFilter(django_filters.FilterSet):
    group=ModelChoiceFilter(field_name="groups", label="Group", queryset=Group.objects.all())