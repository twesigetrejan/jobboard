from django import forms
from .models import Job, Application

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        exclude = ('employer', 'created_at', 'updated_at')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Describe the job role, responsibilities, and what makes this position unique...'
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'List the required skills, qualifications, and experience...'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City, State or Remote'
            }),
            'salary_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '50000'
            }),
            'salary_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '80000'
            }),
            'job_type': forms.Select(attrs={'class': 'form-control'}),
            'deadline': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].help_text = "Provide a detailed description of the job"
        self.fields['requirements'].help_text = "List the skills and qualifications needed"
        self.fields['salary_min'].help_text = "Minimum salary (optional)"
        self.fields['salary_max'].help_text = "Maximum salary (optional)"
        self.fields['deadline'].help_text = "Application deadline (optional)"

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ('cover_letter',)
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Write your cover letter here. Explain why you are interested in this position and what makes you a good fit...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cover_letter'].help_text = "Tell the employer why you're the right person for this job"

class JobSearchForm(forms.Form):
    search = forms.CharField(
        max_length=200, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search jobs by title, company, or keywords...'
        })
    )
    location = forms.CharField(
        max_length=200, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City, State or Remote'
        })
    )
    job_type = forms.ChoiceField(
        choices=[('', 'All Types')] + list(Job._meta.get_field('job_type').choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    salary_min = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Salary'
        })
    )

class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ('status', 'notes')
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Internal notes about this application...'
            })
        }
