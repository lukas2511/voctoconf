from cmarkgfm import github_flavored_markdown_to_html
from cmarkgfm.cmark import Options as cmarkgfmOptions
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter()
@stringfilter
def gfm(markdown: str) -> str:
    return mark_safe(github_flavored_markdown_to_html(markdown, options=cmarkgfmOptions.CMARK_OPT_HARDBREAKS))
