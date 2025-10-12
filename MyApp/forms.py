from django.forms import ModelForm, TextInput
from .models import CityModel

class CityForm(ModelForm):
    class Meta:
        model = CityModel
        fields = ['name']
        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
                'name': 'city',
                'id': 'city',
                'placeholder': 'Введите город',
            })
        }