"""
GraphQL queries for user invitations.
"""

import graphene
from graphql import GraphQLError
from apps.users.models import UserInvitation
from graphql_api.types.invitation import UserInvitationType
from graphql_api.decorators import super_admin_required


class InvitationQueries(graphene.ObjectType):
    """Queries for user invitations"""

    # List all pending invitations (Super Admin only)
    pending_invitations = graphene.List(UserInvitationType)

    # List all invitations with optional status filter (Super Admin only)
    all_invitations = graphene.List(
        UserInvitationType,
        status=graphene.String()
    )

    # Get invitation details by token (public - for acceptance page)
    invitation_by_token = graphene.Field(
        UserInvitationType,
        token=graphene.String(required=True)
    )

    # Get invitation by ID (Super Admin only)
    invitation_by_id = graphene.Field(
        UserInvitationType,
        id=graphene.ID(required=True)
    )

    @super_admin_required
    def resolve_pending_invitations(self, info):
        """Get all pending invitations. Super Admin only."""
        return UserInvitation.objects.filter(status=UserInvitation.STATUS_PENDING)

    @super_admin_required
    def resolve_all_invitations(self, info, status=None):
        """
        Get all invitations with optional status filter. Super Admin only.

        Args:
            status: Filter by status (pending, accepted, expired, cancelled)
        """
        queryset = UserInvitation.objects.all()

        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def resolve_invitation_by_token(self, info, token):
        """
        Get invitation details by token. Public access for invitation acceptance.

        Args:
            token: Invitation token from URL
        """
        try:
            return UserInvitation.objects.get(invitation_token=token)
        except UserInvitation.DoesNotExist:
            raise GraphQLError('Invitation not found')

    @super_admin_required
    def resolve_invitation_by_id(self, info, id):
        """Get invitation by ID. Super Admin only."""
        try:
            return UserInvitation.objects.get(pk=id)
        except UserInvitation.DoesNotExist:
            raise GraphQLError('Invitation not found')
