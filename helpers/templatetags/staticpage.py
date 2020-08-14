from django import template
from helpers.models import StaticPage

register = template.Library()

@register.filter
def staticpage(page, locale="de"):
	try:
		return StaticPage.objects.get(name=page).text(locale)
	except:
		return "!!! text for %s missing !!!" % page
