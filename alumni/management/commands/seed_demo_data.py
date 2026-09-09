from decimal import Decimal

from django.contrib.auth.models import User, Group
from django.core.management.base import BaseCommand

from alumni.models import AlumniProfile, Announcement, MentorshipRequest
from alumni.management.commands.setup_roles import Command as SetupRolesCommand
from alumni.utils import assign_user_to_role


DEMO_ALUMNI = [
    # linked to login users
    {
        'email': 'alumni1@example.com',
        'username': 'alumni1',
        'password': 'alumni123',
        'first_name': 'John',
        'last_name': 'Doe',
        'graduation_year': 2021,
        'course_studied': 'Fashion & Design',
        'employment_status': 'employed',
        'company_name': 'Creative Designs Ltd',
        'company_location': 'Accra',
        'mentorship_interest': True,
        'networking_interest': True,
        'monthly_savings': '500',
        'monthly_investment': '200',
        'skills_acquired': 'Fashion design, pattern making, digital design',
    },
    {
        'email': 'alumni2@example.com',
        'username': 'alumni2',
        'password': 'alumni123',
        'first_name': 'Jane',
        'last_name': 'Smith',
        'graduation_year': 2022,
        'course_studied': 'Bead Jewelry',
        'employment_status': 'self_employed',
        'company_name': "Jane's Jewelry",
        'company_location': 'Kumasi',
        'mentorship_interest': False,
        'networking_interest': True,
        'monthly_savings': '300',
        'monthly_investment': '150',
        'skills_acquired': 'Jewelry making, beadwork, online marketing',
    },
    # invite-ready / chart fodder (no user unless noted)
    {
        'email': 'kwame.mensah@example.com',
        'first_name': 'Kwame',
        'last_name': 'Mensah',
        'graduation_year': 2020,
        'course_studied': 'Fashion & Design',
        'employment_status': 'employed',
        'company_name': 'Accra Tailors Co',
        'mentorship_interest': True,
        'networking_interest': True,
        'monthly_savings': '400',
        'monthly_investment': '100',
    },
    {
        'email': 'ama.owusu@example.com',
        'first_name': 'Ama',
        'last_name': 'Owusu',
        'graduation_year': 2021,
        'course_studied': 'Bead Jewelry',
        'employment_status': 'seeking',
        'mentorship_interest': False,
        'networking_interest': True,
        'monthly_savings': '50',
        'monthly_investment': '0',
    },
    {
        'email': 'kofi.asante@example.com',
        'first_name': 'Kofi',
        'last_name': 'Asante',
        'graduation_year': 2019,
        'course_studied': 'Catering',
        'employment_status': 'self_employed',
        'company_name': 'Asante Kitchen',
        'mentorship_interest': True,
        'networking_interest': False,
        'monthly_savings': '600',
        'monthly_investment': '250',
    },
    {
        'email': 'efua.boateng@example.com',
        'first_name': 'Efua',
        'last_name': 'Boateng',
        'graduation_year': 2023,
        'course_studied': 'Catering',
        'employment_status': 'employed',
        'company_name': 'City Bites',
        'mentorship_interest': False,
        'networking_interest': True,
        'monthly_savings': '200',
        'monthly_investment': '50',
    },
    {
        'email': 'yaw.addo@example.com',
        'first_name': 'Yaw',
        'last_name': 'Addo',
        'graduation_year': 2022,
        'course_studied': 'ICT Support',
        'employment_status': 'employed',
        'company_name': 'TechBridge',
        'mentorship_interest': True,
        'networking_interest': True,
        'monthly_savings': '450',
        'monthly_investment': '180',
    },
    {
        'email': 'akosua.darko@example.com',
        'first_name': 'Akosua',
        'last_name': 'Darko',
        'graduation_year': 2024,
        'course_studied': 'ICT Support',
        'employment_status': 'seeking',
        'mentorship_interest': False,
        'networking_interest': True,
        'monthly_savings': '20',
        'monthly_investment': '0',
    },
    {
        'email': 'isaac.tetteh@example.com',
        'first_name': 'Isaac',
        'last_name': 'Tetteh',
        'graduation_year': 2020,
        'course_studied': 'Fashion & Design',
        'employment_status': 'self_employed',
        'company_name': 'Tetteh Studio',
        'mentorship_interest': True,
        'networking_interest': True,
        'monthly_savings': '350',
        'monthly_investment': '120',
    },
    {
        'email': 'serwaa.ansah@example.com',
        'first_name': 'Serwaa',
        'last_name': 'Ansah',
        'graduation_year': 2023,
        'course_studied': 'Bead Jewelry',
        'employment_status': 'employed',
        'company_name': 'Glow Beads',
        'mentorship_interest': False,
        'networking_interest': False,
        'monthly_savings': '280',
        'monthly_investment': '90',
    },
    {
        'email': 'daniel.oware@example.com',
        'first_name': 'Daniel',
        'last_name': 'Oware',
        'graduation_year': 2021,
        'course_studied': 'Catering',
        'employment_status': 'seeking',
        'mentorship_interest': False,
        'networking_interest': True,
        'monthly_savings': '40',
        'monthly_investment': '0',
    },
    {
        'email': 'maame.frempong@example.com',
        'first_name': 'Maame',
        'last_name': 'Frempong',
        'graduation_year': 2019,
        'course_studied': 'ICT Support',
        'employment_status': 'employed',
        'company_name': 'DataNest',
        'mentorship_interest': True,
        'networking_interest': True,
        'monthly_savings': '700',
        'monthly_investment': '300',
    },
    {
        'email': 'nana.agyeman@example.com',
        'first_name': 'Nana',
        'last_name': 'Agyeman',
        'graduation_year': 2024,
        'course_studied': 'Fashion & Design',
        'employment_status': 'seeking',
        'mentorship_interest': False,
        'networking_interest': True,
        'monthly_savings': '15',
        'monthly_investment': '0',
    },
    {
        'email': 'abena.sarpong@example.com',
        'first_name': 'Abena',
        'last_name': 'Sarpong',
        'graduation_year': 2022,
        'course_studied': 'Catering',
        'employment_status': 'self_employed',
        'company_name': 'Sarpong Sweets',
        'mentorship_interest': True,
        'networking_interest': True,
        'monthly_savings': '320',
        'monthly_investment': '110',
    },
    {
        'email': 'fiifi.quaye@example.com',
        'first_name': 'Fiifi',
        'last_name': 'Quaye',
        'graduation_year': 2023,
        'course_studied': 'ICT Support',
        'employment_status': 'employed',
        'company_name': 'CloudWorks GH',
        'mentorship_interest': False,
        'networking_interest': True,
        'monthly_savings': '380',
        'monthly_investment': '140',
    },
    {
        'email': 'adwoa.mensimah@example.com',
        'first_name': 'Adwoa',
        'last_name': 'Mensimah',
        'graduation_year': 2020,
        'course_studied': 'Bead Jewelry',
        'employment_status': 'employed',
        'company_name': 'Heritage Beads',
        'mentorship_interest': True,
        'networking_interest': False,
        'monthly_savings': '410',
        'monthly_investment': '160',
    },
]

