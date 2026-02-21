from django import forms
from django.contrib.auth.models import User
from .models import Review, ContactMessage, UserProfile


class RegistrationForm(forms.Form):
    full_name = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Full Name'}
    ))
    username = forms.CharField(max_length=50, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username'}
    ))
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Email'}
    ))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Phone Number (optional)'}
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}
    ))
    confirm_password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}
    ))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get('password')
        confirm = cleaned.get('confirm_password')

        if password and len(password) < 8:
            self.add_error('password', 'Password must be at least 8 characters.')

        if password and confirm and password != confirm:
            self.add_error('confirm_password', 'Passwords do not match.')

        return cleaned


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username or Email'}
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}
    ))
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput(
        attrs={'class': 'form-check-input'}
    ))


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your Message', 'rows': 5}),
        }


# the rating field is hidden because the star picker in the template sets it via js
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.HiddenInput(),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your review here...',
                'rows': 4,
            }),
        }


class ProfileEditForm(forms.Form):
    full_name = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control'}
    ))
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'form-control'}
    ))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control'}
    ))
    profile_picture = forms.FileField(required=False, widget=forms.FileInput(
        attrs={'class': 'form-control'}
    ))
    new_password = forms.CharField(required=False, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Leave blank to keep current'}
    ))
    confirm_new_password = forms.CharField(required=False, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Confirm new password'}
    ))

    def clean(self):
        cleaned = super().clean()
        new_pw = cleaned.get('new_password')
        confirm_pw = cleaned.get('confirm_new_password')

        if new_pw:
            if len(new_pw) < 8:
                self.add_error('new_password', 'Password must be at least 8 characters.')
            if new_pw != confirm_pw:
                self.add_error('confirm_new_password', 'Passwords do not match.')

        return cleaned
