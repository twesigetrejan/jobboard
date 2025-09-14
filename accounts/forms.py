from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, EmployerProfile, JobSeekerProfile, USER_ROLES

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=USER_ROLES)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create UserProfile with selected role
            UserProfile.objects.create(
                user=user,
                role=self.cleaned_data['role']
            )
        return user

class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        exclude = ('user', 'created_at', 'updated_at')
        widgets = {
            'company_description': forms.Textarea(attrs={'rows': 4}),
            'website': forms.URLInput(attrs={'placeholder': 'https://www.example.com'}),
            'contact_email': forms.EmailInput(),
            'phone_number': forms.TextInput(attrs={'placeholder': '+1 (555) 123-4567'}),
        }

class JobSeekerProfileForm(forms.ModelForm):
    class Meta:
        model = JobSeekerProfile
        exclude = ('user', 'created_at', 'updated_at')
        widgets = {
            'skills': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Python, Django, JavaScript, React, etc.'
            }),
            'experience': forms.Textarea(attrs={'rows': 4}),
            'education': forms.Textarea(attrs={'rows': 3}),
            'linkedin_url': forms.URLInput(attrs={'placeholder': 'https://linkedin.com/in/yourprofile'}),
            'portfolio_url': forms.URLInput(attrs={'placeholder': 'https://your-portfolio.com'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+1 (555) 123-4567'}),
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username',  'email')
        widgets = {
            'email': forms.EmailInput(),
        }
