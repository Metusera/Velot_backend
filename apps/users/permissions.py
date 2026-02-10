"""
Permission helper functions for RBAC.
These functions can be used throughout the application to check permissions.
"""


def can_manage_users(user):
    """
    Check if user can manage other users.
    Only Super Admin can manage users.
    """
    return user.is_authenticated and user.is_super_admin


def can_delete_programs(user):
    """
    Check if user can delete programs.
    Only Admin and Super Admin can delete programs.
    """
    return user.is_authenticated and user.role in ['super_admin', 'admin']


def can_create_programs(user):
    """
    Check if user can create programs.
    Editor, Admin, and Super Admin can create programs.
    """
    return user.is_authenticated and user.is_editor


def can_edit_programs(user):
    """
    Check if user can edit programs.
    Editor, Admin, and Super Admin can edit programs.
    """
    return user.is_authenticated and user.is_editor


def can_publish_programs(user):
    """
    Check if user can publish/unpublish programs.
    Editor, Admin, and Super Admin can publish programs.
    """
    return user.is_authenticated and user.is_editor


def can_delete_events(user):
    """
    Check if user can delete events.
    Only Admin and Super Admin can delete events.
    """
    return user.is_authenticated and user.role in ['super_admin', 'admin']


def can_create_events(user):
    """
    Check if user can create events.
    Editor, Admin, and Super Admin can create events.
    """
    return user.is_authenticated and user.is_editor


def can_edit_events(user):
    """
    Check if user can edit events.
    Editor, Admin, and Super Admin can edit events.
    """
    return user.is_authenticated and user.is_editor
