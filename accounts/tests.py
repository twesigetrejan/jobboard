# --- Edit Profile Tests ---
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import EmployerProfile, JobSeekerProfile

class EditEmployerProfileViewTest(TestCase):
	def setUp(self):
		self.client = Client()
		self.user = User.objects.create_user(username='employer', password='testpass', email='emp@test.com')
		self.profile = EmployerProfile.objects.create(user=self.user, company_name='TestCo', company_description='desc', location='loc', contact_email='emp@test.com')
		self.client.login(username='employer', password='testpass')

	def test_edit_employer_profile_get(self):
		response = self.client.get(reverse('edit_employer_profile'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'TestCo')

	def test_edit_employer_profile_post_success(self):
		response = self.client.post(reverse('edit_employer_profile'), {
			'company_name': 'NewCo',
			'company_description': 'newdesc',
			'location': 'newloc',
			'contact_email': 'new@test.com',
		})
		self.assertRedirects(response, reverse('employer_dashboard'))
		self.profile.refresh_from_db()
		self.assertEqual(self.profile.company_name, 'NewCo')
		self.assertEqual(self.profile.contact_email, 'new@test.com')

	def test_edit_employer_profile_permission(self):
		other = User.objects.create_user(username='other', password='testpass')
		self.client.login(username='other', password='testpass')
		response = self.client.get(reverse('edit_employer_profile'))
		self.assertEqual(response.status_code, 404)

class EditJobSeekerProfileViewTest(TestCase):
	def setUp(self):
		self.client = Client()
		self.user = User.objects.create_user(username='seeker', password='testpass', email='seek@test.com')
		self.profile = JobSeekerProfile.objects.create(user=self.user, full_name='Seek Name', skills='Python', experience='exp')
		self.client.login(username='seeker', password='testpass')

	def test_edit_job_seeker_profile_get(self):
		response = self.client.get(reverse('edit_job_seeker_profile'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Seek Name')

	def test_edit_job_seeker_profile_post_success(self):
		response = self.client.post(reverse('edit_job_seeker_profile'), {
			'full_name': 'New Name',
			'skills': 'Django',
			'experience': 'newexp',
		})
		self.assertRedirects(response, reverse('job_seeker_dashboard'))
		self.profile.refresh_from_db()
		self.assertEqual(self.profile.full_name, 'New Name')
		self.assertEqual(self.profile.skills, 'Django')

	def test_edit_job_seeker_profile_permission(self):
		other = User.objects.create_user(username='other', password='testpass')
		self.client.login(username='other', password='testpass')
		response = self.client.get(reverse('edit_job_seeker_profile'))
		self.assertEqual(response.status_code, 404)
from django.test import TestCase

# Create your tests here.
