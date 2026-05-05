from urllib.parse import urlparse

from django import forms
from django.core.exceptions import ValidationError

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].choices = [
            (Project.STATUS_OPEN, "Открыт"),
            (Project.STATUS_CLOSED, "Закрыт"),
        ]

    def clean_github_url(self):
        value = self.cleaned_data.get("github_url")
        if not value:
            return value

        parsed = urlparse(value)
        if not parsed.netloc.lower().endswith("github.com"):
            raise ValidationError("Ссылка должна вести на github.com")

        return value
