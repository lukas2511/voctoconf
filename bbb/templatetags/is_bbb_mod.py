from django import template

register = template.Library()

@register.filter
def is_bbb_mod(room, user):
    return room.is_moderator(user)
