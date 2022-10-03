# django imports
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SearchForm(forms.Form):
    autofocus = True
    search_name = forms.CharField(widget=forms.TextInput(attrs={'size': 30, 'autofocus': autofocus,
                                                                'placeholder': 'Ex: John Smith or plumbing',
                                                                'class': 'nav'}),
                                  label='Search by name or skill ',
                                  required=True,
                                  initial='',
                                  )

    def clean_name(self):
        name = self.cleaned_data['search_name']
        return name


class AccountCreationForm(UserCreationForm, forms.Form):
    """
        Extends the basic UserCreationForm into something that will accept more information for user creation
    """
    error_messages = {
        'username_exists': 'The requested username is already taken'
    }

    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'size': '50', 'placeholder': 'Ex: someone@domain.com'}),
        label='E-mail Address',
        required=True,
        initial='')
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'size': '40'}),
        label='First Name',
        required=True,
        initial='')
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'size': '40'}),
        label='Last Name',
        required=True,
        initial='')

    def clean_username(self):
        username = self.cleaned_data['username']
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        return last_name

    def check_username(self):
        username = self.clean_username
        print(username)
        # Check if username already is in the database
        try:
            test_user = User.objects.get(username=username)
            print(test_user)
            raise forms.ValidationError(
                self.error_messages['username_exists'],
                code='username_exists'
            )
        except User.DoesNotExist:
            return True
