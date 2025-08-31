from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# User role choices
USER_ROLES = (
    ('employer', 'Employer'),
    ('job_seeker', 'Job Seeker'),
)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=USER_ROLES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

class EmployerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)
    company_description = models.TextField()
    location = models.CharField(max_length=200)
    website = models.URLField(blank=True, null=True)
    contact_email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.company_name
    
    def get_absolute_url(self):
        return reverse('employer_profile', kwargs={'pk': self.pk})

class JobSeekerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    skills = models.TextField(help_text="Enter skills separated by commas")
    experience = models.TextField(blank=True, null=True)
    education = models.TextField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.full_name
    
    def get_absolute_url(self):
        return reverse('job_seeker_profile', kwargs={'pk': self.pk})
    
    def get_skills_list(self):
        return [skill.strip() for skill in self.skills.split(',') if skill.strip()]
