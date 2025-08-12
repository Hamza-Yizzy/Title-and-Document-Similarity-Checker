from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['book_title', 'authors', 'area', 'year', 'file']
        widgets = {
            'book_title': forms.TextInput(attrs={
                'class': 'form-control text-lg py-2 px-4 rounded-lg border border-gray-300 w-full'
            }),
            'authors': forms.TextInput(attrs={
                'class': 'form-control text-lg py-2 px-4 rounded-lg border border-gray-300 w-full'
            }),
            'area': forms.TextInput(attrs={
                'class': 'form-control text-lg py-2 px-4 rounded-lg border border-gray-300 w-full'
            }),
            'year': forms.Select(attrs={
                'class': 'form-select text-lg py-2 px-4 rounded-lg border border-gray-300 w-full'
            }),
            'file': forms.ClearableFileInput(attrs={
                'class': 'form-control text-lg py-2 px-4 rounded-lg border border-gray-300 w-full'
            }),
        }
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class EditUserWithPasswordForm(UserCreationForm):
    username = forms.CharField(
        min_length=6,
        help_text="Username must be at least 6 characters.",
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )

    password1 = forms.CharField(
        label="New Password",
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Leave blank to keep current password'})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Leave blank to keep current password'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) < 6:
            raise forms.ValidationError("Username must be at least 6 characters long.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 or p2:
            if p1 != p2:
                self.add_error('password2', "Passwords do not match.")
        return cleaned_data


from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
