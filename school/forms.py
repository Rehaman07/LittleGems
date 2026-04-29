from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from .models import AdmissionApplication, Enquiry


phone_validator = RegexValidator(
    regex=r'^\+?[\d\s\-]{7,15}$',
    message="Enter a valid phone number (7–15 digits, may include +, spaces, or dashes)."
)


class AdmissionForm(forms.ModelForm):
    """
    Validated admission application form.
    Field names match the raw <input name="..."> attributes in admissions.html.
    """
    phone = forms.CharField(
        max_length=15,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={'placeholder': 'e.g. +91 70326 91555'})
    )

    class Meta:
        model = AdmissionApplication
        fields = ['child_name', 'date_of_birth', 'parent_name', 'email', 'phone', 'program', 'message']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'message': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_child_name(self):
        name = self.cleaned_data.get('child_name', '').strip()
        if len(name) < 2:
            raise forms.ValidationError("Please enter the child's full name.")
        return name

    def clean_parent_name(self):
        name = self.cleaned_data.get('parent_name', '').strip()
        if len(name) < 2:
            raise forms.ValidationError("Please enter the parent/guardian's full name.")
        return name


class EnquiryForm(forms.ModelForm):
    """
    Validated enquiry / contact form.
    Field names match the raw <input name="..."> attributes in contact.html.
    """
    phone = forms.CharField(
        max_length=15,
        validators=[phone_validator],
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Phone Number'})
    )

    class Meta:
        model = Enquiry
        fields = ['name', 'email', 'phone', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 2:
            raise forms.ValidationError("Please enter your full name.")
        return name

    def clean_message(self):
        msg = self.cleaned_data.get('message', '').strip()
        if len(msg) < 10:
            raise forms.ValidationError("Please write a more detailed message (at least 10 characters).")
        return msg


class UserRegistrationForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Full Name', 'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email Address', 'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'}),
        required=True
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.username = self.cleaned_data["email"]  # Use email as username
        user.first_name = self.cleaned_data["full_name"]
        if commit:
            user.save()
        return user
