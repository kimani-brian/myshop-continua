from django import forms
from .models import NewsletterSubscriber


class NewsletterSignupForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ["email"]
        widgets = {
            "email": forms.EmailInput(attrs={
                "placeholder": "Email address",
                "aria-label": "Email address",
                "class": "newsletter__input",
                "autocomplete": "email",
                "required": "required",
            })
        }

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        return email
