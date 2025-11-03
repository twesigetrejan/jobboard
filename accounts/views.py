from django.contrib.auth.decorators import login_required
# My Applications view for job seekers
@login_required
def my_applications(request):
    applications = Application.objects.filter(applicant=request.user).select_related('job').order_by('-created_at')
    context = {
        'applications': applications,
    }
    return render(request, 'accounts/my_applications.html', context)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from .forms import CustomUserCreationForm, EmployerProfileForm, JobSeekerProfileForm, UserUpdateForm
from .models import UserProfile, EmployerProfile, JobSeekerProfile
from jobs.models import Job, Application
from django.http import JsonResponse
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta

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
    
    if request.method == 'POST':
        if not user_form.is_valid() or not profile_form.is_valid():
            print('User form errors:', user_form.errors)
            print('Profile form errors:', profile_form.errors)
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
    
    if request.method == 'POST':
        if not user_form.is_valid() or not profile_form.is_valid():
            print('User form errors:', user_form.errors)
            print('Profile form errors:', profile_form.errors)
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
    # For compatibility with the template, pass as 'profile'
    context = {
        'profile': job_seeker_profile,
        'user': request.user,
    }
    return render(request, 'accounts/job_seeker_profile_detail.html', context)


@login_required
def employer_analytics(request):
    """Render a page with multiple employer visualizations."""
    try:
        employer_profile = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Please complete your employer profile first.')
        return redirect('create_employer_profile')

    return render(request, 'accounts/employer_analytics.html', {'employer_profile': employer_profile})


@login_required
def employer_analytics_data(request):
    """Return aggregated data for employer visualizations as JSON."""
    # Only include data for jobs owned by the current user
    apps = Application.objects.filter(job__employer=request.user)
    status_counts_qs = apps.values('status').annotate(count=Count('pk'))
    status_counts = {item['status']: item['count'] for item in status_counts_qs}
    # Ensure keys exist
    status_counts_full = {
        'pending': status_counts.get('pending', 0),
        'reviewed': status_counts.get('reviewed', 0),
        'accepted': status_counts.get('accepted', 0),
        'rejected': status_counts.get('rejected', 0),
    }

    # Jobs by type
    jobs_by_type_qs = Job.objects.filter(employer=request.user).values('job_type').annotate(count=Count('pk'))
    jobs_by_type = {item['job_type']: item['count'] for item in jobs_by_type_qs}

    # Applications over time (last 30 days)
    start_date = timezone.now() - timedelta(days=30)
    apps_time_qs = apps.filter(applied_at__gte=start_date).annotate(date=TruncDate('applied_at')).values('date').annotate(count=Count('pk')).order_by('date')
    apps_over_time = [{ 'date': item['date'].isoformat(), 'count': item['count'] } for item in apps_time_qs]
    # Conversion funnel metrics
    total_apps = apps.count()
    pending = status_counts_full.get('pending', 0)
    reviewed = status_counts_full.get('reviewed', 0)
    accepted = status_counts_full.get('accepted', 0)
    rejected = status_counts_full.get('rejected', 0)
    review_rate = (reviewed / total_apps) if total_apps else 0
    accept_rate = (accepted / total_apps) if total_apps else 0
    funnel = {
        'total': total_apps,
        'pending': pending,
        'reviewed': reviewed,
        'accepted': accepted,
        'rejected': rejected,
        'review_rate': review_rate,
        'accept_rate': accept_rate,
    }

    # Applications by location (top 10)
    loc_qs = apps.values('applicant__jobseekerprofile__location').annotate(count=Count('pk')).order_by('-count')[:10]
    location_counts = []
    for item in loc_qs:
        loc = item.get('applicant__jobseekerprofile__location') or 'Unknown'
        location_counts.append({'location': loc, 'count': item['count']})

    # Top jobs by number of applications
    top_jobs_qs = Job.objects.filter(employer=request.user).annotate(app_count=Count('applications')).order_by('-app_count')[:10]
    top_jobs = [{'id': j.pk, 'title': j.title, 'count': j.app_count} for j in top_jobs_qs]

    data = {
        'status_counts': status_counts_full,
        'jobs_by_type': jobs_by_type,
        'applications_over_time': apps_over_time,
        'funnel': funnel,
        'location_counts': location_counts,
        'top_jobs': top_jobs,
    }
    return JsonResponse(data)
