import datetime
from rest_framework import serializers
from django.utils import timezone
from django import forms
import re

class UserFormSerializer(serializers.Serializer):
    firstname = serializers.CharField(
        style={'placeholder': 'Firstname *', 'autofocus': True}
    )
    lastname = serializers.CharField(
        style={'placeholder': 'Lastname *', 'autofocus': True}
    )
    email = serializers.EmailField(
        style={'placeholder': 'Email', 'autofocus': True}
    )
    password = serializers.CharField(
        style={'input_type': 'password', 'placeholder': 'Password'}
    )
    confirmation_password = serializers.CharField(
        style={'input_type': 'password', 'placeholder': 'Password'}
    )

    def clean_username(self):
        un = self.cleaned_data['username']
        if len(un) <= 0:
            raise forms.ValidationError('enter a valid username')
        return un

    def clean_email(self):
        email = self.cleaned_data['email']
        if not re.match(r'\S+@\S+', email):
            raise forms.ValidationError('enter a valid email')
        return email
