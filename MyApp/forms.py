from django.forms import ModelForm, TextInput

class CityForm(forms.Form):
    class Meta:
        model = 