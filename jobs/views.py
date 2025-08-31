from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from .models import Job, Application
from .forms import JobForm, ApplicationForm, JobSearchForm, ApplicationStatusForm
from accounts.models import EmployerProfile, JobSeekerProfile

def home(request):
    """Home page with job listings and search functionality"""
    form = JobSearchForm(request.GET or None)
    jobs = Job.objects.filter(is_active=True)
    
    if form.is_valid():
        search_query = form.cleaned_data.get('search')
        location = form.cleaned_data.get('location')
        job_type = form.cleaned_data.get('job_type')
        salary_min = form.cleaned_data.get('salary_min')
        
        if search_query:
            jobs = jobs.filter(
                Q(title__icontains=search_query) |
                Q(company_name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        if location:
            jobs = jobs.filter(location__icontains=location)
        
        if job_type:
            jobs = jobs.filter(job_type=job_type)
        
        if salary_min:
            jobs = jobs.filter(salary_min__gte=salary_min)
    
    # Pagination
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'total_jobs': jobs.count(),
    }
    return render(request, 'jobs/home.html', context)

def job_detail(request, pk):
    """Job detail page"""
    job = get_object_or_404(Job, pk=pk, is_active=True)
    user_has_applied = False
    
    if request.user.is_authenticated:
        user_has_applied = Application.objects.filter(
            job=job,
            applicant=request.user
        ).exists()
    
    context = {
        'job': job,
        'user_has_applied': user_has_applied,
    }
    return render(request, 'jobs/job_detail.html', context)

@login_required
def create_job(request):
    """Create a new job posting (employers only)"""
    try:
        employer_profile = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Only employers can post jobs. Please create an employer profile.')
        return redirect('create_employer_profile')
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user
            # Auto-fill company name from employer profile
            job.company_name = employer_profile.company_name
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('job_detail', pk=job.pk)
    else:
        # Pre-fill company name
        form = JobForm(initial={'company_name': employer_profile.company_name})
    
    return render(request, 'jobs/create_job.html', {'form': form})

@login_required
def edit_job(request, pk):
    """Edit job posting (job owner only)"""
    job = get_object_or_404(Job, pk=pk, employer=request.user)
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('job_detail', pk=job.pk)
    else:
        form = JobForm(instance=job)
    
    return render(request, 'jobs/edit_job.html', {'form': form, 'job': job})

@login_required
def delete_job(request, pk):
    """Delete job posting (job owner only)"""
    job = get_object_or_404(Job, pk=pk, employer=request.user)
    
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted successfully!')
        return redirect('employer_dashboard')
    
    return render(request, 'jobs/delete_job.html', {'job': job})

@login_required
def apply_for_job(request, pk):
    """Apply for a job (job seekers only)"""
    job = get_object_or_404(Job, pk=pk, is_active=True)
    
    # Check if user is a job seeker
    try:
        job_seeker_profile = JobSeekerProfile.objects.get(user=request.user)
    except JobSeekerProfile.DoesNotExist:
        messages.error(request, 'Only job seekers can apply for jobs. Please create a job seeker profile.')
        return redirect('create_job_seeker_profile')
    
    # Check if user has already applied
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.error(request, 'You have already applied for this job.')
        return redirect('job_detail', pk=pk)
    
    # Check if deadline has passed
    if job.is_deadline_passed():
        messages.error(request, 'The application deadline for this job has passed.')
        return redirect('job_detail', pk=pk)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, 'Your application has been submitted successfully!')
            return redirect('job_detail', pk=pk)
    else:
        form = ApplicationForm()
    
    context = {
        'form': form,
        'job': job,
        'job_seeker_profile': job_seeker_profile,
    }
    return render(request, 'jobs/apply_for_job.html', context)

@login_required
def my_applications(request):
    """View user's job applications"""
    try:
        job_seeker_profile = JobSeekerProfile.objects.get(user=request.user)
    except JobSeekerProfile.DoesNotExist:
        messages.error(request, 'Please create a job seeker profile first.')
        return redirect('create_job_seeker_profile')
    
    applications = Application.objects.filter(applicant=request.user)
    
    # Pagination
    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'jobs/my_applications.html', {'page_obj': page_obj})

@login_required
def application_detail(request, pk):
    """View application details"""
    application = get_object_or_404(Application, pk=pk)
    
    # Check permissions
    if application.applicant != request.user and application.job.employer != request.user:
        raise Http404("Application not found")
    
    return render(request, 'jobs/application_detail.html', {'application': application})

@login_required
def job_applications(request, pk):
    """View applications for a specific job (employer only)"""
    job = get_object_or_404(Job, pk=pk, employer=request.user)
    applications = Application.objects.filter(job=job)
    
    # Pagination
    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'job': job,
        'page_obj': page_obj,
    }
    return render(request, 'jobs/job_applications.html', context)

@login_required
def update_application_status(request, pk):
    """Update application status (employer only)"""
    application = get_object_or_404(Application, pk=pk)
    
    # Check if user is the job owner
    if application.job.employer != request.user:
        raise Http404("Application not found")
    
    if request.method == 'POST':
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, 'Application status updated successfully!')
            return redirect('job_applications', pk=application.job.pk)
    else:
        form = ApplicationStatusForm(instance=application)
    
    context = {
        'form': form,
        'application': application,
    }
    return render(request, 'jobs/update_application_status.html', context)

@login_required
def withdraw_application(request, pk):
    """Withdraw job application (applicant only)"""
    application = get_object_or_404(Application, pk=pk, applicant=request.user)
    
    if request.method == 'POST':
        job_pk = application.job.pk
        application.delete()
        messages.success(request, 'Application withdrawn successfully!')
        return redirect('job_detail', pk=job_pk)
    
    return render(request, 'jobs/withdraw_application.html', {'application': application})
