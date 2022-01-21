from django import template

register = template.Library()

@register.filter('in_group')
def in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

@register.filter('in_more_groups')
def in_more_groups(user):
    if user.groups.all().count() > 1:
        return True
    else:
        return False