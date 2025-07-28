from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from alumni.models import AlumniProfile


class Command(BaseCommand):
    help = 'Set up user roles and permissions for the alumni management system'

    def handle(self, *args, **options):
        # Create Groups for different user roles
        
        # 1. Organization Admin Group
        org_admin_group, created = Group.objects.get_or_create(name='Organization Admin')
        if created:
            self.stdout.write(
                self.style.SUCCESS('Created "Organization Admin" group')
            )
        
        # 2. Alumni Group (regular users)
        alumni_group, created = Group.objects.get_or_create(name='Alumni')
        if created:
            self.stdout.write(
                self.style.SUCCESS('Created "Alumni" group')
            )
        
        # Get AlumniProfile content type for permissions
        alumni_content_type = ContentType.objects.get_for_model(AlumniProfile)
        
        # Set up permissions for Organization Admin
        org_admin_permissions = [
            'add_alumniprofile',
            'change_alumniprofile', 
            'delete_alumniprofile',
            'view_alumniprofile',
        ]
        
        for perm_codename in org_admin_permissions:
            try:
                permission = Permission.objects.get(
                    codename=perm_codename,
                    content_type=alumni_content_type
                )
                org_admin_group.permissions.add(permission)
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Permission {perm_codename} not found')
                )
        
        # Set up permissions for Alumni (limited)
        alumni_permissions = [
            'view_alumniprofile',  # Can view their own profile
            'change_alumniprofile',  # Can edit their own profile
        ]
        
        for perm_codename in alumni_permissions:
            try:
                permission = Permission.objects.get(
                    codename=perm_codename,
                    content_type=alumni_content_type
                )
                alumni_group.permissions.add(permission)
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Permission {perm_codename} not found')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up user roles and permissions')
        )
        
        # Display summary
        self.stdout.write('\n--- Role Summary ---')
        self.stdout.write('1. System Admin: Full Django admin access (superuser)')
        self.stdout.write('2. Organization Admin: Can manage all alumni profiles')
        self.stdout.write('3. Alumni: Can view and edit their own profile only') 