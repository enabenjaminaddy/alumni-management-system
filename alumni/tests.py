from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.core import mail
from io import BytesIO

from alumni.models import AlumniProfile, Announcement, MentorshipRequest
from alumni.import_utils import parse_alumni_csv, commit_alumni_rows
from alumni.management.commands.setup_roles import Command as SetupRolesCommand


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    SENDGRID_API_KEY='test',
)
class BaseAlumniTestCase(TestCase):
    def setUp(self):
        SetupRolesCommand().handle()
        self.client = Client()

        self.org_admin = User.objects.create_user(
            username='admin@example.com',
            email='admin@example.com',
            password='pass12345',
        )
        self.org_admin.groups.add(Group.objects.get(name='Organization Admin'))

        self.alumni_user = User.objects.create_user(
            username='alumni@example.com',
            email='alumni@example.com',
            password='pass12345',
            first_name='Ada',
            last_name='Alumni',
        )
        self.alumni_user.groups.add(Group.objects.get(name='Alumni'))
        self.alumni_profile = AlumniProfile.objects.create(
            user=self.alumni_user,
            first_name='Ada',
            last_name='Alumni',
            email='alumni@example.com',
            employment_status='employed',
            course_studied='Nursing',
            graduation_year=2022,
            mentorship_interest=True,
        )

        self.other_profile = AlumniProfile.objects.create(
            first_name='Bob',
            last_name='Seeker',
            email='bob@example.com',
            employment_status='seeking',
            course_studied='IT',
            graduation_year=2023,
        )


class RBACTests(BaseAlumniTestCase):
    def test_send_invite_requires_org_admin(self):
        url = reverse('send_invite', args=[self.other_profile.id])

        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login', resp.url)

        self.client.login(username='alumni@example.com', password='pass12345')
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)

        self.client.login(username='admin@example.com', password='pass12345')
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse('alumni_list'))
        self.assertTrue(User.objects.filter(email='bob@example.com').exists())
        self.assertEqual(len(mail.outbox), 1)

    def test_alumni_cannot_access_org_dashboard(self):
        self.client.login(username='alumni@example.com', password='pass12345')
        resp = self.client.get(reverse('org_admin_dashboard'))
        self.assertEqual(resp.status_code, 302)

    def test_org_admin_dashboard_ok(self):
        self.client.login(username='admin@example.com', password='pass12345')
        resp = self.client.get(reverse('org_admin_dashboard'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Employment rate')


class CSVImportTests(BaseAlumniTestCase):
    def test_parse_valid_and_invalid_rows(self):
        content = (
            'email,first_name,last_name,graduation_year,employment_status\n'
            'new@example.com,New,Person,2024,employed\n'
            'bad-email,X,Y,2024,employed\n'
            'alumni@example.com,Ada,Updated,2022,employed\n'
        )
        rows, errors = parse_alumni_csv(BytesIO(content.encode()))
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['row'], 3)
        self.assertEqual(len(rows), 2)
        actions = {r['email']: r['import_action'] for r in rows}
        self.assertEqual(actions['new@example.com'], 'create')
        self.assertEqual(actions['alumni@example.com'], 'update')

    def test_commit_creates_and_updates(self):
        rows = [
            {
                'email': 'new@example.com',
                'first_name': 'New',
                'last_name': 'Person',
                'phone_number': None,
                'current_address': None,
                'graduation_year': 2024,
                'course_studied': 'Nursing',
                'employment_status': 'employed',
                'company_name': None,
                'company_location': None,
                'skills_acquired': None,
                'work_experience': None,
                'monthly_savings': '10.00',
                'monthly_investment': '5.00',
                'mentorship_interest': False,
                'networking_interest': True,
            }
        ]
        created, updated = commit_alumni_rows(rows)
        self.assertEqual(created, 1)
        self.assertEqual(updated, 0)
        self.assertTrue(AlumniProfile.objects.filter(email='new@example.com').exists())

    def test_import_view_requires_admin(self):
        self.client.login(username='alumni@example.com', password='pass12345')
        resp = self.client.get(reverse('import_alumni_csv'))
        self.assertEqual(resp.status_code, 302)


class ExportTests(BaseAlumniTestCase):
    def test_bulk_export(self):
        self.client.login(username='admin@example.com', password='pass12345')
        resp = self.client.post(reverse('bulk_operations'), {
            'action': 'export',
            'selected_alumni': [self.alumni_profile.id, self.other_profile.id],
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'text/csv')
        body = resp.content.decode()
        self.assertIn('alumni@example.com', body)
        self.assertIn('bob@example.com', body)


class AnnouncementTests(BaseAlumniTestCase):
    def test_unpublished_hidden_from_alumni(self):
        Announcement.objects.create(
            title='Public', body='Hello', is_published=True, created_by=self.org_admin
        )
        draft = Announcement.objects.create(
            title='Draft', body='Secret', is_published=False, created_by=self.org_admin
        )
        self.client.login(username='alumni@example.com', password='pass12345')
        resp = self.client.get(reverse('announcements_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Public')
        self.assertNotContains(resp, 'Draft')

        resp = self.client.get(reverse('announcement_detail', args=[draft.pk]))
        self.assertEqual(resp.status_code, 302)

        self.client.login(username='admin@example.com', password='pass12345')
        resp = self.client.get(reverse('announcements_list'))
        self.assertContains(resp, 'Draft')


class MentorshipTests(BaseAlumniTestCase):
    def test_request_and_accept(self):
        mentee_user = User.objects.create_user(
            username='mentee@example.com',
            email='mentee@example.com',
            password='pass12345',
        )
        mentee_user.groups.add(Group.objects.get(name='Alumni'))
        mentee = AlumniProfile.objects.create(
            user=mentee_user,
            first_name='Mina',
            last_name='Mentee',
            email='mentee@example.com',
            employment_status='seeking',
        )

        self.client.login(username='mentee@example.com', password='pass12345')
        resp = self.client.post(reverse('mentorship_hub'), {
            'mentor': self.alumni_profile.id,
            'message': 'Please help',
        })
        self.assertEqual(resp.status_code, 302)
        req = MentorshipRequest.objects.get(mentee=mentee, mentor=self.alumni_profile)
        self.assertEqual(req.status, 'pending')

        self.client.login(username='alumni@example.com', password='pass12345')
        resp = self.client.post(reverse('mentorship_respond', args=[req.pk]), {
            'action': 'accept',
        })
        self.assertEqual(resp.status_code, 302)
        req.refresh_from_db()
        self.assertEqual(req.status, 'accepted')
