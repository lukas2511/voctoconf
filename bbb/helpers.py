#!/usr/bin/env python3

from django import template

register = template.Library()

@register.filter
def is_bbb_moderator(room, user):
	if not user.is_authenticated:
		return False

	if user.is_superuser or user.is_staff:
		return True

	if room.moderators.filter(username=user.username).exists():
		return True

	if room.for_partner.all() and any([(x.owner and x.owner == user) for x in room.for_partner.all()]):
		return True

	return False


