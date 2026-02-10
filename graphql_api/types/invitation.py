"""
GraphQL types for user invitations.
"""

import graphene
from graphene_django import DjangoObjectType
from apps.users.models import UserInvitation, User


class UserInvitationType(DjangoObjectType):
    """GraphQL Type for UserInvitation model"""

    class Meta:
        model = UserInvitation
        fields = (
            'id',
            'email',
            'full_name',
            'role',
            'invited_by',
            'invitation_token',
            'status',
            'created_at',
            'expires_at',
            'accepted_at',
        )

    role_display = graphene.String()
    status_display = graphene.String()
    is_expired = graphene.Boolean()
    is_valid = graphene.Boolean()

    def resolve_role_display(self, info):
        """Return human-readable role name"""
        return self.get_role_display()

    def resolve_status_display(self, info):
        """Return human-readable status"""
        return self.get_status_display()

    def resolve_is_expired(self, info):
        """Check if invitation has expired"""
        return self.is_expired

    def resolve_is_valid(self, info):
        """Check if invitation is valid"""
        return self.is_valid
