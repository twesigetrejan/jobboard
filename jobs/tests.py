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

    def test_create_job_missing_required_fields(self):
        response = self.client.post(reverse('create_job'), {
            'title': '',  # Missing title
            'company_name': '',  # Missing company name
            'description': '',
            'requirements': '',
            'location': '',
            'job_type': '',
        })
        self.assertEqual(response.status_code, 200)  # Should not redirect
        self.assertContains(response, 'This field is required', status_code=200)

    def test_create_job_invalid_job_type(self):
        response = self.client.post(reverse('create_job'), {
            'title': 'Test Job',
            'company_name': 'TestCo',
            'description': 'Test Description',
            'requirements': 'Test Requirements',
            'location': 'Test Location',
            'job_type': 'invalid_type',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Select a valid choice', status_code=200)



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

    def test_edit_job_unauthorized(self):
        other_user = User.objects.create_user(username='other', password='testpass')
        self.client.login(username='other', password='testpass')
        response = self.client.post(reverse('edit_job', args=[self.job.pk]), {
            'title': 'Hacked Title',
            'company_name': 'TestCo',
            'description': 'Hacked',
            'requirements': 'Hacked',
            'location': 'Hacked',
            'job_type': 'full_time',
        })
        self.assertEqual(response.status_code, 404)
        self.job.refresh_from_db()
        self.assertNotEqual(self.job.title, 'Hacked Title')

    def test_delete_job_success(self):
        response = self.client.post(reverse('delete_job', args=[self.job.pk]))
        self.assertRedirects(response, reverse('employer_dashboard'))
        with self.assertRaises(Job.DoesNotExist):
            Job.objects.get(pk=self.job.pk)

    def test_delete_job_unauthorized(self):
        other_user = User.objects.create_user(username='other', password='testpass')
        self.client.login(username='other', password='testpass')
        response = self.client.post(reverse('delete_job', args=[self.job.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Job.objects.filter(pk=self.job.pk).exists())

    def test_delete_job_removes_applications(self):
        applicant = User.objects.create_user(username='applicant', password='testpass')
        app = Application.objects.create(job=self.job, applicant=applicant, cover_letter='Test')
        self.assertTrue(Application.objects.filter(pk=app.pk).exists())
        response = self.client.post(reverse('delete_job', args=[self.job.pk]))
        self.assertRedirects(response, reverse('employer_dashboard'))
        self.assertFalse(Application.objects.filter(pk=app.pk).exists())



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
        # Create test applicants
        self.applicant1 = User.objects.create_user(username='applicant1', password='testpass')
        self.applicant2 = User.objects.create_user(username='applicant2', password='testpass')
        self.applicant3 = User.objects.create_user(username='applicant3', password='testpass')
        
        # Create applications with different statuses
        Application.objects.create(job=self.job, applicant=self.applicant1, cover_letter='Pending', status='pending')
        Application.objects.create(job=self.job, applicant=self.applicant2, cover_letter='Accepted', status='accepted')
        Application.objects.create(job=self.job, applicant=self.applicant3, cover_letter='Rejected', status='rejected')
        self.client.login(username='employer', password='testpass')

    def test_job_applications_view(self):
        response = self.client.get(reverse('job_applications', args=[self.job.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['pending_applications'], 1)
        self.assertEqual(response.context['accepted_applications'], 1)
        self.assertEqual(response.context['rejected_applications'], 1)
        self.assertContains(response, 'Test Job')

class UpdateApplicationStatusViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create employer and job
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
        # Create applicant and application
        self.applicant = User.objects.create_user(username='applicant', password='testpass')
        self.application = Application.objects.create(
            job=self.job,
            applicant=self.applicant,
            cover_letter='Test cover letter',
            status='pending'
        )
        # Create another employer (unauthorized user)
        self.other_employer = User.objects.create_user(username='other_employer', password='testpass')

    def test_update_application_status_success(self):
        self.client.login(username='employer', password='testpass')
        response = self.client.post(reverse('update_application_status', args=[self.application.pk]), {
            'status': 'accepted'
        })
        # Redirect to job applications
        self.assertRedirects(response, reverse('job_applications', args=[self.job.pk]))
        # Check that status was updated
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'accepted')

    def test_update_application_status_unauthorized(self):
        # Login as different employer
        self.client.login(username='other_employer', password='testpass')
        response = self.client.post(reverse('update_application_status', args=[self.application.pk]), {
            'status': 'accepted'
        })
    
        self.assertEqual(response.status_code, 404)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'pending')

    def test_update_application_status_get_request(self):
        self.client.login(username='employer', password='testpass')
        response = self.client.get(reverse('update_application_status', args=[self.application.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'pending')  # Should show current status
        self.assertContains(response, self.applicant.username)
