"""
Service layer for user-related business logic.
Handles invitation sending, acceptance, and user creation.
"""

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import User, UserInvitation
from .utils import generate_secure_password
import logging

logger = logging.getLogger(__name__)


class InvitationService:
    """
    Service class for handling user invitations.
    """

    @staticmethod
    def send_invitation(email, full_name, role, invited_by):
        """
        Create and send a user invitation.

        Args:
            email (str): Email address of the invitee
            full_name (str): Full name of the invitee
            role (str): Role to assign (must be valid User.ROLE_CHOICES)
            invited_by (User): User sending the invitation

        Returns:
            UserInvitation: Created invitation object

        Raises:
            ValueError: If email already exists or invalid role
        """
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            raise ValueError(f"User with email {email} already exists")

        # Check if valid role
        valid_roles = [choice[0] for choice in User.ROLE_CHOICES]
        if role not in valid_roles:
            raise ValueError(f"Invalid role: {role}. Must be one of {valid_roles}")

        # Cancel any existing pending invitations for this email
        UserInvitation.objects.filter(
            email=email,
            status=UserInvitation.STATUS_PENDING
        ).update(status=UserInvitation.STATUS_CANCELLED)

        # Create invitation
        invitation = UserInvitation.objects.create(
            email=email,
            full_name=full_name,
            role=role,
            invited_by=invited_by
        )

        # Send invitation email
        InvitationService._send_invitation_email(invitation)

        logger.info(f"Invitation sent to {email} by {invited_by.email}")
        return invitation

    @staticmethod
    def _send_invitation_email(invitation):
        """
        Send invitation email to the invitee.

        Args:
            invitation (UserInvitation): Invitation object
        """
        # Build acceptance URL
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        acceptance_url = f"{frontend_url}/accept-invitation/{invitation.invitation_token}"

        # Prepare email context
        context = {
            'full_name': invitation.full_name,
            'role': invitation.get_role_display(),
            'invited_by': invitation.invited_by.full_name,
            'acceptance_url': acceptance_url,
            'expiry_days': 7,
            'institution_name': 'VeloT Africa',
        }

        # Render HTML and plain text email
        html_message = render_to_string('emails/invitation.html', context)
        plain_message = render_to_string('emails/invitation.txt', context)

        # Send email
        try:
            send_mail(
                subject=f"You're invited to join {context['institution_name']}",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[invitation.email],
                html_message=html_message,
                fail_silently=False,
            )
            logger.info(f"Invitation email sent successfully to {invitation.email}")
        except Exception as e:
            logger.error(f"Failed to send invitation email to {invitation.email}: {str(e)}")
            # Don't raise - invitation is still created, can be resent later

    @staticmethod
    def accept_invitation(token, password):
        """
        Accept an invitation and create user account.

        Args:
            token (str): Invitation token
            password (str): Password for new account

        Returns:
            User: Created user object

        Raises:
            ValueError: If invitation invalid, expired, or already used
        """
        try:
            invitation = UserInvitation.objects.get(invitation_token=token)
        except UserInvitation.DoesNotExist:
            raise ValueError("Invalid invitation token")

        # Check if invitation is valid
        if not invitation.is_valid:
            if invitation.is_expired:
                raise ValueError("Invitation has expired")
            else:
                raise ValueError(f"Invitation is {invitation.get_status_display()}")

        # Check if user already exists
        if User.objects.filter(email=invitation.email).exists():
            raise ValueError(f"User with email {invitation.email} already exists")

        # Create user
        user = User.objects.create_user(
            email=invitation.email,
            full_name=invitation.full_name,
            password=password,
            role=invitation.role,
            is_active=True
        )

        # Mark invitation as accepted
        invitation.mark_as_accepted()

        logger.info(f"Invitation accepted and user created: {user.email}")
        return user

    @staticmethod
    def resend_invitation(invitation_id, resent_by):
        """
        Resend an invitation email.

        Args:
            invitation_id (int): ID of invitation to resend
            resent_by (User): User resending the invitation

        Returns:
            UserInvitation: Updated invitation object

        Raises:
            ValueError: If invitation not found or cannot be resent
        """
        try:
            invitation = UserInvitation.objects.get(id=invitation_id)
        except UserInvitation.DoesNotExist:
            raise ValueError("Invitation not found")

        # Only resend pending invitations
        if invitation.status != UserInvitation.STATUS_PENDING:
            raise ValueError(f"Cannot resend invitation with status: {invitation.get_status_display()}")

        # Check if user was created in the meantime
        if User.objects.filter(email=invitation.email).exists():
            invitation.mark_as_accepted()
            raise ValueError(f"User with email {invitation.email} already exists")

        # Resend email
        InvitationService._send_invitation_email(invitation)

        logger.info(f"Invitation resent to {invitation.email} by {resent_by.email}")
        return invitation

    @staticmethod
    def cancel_invitation(invitation_id, cancelled_by):
        """
        Cancel a pending invitation.

        Args:
            invitation_id (int): ID of invitation to cancel
            cancelled_by (User): User cancelling the invitation

        Returns:
            UserInvitation: Updated invitation object

        Raises:
            ValueError: If invitation not found
        """
        try:
            invitation = UserInvitation.objects.get(id=invitation_id)
        except UserInvitation.DoesNotExist:
            raise ValueError("Invitation not found")

        # Only cancel pending invitations
        if invitation.status == UserInvitation.STATUS_PENDING:
            invitation.mark_as_cancelled()
            logger.info(f"Invitation cancelled for {invitation.email} by {cancelled_by.email}")
        else:
            logger.warning(f"Cannot cancel invitation with status: {invitation.get_status_display()}")

        return invitation
