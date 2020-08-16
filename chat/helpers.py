from django import template

def is_chat_moderator(user):
	if not user.is_authenticated:
		return False

	if user.is_superuser or user.is_staff:
		return True

	return False