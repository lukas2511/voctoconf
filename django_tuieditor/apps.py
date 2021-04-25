import django.contrib.admin.options as options
from django.apps import AppConfig

from django_tuieditor.models import MarkdownField
from django_tuieditor.widgets import MarkdownEditorWidget

# DIRTY HACK BELOW!
options.FORMFIELD_FOR_DBFIELD_DEFAULTS.update({
    MarkdownField: {'widget': MarkdownEditorWidget},
})


class DjangoTUIEditorConfig(AppConfig):
    name = 'django_tuieditor'
    verbose_name = 'Django TUI.Editor'
