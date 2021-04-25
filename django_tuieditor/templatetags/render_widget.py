from django import template
from django.forms import Widget

register = template.Library()

@register.simple_tag
def render_widget(widget: Widget, name: str, value: str, attrs: dict = None):
    default_attrs = {'id': f"__django_tuieditor__render_widget__id__{name}"}
    if attrs:
        default_attrs.update(attrs)
    return widget.render(name, value, attrs=default_attrs)

@register.filter
def render_widget_media(widget: Widget):
    return widget.media
