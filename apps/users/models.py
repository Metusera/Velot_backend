from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
import secrets
from .managers import CustomUserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model using email as username field.
    Implements role-based access control (RBAC).
    """

    ROLE_SUPER_ADMIN = 'super_admin'
    ROLE_ADMIN = 'admin'
    ROLE_INSTRUCTOR = 'instructor'
    ROLE_EDITOR = 'editor'
    ROLE_LEARNER = 'learner'

    ROLE_CHOICES = [
        (ROLE_SUPER_ADMIN, 'Super Admin'),
        (ROLE_ADMIN, 'Admin'),
        (ROLE_INSTRUCTOR, 'Instructor'),
        (ROLE_EDITOR, 'Editor'),
        (ROLE_LEARNER, 'Learner'),
    ]

    email = models.EmailField(_('email address'), unique=True)
    full_name = models.CharField(_('full name'), max_length=255)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_LEARNER,
        help_text=_('User role determines permissions')
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # Determine if this is a new user or role has changed
        is_new = self.pk is None
        old_role = None

        if not is_new:
            try:
                old_instance = User.objects.get(pk=self.pk)
                old_role = old_instance.role
            except User.DoesNotExist:
                pass

        # Save the user first
        super().save(*args, **kwargs)

        # Assign to appropriate group if new user or role changed
        if is_new or (old_role and old_role != self.role):
            self.assign_group()

    def assign_group(self):
        """
        Assign user to appropriate Django group based on role.
        This integrates with Django's permission system.
        """
        # Remove from all groups first
        self.groups.clear()

        # Create group name from role
        group_name = self.get_role_display()
        group, created = Group.objects.get_or_create(name=group_name)

        # Add user to the group
        self.groups.add(group)

    @property
    def is_super_admin(self):
        """Check if user is a Super Admin"""
        return self.role == self.ROLE_SUPER_ADMIN

    @property
    def is_admin(self):
        """Check if user is Admin or Super Admin"""
        return self.role in [self.ROLE_SUPER_ADMIN, self.ROLE_ADMIN]

    @property
    def is_editor(self):
        """Check if user is Editor, Admin, or Super Admin"""
        return self.role in [self.ROLE_SUPER_ADMIN, self.ROLE_ADMIN, self.ROLE_EDITOR]

    @property
    def is_instructor(self):
        """Check if user is Instructor, Admin, or Super Admin"""
        return self.role in [self.ROLE_SUPER_ADMIN, self.ROLE_ADMIN, self.ROLE_INSTRUCTOR]

    @property
    def can_manage_users(self):
        """Only Super Admin can manage users"""
        return self.is_super_admin

    @property
    def can_delete_content(self):
        """Admin and Super Admin can delete content"""
        return self.role in [self.ROLE_SUPER_ADMIN, self.ROLE_ADMIN]

    @property
    def can_edit_content(self):
        """Editor, Admin, and Super Admin can edit content"""
        return self.is_editor

    @property
    def can_view_content(self):
        """All authenticated users can view content"""
        return True

    @property
    def can_teach_programs(self):
        """Instructor, Admin, and Super Admin can teach programs"""
        return self.is_instructor


class UserInvitation(models.Model):
    """
    Model for user invitations sent by admins.
    Allows inviting users with a specific role before they have an account.
    """

    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_EXPIRED = 'expired'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_EXPIRED, 'Expired'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    email = models.EmailField(_('email address'), unique=True)
    full_name = models.CharField(_('full name'), max_length=255)
    role = models.CharField(
        max_length=20,
        choices=User.ROLE_CHOICES,
        help_text=_('Role that will be assigned when invitation is accepted')
    )
    invited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_invitations',
        help_text=_('Admin who sent the invitation')
    )
    invitation_token = models.CharField(
        max_length=64,
        unique=True,
        help_text=_('Unique token for invitation acceptance')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        help_text=_('Invitation expires after 7 days')
    )
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('user invitation')
        verbose_name_plural = _('user invitations')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.email} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        # Generate token if not exists
        if not self.invitation_token:
            self.invitation_token = secrets.token_urlsafe(48)

        # Set expiry to 7 days from now if not set
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)

        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """Check if invitation has expired"""
        return timezone.now() > self.expires_at or self.status == self.STATUS_EXPIRED

    @property
    def is_valid(self):
        """Check if invitation is valid (pending and not expired)"""
        return self.status == self.STATUS_PENDING and not self.is_expired

    def mark_as_accepted(self):
        """Mark invitation as accepted"""
        self.status = self.STATUS_ACCEPTED
        self.accepted_at = timezone.now()
        self.save(update_fields=['status', 'accepted_at'])

    def mark_as_cancelled(self):
        """Mark invitation as cancelled"""
        self.status = self.STATUS_CANCELLED
        self.save(update_fields=['status'])

    def mark_as_expired(self):
        """Mark invitation as expired"""
        self.status = self.STATUS_EXPIRED
        self.save(update_fields=['status'])
