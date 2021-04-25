from django.db import models
from django.utils.translation import gettext_lazy as _

from .fields import MarkdownFormField


class MarkdownField(models.TextField):
    description = _("Markdown Code Text")

    def formfield(self, **kwargs):
        # see https://docs.djangoproject.com/en/3.2/howto/custom-model-fields/
        return super().formfield(**{'form_class': MarkdownFormField, **kwargs})
