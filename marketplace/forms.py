from django import forms
from django.core.exceptions import ValidationError

from .models import Product

FORBIDDEN_WORDS = [
    'казино', 'криптовалюта', 'крипта', 'биржа',
    'дешево', 'бесплатно', 'обман', 'полиция', 'радар'
]


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'photo', 'category', 'price']

    def clean_name(self):
        name = self.cleaned_data.get('name', '')
        name_lower = name.lower()

        for word in FORBIDDEN_WORDS:
            if word in name_lower:
                raise ValidationError(
                    f'Название не может содержать запрещенное слово: "{word}"'
                )

        return name

    def clean_description(self):
        description = self.cleaned_data.get('description', '')
        if description:
            description_lower = description.lower()

            for word in FORBIDDEN_WORDS:
                if word in description_lower:
                    raise ValidationError(
                        f'Описание не может содержать запрещенное слово: "{word}"'
                    )

        return description

    def clean_price(self):
        price = self.cleaned_data.get('price')

        if price is not None and price < 0:
            raise ValidationError('Цена не может быть отрицательной')

        return price

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')

        if photo:
            if hasattr(photo, 'size') and photo.size > 5 * 1024 * 1024:
                raise ValidationError('Размер файла не должен превышать 5 МБ')

            if hasattr(photo, 'name'):
                valid_extensions = ['.jpg', '.jpeg', '.png']
                file_ext = photo.name.lower().split('.')[-1]
                if f'.{file_ext}' not in valid_extensions:
                    raise ValidationError(
                        'Допустимы только изображения форматов JPEG и PNG'
                    )

        return photo

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for _field_name, field in self.fields.items():
            if field.widget.__class__.__name__ not in ['CheckboxInput', 'RadioSelect']:
                current_classes = field.widget.attrs.get('class', '')
                if 'form-control' not in current_classes:
                    field.widget.attrs['class'] = f'{current_classes} form-control'.strip()


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label='Имя',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваше имя'
        })
    )
    email = forms.EmailField(
        label='Почта',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите вашу почту'
        })
    )
    message = forms.CharField(
        label='Сообщение',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваше сообщение',
            'rows': 3
        })
    )
