from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 
            'sku', 
            'category',  
            'price',
            'minimum_stock',
        ]

        labels = {
            'sku': 'SKU',
        }

        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control product-form-control'}),
            'sku': forms.TextInput(
                attrs={'class': 'form-control product-form-control'}),
            'price': forms.NumberInput(
                attrs={'class': 'form-control product-form-control'}),
            'minimum_stock': forms.NumberInput(
                attrs={'class': 'form-control product-form-control'}),
        }

class StockForm(forms.Form):
    ACTION_CHOICES =[
        ("increase", "Increase Stock"),
        ("decrease", "Decrease Stock"),
    ]

    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.RadioSelect
    )

    edit_quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "min": 1
            }
        )
    )

class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control stockflow-input",
                'placeholder': "Your Name",
                "autocomplete": "name",
                }
            )
        )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control stockflow-input",
                'placeholder': "Your Email",
                "autocomplete": "email",
                }
            )
        )
    
    message = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(
            attrs={
                "class": "form-control stockflow-input",
                'placeholder': "Your Message",
                "rows": 6,
                }
            )
        )