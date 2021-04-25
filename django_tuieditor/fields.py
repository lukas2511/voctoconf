from django import forms

from .widgets import MarkdownEditorWidget


class MarkdownFormField(forms.CharField):
    widget = MarkdownEditorWidget
