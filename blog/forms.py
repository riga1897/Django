from typing import Any

from django import forms

from .models import BlogPost


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ["title", "content", "preview", "owner", "is_published"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        for _field_name, field in self.fields.items():
            if field.widget.__class__.__name__ not in ["CheckboxInput", "RadioSelect"]:
                current_classes = field.widget.attrs.get("class", "")
                if "form-control" not in current_classes:
                    field.widget.attrs["class"] = f"{current_classes} form-control".strip()
