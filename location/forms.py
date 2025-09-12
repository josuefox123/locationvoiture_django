from django import forms
from .models import Vehicule, Client, Louer
from django.contrib.auth.models import User

class VehiculeForm(forms.ModelForm):
    class Meta:
        model = Vehicule
        fields = '__all__'
        



class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]  # on limite aux champs utiles
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        exclude = ["user", "email_confirmed", "confirmation_code", "confirmation_code_expires_at"]
        widgets = {
            "nom": forms.TextInput(attrs={"class": "form-control"}),
            "prenom": forms.TextInput(attrs={"class": "form-control"}),
            "profession": forms.TextInput(attrs={"class": "form-control"}),
            "adresse": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "telephone": forms.TextInput(attrs={"class": "form-control"}),
        }


class LouerForm(forms.ModelForm):
    class Meta:
        model = Louer
       
        fields = ['date_debut', 'date_finlocation', 'kilometrageapreslocation']
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_finlocation': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'kilometrageapreslocation': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_finlocation = cleaned_data.get('date_finlocation')

        if date_debut and date_finlocation and date_debut > date_finlocation:
            raise forms.ValidationError("La date de début doit être antérieure à la date de fin.")
        
        return cleaned_data

    
