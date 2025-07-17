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

        
