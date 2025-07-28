from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from alumni.models import AlumniProfile


class Command(BaseCommand):
    help = 'Create AlumniProfile records for test users'

    def handle(self, *args, **options):
        # Create profile for alumni1
        try:
            alumni1_user = User.objects.get(username='alumni1')
            alumni1_profile, created = AlumniProfile.objects.get_or_create(
                user=alumni1_user,
                defaults={
                    'first_name': alumni1_user.first_name,
                    'last_name': alumni1_user.last_name,
                    'email': alumni1_user.email,
                    'graduation_year': 2021,
                    'course_studied': 'Fashion & Design',
                    'current_address': 'Accra, Ghana',
                    'phone_number': '+233 123 456 789',
                    'employment_status': 'employed',
                    'company_name': 'Creative Designs Ltd',
                    'company_location': 'Accra, Ghana',
                    'skills_acquired': 'Fashion design, pattern making, tailoring, digital design',
                    'work_experience': 'Fashion designer at Creative Designs Ltd since graduation. Specialized in contemporary African fashion.',
                    'monthly_savings': 500.00,
                    'monthly_investment': 200.00,
                    'testimonial': 'The training program equipped me with practical skills that helped me secure employment immediately after graduation.',
                    'mentorship_interest': True,
                    'networking_interest': True,
                    'social_media_accounts': 'Instagram: @johndoe_designs\nLinkedIn: john-doe-designer'
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created AlumniProfile for {alumni1_user.username}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'AlumniProfile already exists for {alumni1_user.username}')
                )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('User alumni1 not found')
            )

        # Create profile for alumni2
        try:
            alumni2_user = User.objects.get(username='alumni2')
            alumni2_profile, created = AlumniProfile.objects.get_or_create(
                user=alumni2_user,
                defaults={
                    'first_name': alumni2_user.first_name,
                    'last_name': alumni2_user.last_name,
                    'email': alumni2_user.email,
                    'graduation_year': 2022,
                    'course_studied': 'Bead Jewelry',
                    'current_address': 'Kumasi, Ghana',
                    'phone_number': '+233 987 654 321',
                    'employment_status': 'self_employed',
                    'company_name': 'Jane\'s Jewelry',
                    'company_location': 'Kumasi, Ghana',
                    'skills_acquired': 'Jewelry making, beadwork, business management, online marketing',
                    'work_experience': 'Started own jewelry business after graduation. Specializes in traditional Ghanaian beadwork with modern designs.',
                    'monthly_savings': 300.00,
                    'monthly_investment': 150.00,
                    'testimonial': 'The program gave me the confidence and skills to start my own business. I\'m now financially independent.',
                    'mentorship_interest': False,
                    'networking_interest': True,
                    'social_media_accounts': 'Instagram: @janes_jewelry\nFacebook: Jane\'s Jewelry Store'
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created AlumniProfile for {alumni2_user.username}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'AlumniProfile already exists for {alumni2_user.username}')
                )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('User alumni2 not found')
            )

        self.stdout.write('\n--- Alumni Profiles Created ---')
        self.stdout.write('alumni1 (John Doe): Fashion & Design graduate, employed')
        self.stdout.write('alumni2 (Jane Smith): Bead Jewelry graduate, self-employed')
        self.stdout.write('\nNow when alumni users edit their profiles, they will see pre-populated data!') 