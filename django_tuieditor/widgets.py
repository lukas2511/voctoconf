from django import forms
from django.contrib.admin.widgets import AdminTextareaWidget


class MarkdownEditorWidget(forms.Textarea):
    template_name = 'django_tuieditor/editor.html'

    class Media:
        css = { 'screen': ( 'django_tuieditor/codemirror.css', 'django_tuieditor/toastui-editor.css', 'django_tuieditor/django-fixes.css', ) }
        js = ( 'django_tuieditor/codemirror.js', 'django_tuieditor/toastui-editor.js', 'django_tuieditor/django-fixes.js', )

class MarkdownViewerWidget(forms.Textarea):
    template_name = 'django_tuieditor/viewer.html'

    def __init__(self, attrs=None):
        default_attrs = {'class': 'tui-editor-contents'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    class Media:
        css = { 'screen': ( 'django_tuieditor/codemirror.css', 'django_tuieditor/toastui-editor.css', 'django_tuieditor/django-fixes.css', ) }
        js = ( 'django_tuieditor/codemirror.js', 'django_tuieditor/toastui-editor-viewer.js', 'django_tuieditor/django-fixes.js', )

class StaticMarkdownViewerWidget(forms.Textarea):
    template_name = 'django_tuieditor/static_viewer.html'

    def __init__(self, attrs=None):
        default_attrs = {'class': 'tui-editor-contents'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    class Media:
        css = { 'screen': ( 'django_tuieditor/toastui-editor.css', 'django_tuieditor/django-fixes.css', ) }
        js = ()
