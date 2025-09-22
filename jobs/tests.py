from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import EmployerProfile,JobSeekerProfile
from .models import Job, Application

class CreateJobViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='employer', password='testpass')
        self.employer_profile = EmployerProfile.objects.create(user=self.user, company_name='TestCo')
        self.client.login(username='employer', password='testpass')

    def test_create_job_success(self):
        response = self.client.post(reverse('create_job'), {
            'title': 'Test Job',
            'company_name': 'TestCo',
            'description': 'Test Description',
            'requirements': 'Test Requirements',
            'location': 'Test Location',
            'job_type': 'full_time',
            'salary_min': 50000,
            'salary_max': 80000,
            'is_active': True,
        })
        self.assertEqual(response.status_code, 302)  # Redirect to job_detail
        job = Job.objects.get(title='Test Job')
        self.assertEqual(job.employer, self.user)
        self.assertEqual(job.company_name, 'TestCo')

    def test_create_job_requires_employer_profile(self):
        # Remove employer profile
        self.employer_profile.delete()
        response = self.client.get(reverse('create_job'))
        self.assertRedirects(response, reverse('create_employer_profile'))



class EditJobViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='employer', password='testpass')
        self.employer_profile = EmployerProfile.objects.create(user=self.user, company_name='TestCo')
        self.job = Job.objects.create(
            employer=self.user,
            title='Original Title',
            company_name='TestCo',
            description='Original Description',
            requirements='Original Requirements',
            location='Original Location',
            job_type='full_time'
        )
        self.client.login(username='employer', password='testpass')

    def test_edit_job_success(self):
        response = self.client.post(reverse('edit_job', args=[self.job.pk]), {
            'title': 'Updated Title',
            'company_name': 'TestCo',
            'description': 'Updated Description',
            'requirements': 'Updated Requirements',
            'location': 'Updated Location',
            'job_type': 'full_time',
            'salary_min': '1000',
            'salary_max': '2000',
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after successful edit
        self.job.refresh_from_db()
        self.assertEqual(self.job.title, 'Updated Title')
        self.assertEqual(self.job.description, 'Updated Description')





class ApplyForJobViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='seeker', password='testpass')
        self.job_seeker_profile = JobSeekerProfile.objects.create(user=self.user)
        self.job = Job.objects.create(
            employer_id=1,  # You may need to create an employer user
            title='Test Job',
            company_name='TestCo',
            description='Test Description',
            requirements='Test Requirements',
            location='Test Location',
            job_type='full_time',
            is_active=True
        )
        self.client.login(username='seeker', password='testpass')

    def test_apply_for_job_success(self):
        response = self.client.post(reverse('apply_for_job', args=[self.job.pk]), {
            'cover_letter': 'I am interested in this job.'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect to job_detail
        self.assertTrue(Application.objects.filter(job=self.job, applicant=self.user).exists())

    def test_cannot_apply_twice(self):
        Application.objects.create(job=self.job, applicant=self.user, cover_letter='Already applied')
        response = self.client.post(reverse('apply_for_job', args=[self.job.pk]), {
            'cover_letter': 'Trying to apply again.'
        })
        self.assertRedirects(response, reverse('job_detail', args=[self.job.pk]))
        self.assertEqual(Application.objects.filter(job=self.job, applicant=self.user).count(), 1)


class JobApplicationsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.employer = User.objects.create_user(username='employer', password='testpass')
        self.employer_profile = EmployerProfile.objects.create(user=self.employer, company_name='TestCo')
        self.job = Job.objects.create(
            employer=self.employer,
            title='Test Job',
            company_name='TestCo',
            description='Test Description',
            requirements='Test Requirements',
            location='Test Location',
            job_type='full_time'
        )
        # Create applications with different statuses
        Application.objects.create(job=self.job, applicant_id=2, cover_letter='Pending', status='pending')
        Application.objects.create(job=self.job, applicant_id=3, cover_letter='Accepted', status='accepted')
        Application.objects.create(job=self.job, applicant_id=4, cover_letter='Rejected', status='rejected')
        self.client.login(username='employer', password='testpass')

    def test_job_applications_view(self):
        response = self.client.get(reverse('job_applications', args=[self.job.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['pending_applications'], 1)
        self.assertEqual(response.context['accepted_applications'], 1)
        self.assertEqual(response.context['rejected_applications'], 1)
        self.assertContains(response, 'Test Job')
