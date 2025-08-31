from django.urls import path
from . import views

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # Job-related URLs
    path('job/<int:pk>/', views.job_detail, name='job_detail'),
    path('job/create/', views.create_job, name='create_job'),
    path('job/<int:pk>/edit/', views.edit_job, name='edit_job'),
    path('job/<int:pk>/delete/', views.delete_job, name='delete_job'),
    
    # Application-related URLs
    path('job/<int:pk>/apply/', views.apply_for_job, name='apply_for_job'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('application/<int:pk>/', views.application_detail, name='application_detail'),
    path('application/<int:pk>/withdraw/', views.withdraw_application, name='withdraw_application'),
    
    # Employer application management URLs
    path('job/<int:pk>/applications/', views.job_applications, name='job_applications'),
    path('application/<int:pk>/update-status/', views.update_application_status, name='update_application_status'),
]
