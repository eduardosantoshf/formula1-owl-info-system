# -*- coding: utf-8 -*-
# @Author: Eduardo Santos
# @Date:   2023-04-11 16:20:38
# @Last Modified by:   Eduardo Santos
# @Last Modified time: 2023-04-11 17:28:10

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


#### ADMIN ####
class CreateDriverForm(forms.Form):
    forename = forms.CharField( max_length=30, required=True, help_text='',widget=forms.TextInput(attrs={'class': 'form-control'}))
    surname = forms.CharField(max_length=30, required=True, help_text='', widget=forms.TextInput(attrs={'class': 'form-control'}))
    nationality = forms.CharField(max_length=30, required=True, help_text='', widget=forms.TextInput(attrs={'class': 'form-control'}))
    code = forms.CharField(max_length=5, required=True, help_text='', widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        fields = ('forename', 'surname', 'nationality', 'code')


class CreateTeamForm(forms.Form):
    name = forms.CharField( max_length=30, required=True, help_text='',widget=forms.TextInput(attrs={'class': 'form-control'}))
    nationality = forms.CharField(max_length=30, required=True, help_text='', widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        fields = ('name', 'nationality')

class DeleteDriverForm(forms.Form):
    code = forms.CharField(max_length=5, required=True, help_text='', widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        fields = ('code')

class DeleteTeamForm(forms.Form):
    name = forms.CharField( max_length=30, required=True, help_text='',widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        fields = ('name')