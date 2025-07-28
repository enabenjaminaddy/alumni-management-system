from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from alumni.utils import assign_user_to_role


class Command(BaseCommand):
    help = 'Create test users for different roles'

    def handle(self, *args, **options):
        # Create Organization Admin test user
        org_admin_user, created = User.objects.get_or_create(
            username='orgadmin',
            defaults={
                'email': 'orgadmin@example.com',
                'first_name': 'Organization',
                'last_name': 'Admin',
                'is_staff': False,
                'is_active': True,
            }
        )
        
        if created:
            org_admin_user.set_password('admin123')
            org_admin_user.save()
            self.stdout.write(
                self.style.SUCCESS('Created Organization Admin user: orgadmin / admin123')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Organization Admin user already exists')
            )
        
        # Assign to Organization Admin group
        assign_user_to_role(org_admin_user, 'organization_admin')
        
        # Create Alumni test user
        alumni_user, created = User.objects.get_or_create(
            username='alumni1',
            defaults={
                'email': 'alumni1@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'is_staff': False,
                'is_active': True,
            }
        )
        
        if created:
            alumni_user.set_password('alumni123')
            alumni_user.save()
            self.stdout.write(
                self.style.SUCCESS('Created Alumni user: alumni1 / alumni123')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Alumni user already exists')
            )
        
        # Assign to Alumni group
        assign_user_to_role(alumni_user, 'alumni')
        
        # Create another Alumni test user
        alumni_user2, created = User.objects.get_or_create(
            username='alumni2',
            defaults={
                'email': 'alumni2@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'is_staff': False,
                'is_active': True,
            }
        )
        
        if created:
            alumni_user2.set_password('alumni123')
            alumni_user2.save()
            self.stdout.write(
                self.style.SUCCESS('Created Alumni user: alumni2 / alumni123')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Alumni user 2 already exists')
            )
        
        # Assign to Alumni group
        assign_user_to_role(alumni_user2, 'alumni')
        
        self.stdout.write('\n--- Test Users Created ---')
        self.stdout.write('System Admin: stephen (your superuser)')
        self.stdout.write('Organization Admin: orgadmin / admin123')
        self.stdout.write('Alumni 1: alumni1 / alumni123')
        self.stdout.write('Alumni 2: alumni2 / alumni123')
        self.stdout.write('\nYou can now test role-based login with these accounts!') 