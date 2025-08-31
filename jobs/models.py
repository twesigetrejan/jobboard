from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

# Job type choices
JOB_TYPE_CHOICES = (
    ('full_time', 'Full Time'),
    ('part_time', 'Part Time'),
    ('contract', 'Contract'),
    ('internship', 'Internship'),
    ('freelance', 'Freelance'),
)

# Application status choices
APPLICATION_STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('reviewed', 'Reviewed'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
)

class Job(models.Model):
    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField()
    location = models.CharField(max_length=200)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} at {self.company_name}"
    
    def get_absolute_url(self):
        return reverse('job_detail', kwargs={'pk': self.pk})
    
    def get_salary_range(self):
        if self.salary_min and self.salary_max:
            return f"${self.salary_min:,.0f} - ${self.salary_max:,.0f}"
        elif self.salary_min:
            return f"From ${self.salary_min:,.0f}"
        elif self.salary_max:
            return f"Up to ${self.salary_max:,.0f}"
        return "Salary not specified"
    
    def is_deadline_passed(self):
        if self.deadline:
            return timezone.now() > self.deadline
        return False
    
    def applications_count(self):
        return self.applications.count()

class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField()
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True, help_text="Internal notes by employer")
    
    class Meta:
        unique_together = ('job', 'applicant')
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.applicant.username} - {self.job.title}"
    
    def get_absolute_url(self):
        return reverse('application_detail', kwargs={'pk': self.pk})
