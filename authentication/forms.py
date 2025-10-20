
from django import forms

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            raise forms.ValidationError("Invalid email or password")

        user = authenticate(username=username, password=password)
        if user is None:
            raise forms.ValidationError("Invalid email or password")
        self.user = user
        return self.cleaned_data

    def get_user(self):
        return self.user