ANNOUNCEMENTS = [
    {
        'title': 'Welcome to the alumni portal',
        'body': 'Thanks for joining. Keep your profile updated so we can share opportunities that match your skills.',
        'category': 'general',
        'is_published': True,
    },
    {
        'title': 'Mentorship signup open',
        'body': 'If you are willing to mentor recent graduates, turn on mentorship interest on your profile. Seeking alumni can request a match from Mentorship.',
        'category': 'opportunity',
        'is_published': True,
    },
    {
        'title': 'Profile update deadline',
        'body': 'Please confirm your employment status and contact details by the end of the month for our annual outcomes report.',
        'category': 'deadline',
        'is_published': True,
    },
    {
        'title': 'Draft: spring networking night',
        'body': 'Internal draft — do not publish until venue is confirmed.',
        'category': 'opportunity',
        'is_published': False,
    },
]


class Command(BaseCommand):
    help = 'Seed demo users, alumni profiles, announcements, and mentorship requests'

    def handle(self, *args, **options):
        SetupRolesCommand().handle()

        org_admin, created = User.objects.get_or_create(
            username='orgadmin',
            defaults={
                'email': 'orgadmin@example.com',
                'first_name': 'Organization',
                'last_name': 'Admin',
                'is_active': True,
            },
        )
        if created:
            org_admin.set_password('admin123')
            org_admin.save()
            self.stdout.write(self.style.SUCCESS('Created orgadmin / admin123'))
        assign_user_to_role(org_admin, 'organization_admin')

        profiles_by_email = {}
        for row in DEMO_ALUMNI:
            user = None
            username = row.get('username')
            if username:
                user, u_created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': row['email'],
                        'first_name': row['first_name'],
                        'last_name': row['last_name'],
                        'is_active': True,
                    },
                )
                if u_created:
                    user.set_password(row.get('password', 'alumni123'))
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f'Created user {username}'))
                assign_user_to_role(user, 'alumni')

            defaults = {
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'graduation_year': row.get('graduation_year'),
                'course_studied': row.get('course_studied'),
                'employment_status': row.get('employment_status'),
                'company_name': row.get('company_name'),
                'company_location': row.get('company_location'),
                'mentorship_interest': row.get('mentorship_interest', False),
                'networking_interest': row.get('networking_interest', False),
                'monthly_savings': Decimal(row.get('monthly_savings', '0')),
                'monthly_investment': Decimal(row.get('monthly_investment', '0')),
                'skills_acquired': row.get('skills_acquired', ''),
            }
            if user:
                defaults['user'] = user

            profile, p_created = AlumniProfile.objects.update_or_create(
                email=row['email'],
                defaults=defaults,
            )
            profiles_by_email[row['email']] = profile
            if p_created:
                self.stdout.write(f'  + profile {profile}')

        for item in ANNOUNCEMENTS:
            Announcement.objects.get_or_create(
                title=item['title'],
                defaults={
                    'body': item['body'],
                    'category': item['category'],
                    'is_published': item['is_published'],
                    'created_by': org_admin,
                },
            )

        # Mentorship: seeking mentees request mentors
        mentor = profiles_by_email.get('alumni1@example.com')
        mentor2 = profiles_by_email.get('kwame.mensah@example.com')
        mentee = profiles_by_email.get('ama.owusu@example.com')
        mentee2 = profiles_by_email.get('akosua.darko@example.com')
        mentee3 = profiles_by_email.get('alumni2@example.com')

        if mentor and mentee:
            MentorshipRequest.objects.get_or_create(
                mentee=mentee,
                mentor=mentor,
                defaults={'message': 'Would love advice on finding my first design role.', 'status': 'pending'},
            )
        if mentor2 and mentee2:
            MentorshipRequest.objects.get_or_create(
                mentee=mentee2,
                mentor=mentor2,
                defaults={'message': 'Looking for ICT career guidance.', 'status': 'accepted'},
            )
        if mentor and mentee3:
            MentorshipRequest.objects.get_or_create(
                mentee=mentee3,
                mentor=mentor,
                defaults={'message': 'Interested in collaborating on jewelry branding.', 'status': 'pending'},
            )

        self.stdout.write(self.style.SUCCESS(
            f'Demo data ready. Profiles: {AlumniProfile.objects.count()}, '
            f'Announcements: {Announcement.objects.count()}, '
            f'Mentorship: {MentorshipRequest.objects.count()}'
        ))
        self.stdout.write('Logins: orgadmin/admin123 · alumni1/alumni123 · alumni2/alumni123')
