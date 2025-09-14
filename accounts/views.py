from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from .forms import CustomUserCreationForm, EmployerProfileForm, JobSeekerProfileForm, UserUpdateForm
from .models import UserProfile, EmployerProfile, JobSeekerProfile
from jobs.models import Job, Application

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome {user.username}')
            # return redirect('login')
            
            # Redirect to profile creation based on role
        if user.userprofile.role == 'employer':
                return redirect('create_employer_profile')
        else:
                return redirect('create_job_seeker_profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def create_employer_profile(request):
    # Check if user already has an employer profile
    try:
        profile = EmployerProfile.objects.get(user=request.user)
        return redirect('employer_dashboard')
    except EmployerProfile.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = EmployerProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'Employer profile created successfully!')
            return redirect('login')
    else:
        form = EmployerProfileForm()
    return render(request, 'accounts/create_employer_profile.html', {'form': form})

@login_required
def create_job_seeker_profile(request):
    # Check if user already has a job seeker profile
    try:
        profile = JobSeekerProfile.objects.get(user=request.user)
        return redirect('job_seeker_dashboard')
    except JobSeekerProfile.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = JobSeekerProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'Profile created successfully!')
            return redirect('login')
    else:
        form = JobSeekerProfileForm()
    return render(request, 'accounts/create_job_seeker_profile.html', {'form': form})

@login_required
def employer_dashboard(request):
    try:
        employer_profile = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Please complete your employer profile first.')
        return redirect('create_employer_profile')
    
    jobs = Job.objects.filter(employer=request.user)
    recent_applications = Application.objects.filter(job__employer=request.user)[:5]
    
    context = {
        'employer_profile': employer_profile,
        'jobs': jobs,
        'recent_applications': recent_applications,
        'total_jobs': jobs.count(),
        'active_jobs': jobs.filter(is_active=True).count(),
        'total_applications': Application.objects.filter(job__employer=request.user).count(),
        
    }
    return render(request, 'accounts/employer_dashboard.html', context)

@login_required
def job_seeker_dashboard(request):
    try:
        job_seeker_profile = JobSeekerProfile.objects.get(user=request.user)
    except JobSeekerProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('create_job_seeker_profile')
    
    applications = Application.objects.filter(applicant=request.user)
    
    context = {
        'job_seeker_profile': job_seeker_profile,
        'applications': applications,
        'total_applications': applications.count(),
        'pending_applications': applications.filter(status='pending').count(),
        'accepted_applications': applications.filter(status='accepted').count(),
    }
    return render(request, 'accounts/job_seeker_dashboard.html', context)

@login_required
def edit_employer_profile(request):
    employer_profile = get_object_or_404(EmployerProfile, user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = EmployerProfileForm(request.POST, request.FILES, instance=employer_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user_form.save()
                profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('employer_dashboard')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = EmployerProfileForm(instance=employer_profile)
    
    return render(request, 'accounts/edit_employer_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def edit_job_seeker_profile(request):
    job_seeker_profile = get_object_or_404(JobSeekerProfile, user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = JobSeekerProfileForm(request.POST, request.FILES, instance=job_seeker_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user_form.save()
                profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('job_seeker_dashboard')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = JobSeekerProfileForm(instance=job_seeker_profile)
    
    return render(request, 'accounts/edit_job_seeker_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def employer_profile_detail(request, pk):
    employer_profile = get_object_or_404(EmployerProfile, pk=pk)
    jobs = Job.objects.filter(employer=employer_profile.user, is_active=True)
    
    context = {
        'employer_profile': employer_profile,
        'jobs': jobs,
    }
    return render(request, 'accounts/employer_profile_detail.html', context)

def job_seeker_profile_detail(request, pk):
    job_seeker_profile = get_object_or_404(JobSeekerProfile, pk=pk)
    
    context = {
        'job_seeker_profile': job_seeker_profile,
    }
    return render(request, 'accounts/job_seeker_profile_detail.html', context)
