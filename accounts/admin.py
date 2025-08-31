from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, EmployerProfile, JobSeekerProfile

# Inline admin for UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profiles'

# Inline admin for EmployerProfile
class EmployerProfileInline(admin.StackedInline):
    model = EmployerProfile
    can_delete = False
    verbose_name_plural = 'Employer Profiles'

# Inline admin for JobSeekerProfile
class JobSeekerProfileInline(admin.StackedInline):
    model = JobSeekerProfile
    can_delete = False
    verbose_name_plural = 'Job Seeker Profiles'

# Extend UserAdmin to include profiles
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__username', 'user__email')

@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'location', 'contact_email', 'created_at')
    list_filter = ('location', 'created_at')
    search_fields = ('company_name', 'user__username', 'contact_email')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'location', 'created_at')
    list_filter = ('location', 'created_at')
    search_fields = ('full_name', 'user__username', 'skills')
    readonly_fields = ('created_at', 'updated_at')
