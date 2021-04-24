from django import template
from django.template.defaultfilters import stringfilter
from cmarkgfm import github_flavored_markdown_to_html

register = template.Library()

@register.filter
@stringfilter
def gfm(markdown: str) -> str:
    return github_flavored_markdown_to_html(markdown)
