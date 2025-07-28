from django.contrib.auth.models import Group


def get_user_role(user):
    """
    Get the user's role based on their group membership.
    Returns: 'system_admin', 'organization_admin', 'alumni', or 'no_role'
    """
    if user.is_superuser:
        return 'system_admin'
    
    if user.groups.filter(name='Organization Admin').exists():
        return 'organization_admin'
    
    if user.groups.filter(name='Alumni').exists():
        return 'alumni'
    
    return 'no_role'


def is_organization_admin(user):
    """Check if user is an Organization Admin"""
    return user.groups.filter(name='Organization Admin').exists() or user.is_superuser


def is_alumni(user):
    """Check if user is an Alumni (regular user)"""
    return user.groups.filter(name='Alumni').exists()


def assign_user_to_role(user, role):
    """
    Assign a user to a specific role group.
    role: 'organization_admin' or 'alumni'
    """
    # Remove user from all role groups first
    user.groups.clear()
    
    if role == 'organization_admin':
        group = Group.objects.get(name='Organization Admin')
        user.groups.add(group)
    elif role == 'alumni':
        group = Group.objects.get(name='Alumni')
        user.groups.add(group)
    
    return True


def get_dashboard_url_for_role(role):
    """Get the appropriate dashboard URL based on user role"""
    role_urls = {
        'system_admin': '/admin/',
        'organization_admin': '/org-admin/',
        'alumni': '/home/',
        'no_role': '/login/'
    }
    return role_urls.get(role, '/login/') 