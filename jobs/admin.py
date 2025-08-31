from django.contrib import admin
from .models import Job, Application

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company_name', 'employer', 'location', 'job_type', 'is_active', 'created_at')
    list_filter = ('job_type', 'is_active', 'location', 'created_at')
    search_fields = ('title', 'company_name', 'description', 'employer__username')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_active',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('employer', 'title', 'company_name', 'job_type', 'is_active')
        }),
        ('Job Details', {
            'fields': ('description', 'requirements', 'location')
        }),
        ('Salary Information', {
            'fields': ('salary_min', 'salary_max'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('deadline', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'job', 'status', 'applied_at')
    list_filter = ('status', 'applied_at', 'job__job_type')
    search_fields = ('applicant__username', 'job__title', 'job__company_name')
    readonly_fields = ('applied_at', 'updated_at')
    list_editable = ('status',)
    date_hierarchy = 'applied_at'
    
    fieldsets = (
        (None, {
            'fields': ('job', 'applicant', 'status')
        }),
        ('Application Details', {
            'fields': ('cover_letter', 'notes')
        }),
        ('Dates', {
            'fields': ('applied_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
