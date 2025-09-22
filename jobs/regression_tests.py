from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import EmployerProfile, JobSeekerProfile
from jobs.models import Job, Application


class RegressionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.employer = User.objects.create_user(username='employer', password='testpass', email='emp@test.com')
        self.employer_profile = EmployerProfile.objects.create(user=self.employer, company_name='TestCo', company_description='desc', location='loc', contact_email='emp@test.com')
        self.job = Job.objects.create(
            employer=self.employer,
            title='Test Job',
            company_name='TestCo',
            description='Test Description',
            requirements='Test Requirements',
            location='Test Location',
            job_type='full_time',
            salary_min=1000,
            salary_max=2000,
            is_active=True
        )
        self.applicant = User.objects.create_user(username='applicant', password='testpass', email='app@test.com')
        self.job_seeker_profile = JobSeekerProfile.objects.create(user=self.applicant, full_name='Applicant Name', skills='Python', experience='exp')

    def test_cannot_create_job_without_employer_profile(self):
        self.employer_profile.delete()
        self.client.login(username='employer', password='testpass')
        response = self.client.get(reverse('create_job'))
        self.assertRedirects(response, reverse('create_employer_profile'))

    def test_cannot_edit_job_as_non_owner(self):
        other = User.objects.create_user(username='other', password='testpass')
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

    def test_delete_job_removes_applications(self):
        app = Application.objects.create(job=self.job, applicant=self.applicant, cover_letter='Test')
        self.client.login(username='employer', password='testpass')
        response = self.client.post(reverse('delete_job', args=[self.job.pk]))
        self.assertRedirects(response, reverse('employer_dashboard'))
        self.assertFalse(Application.objects.filter(pk=app.pk).exists())

    def test_update_application_status_unauthorized(self):
        other_employer = User.objects.create_user(username='other_employer', password='testpass')
        app = Application.objects.create(job=self.job, applicant=self.applicant, cover_letter='Test', status='pending')
        self.client.login(username='other_employer', password='testpass')
        response = self.client.post(reverse('update_application_status', args=[app.pk]), {
            'status': 'accepted'
        })
        self.assertEqual(response.status_code, 404)
        app.refresh_from_db()
        self.assertEqual(app.status, 'pending')

    def test_job_application_invalid_job_type(self):
        self.client.login(username='employer', password='testpass')
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

    def test_job_creation_missing_required_fields(self):
        self.client.login(username='employer', password='testpass')
        response = self.client.post(reverse('create_job'), {
            'title': '',
            'company_name': '',
            'description': '',
            'requirements': '',
            'location': '',
            'job_type': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required', status_code=200)

    def test_job_edit_requires_authentication(self):
        self.client.logout()
        response = self.client.get(reverse('edit_job', args=[self.job.pk]))
        self.assertNotEqual(response.status_code, 200)

    def test_job_delete_requires_authentication(self):
        self.client.logout()
        response = self.client.post(reverse('delete_job', args=[self.job.pk]))
        self.assertNotEqual(response.status_code, 200)
        self.assertTrue(Job.objects.filter(pk=self.job.pk).exists())

    def test_application_creation_requires_login(self):
        self.client.logout()
        response = self.client.post(reverse('apply_for_job', args=[self.job.pk]), {
            'cover_letter': 'Test cover letter',
        })
        self.assertNotEqual(response.status_code, 200)

    def test_job_seeker_cannot_view_other_applications(self):
        self.client.login(username='applicant', password='testpass')
        response = self.client.get(reverse('job_applications', args=[self.job.pk]))
        self.assertNotEqual(response.status_code, 200)

    def test_employer_can_view_applications(self):
        self.client.login(username='employer', password='testpass')
        response = self.client.get(reverse('job_applications', args=[self.job.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Job')

    def test_job_seeker_profile_edit_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('edit_job_seeker_profile'))
        self.assertNotEqual(response.status_code, 200)

    def test_employer_profile_edit_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('edit_employer_profile'))
        self.assertNotEqual(response.status_code, 200)

    def test_job_seeker_cannot_edit_employer_profile(self):
        self.client.login(username='applicant', password='testpass')
        response = self.client.get(reverse('edit_employer_profile'))
        self.assertEqual(response.status_code, 404)

    def test_employer_cannot_edit_job_seeker_profile(self):
        self.client.login(username='employer', password='testpass')
        response = self.client.get(reverse('edit_job_seeker_profile'))
        self.assertEqual(response.status_code, 404)

    def test_job_seeker_cannot_delete_job(self):
        self.client.login(username='applicant', password='testpass')
        response = self.client.post(reverse('delete_job', args=[self.job.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Job.objects.filter(pk=self.job.pk).exists())

    def test_employer_cannot_apply_to_own_job(self):
        self.client.login(username='employer', password='testpass')
        response = self.client.post(reverse('apply_for_job', args=[self.job.pk]), {
            'cover_letter': 'Trying to apply to own job',
        })
        self.assertNotEqual(response.status_code, 200)
