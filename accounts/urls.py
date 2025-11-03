from django.urls import path
from . import views

urlpatterns = [
    # Registration
    path('register/', views.register, name='register'),
    
    # Profile creation
    path('create-employer-profile/', views.create_employer_profile, name='create_employer_profile'),
    path('create-job-seeker-profile/', views.create_job_seeker_profile, name='create_job_seeker_profile'),
    
    # Dashboards
    path('employer-dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('job-seeker-dashboard/', views.job_seeker_dashboard, name='job_seeker_dashboard'),
    
    # Profile editing
    path('edit-employer-profile/', views.edit_employer_profile, name='edit_employer_profile'),
    path('edit-job-seeker-profile/', views.edit_job_seeker_profile, name='edit_job_seeker_profile'),
    
    # Profile viewing
    path('employer/<int:pk>/', views.employer_profile_detail, name='employer_profile_detail'),
    path('job-seeker/<int:pk>/', views.job_seeker_profile_detail, name='job_seeker_profile_detail'),

    # My Applications
    path('my-applications/', views.my_applications, name='my_applications'),
    # Employer analytics / visualizations
    path('employer-analytics/', views.employer_analytics, name='employer_analytics'),
    path('employer-analytics/data/', views.employer_analytics_data, name='employer_analytics_data'),
]
