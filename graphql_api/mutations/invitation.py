"""
GraphQL mutations for user invitations.
"""

import graphene
from graphql import GraphQLError
from apps.users.models import UserInvitation, User
from apps.users.services import InvitationService
from graphql_api.types.invitation import UserInvitationType
from graphql_api.types.user import UserType
from graphql_api.decorators import login_required, super_admin_required


class InviteUserMutation(graphene.Mutation):
    """
    Send a user invitation.
    Only Super Admin can send invitations.
    """

    class Arguments:
        email = graphene.String(required=True)
        full_name = graphene.String(required=True)
        role = graphene.String(required=True)

    invitation = graphene.Field(UserInvitationType)
    success = graphene.Boolean()
    message = graphene.String()

    @super_admin_required
    def mutate(self, info, email, full_name, role):
        try:
            invitation = InvitationService.send_invitation(
                email=email,
                full_name=full_name,
                role=role,
                invited_by=info.context.user
            )

            return InviteUserMutation(
                invitation=invitation,
                success=True,
                message=f'Invitation sent successfully to {email}'
            )
        except ValueError as e:
            return InviteUserMutation(
                success=False,
                message=str(e)
            )
        except Exception as e:
            raise GraphQLError(f'Failed to send invitation: {str(e)}')


class AcceptInvitationMutation(graphene.Mutation):
    """
    Accept a user invitation and create account.
    Public mutation - no authentication required.
    """

    class Arguments:
        token = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(UserType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, token, password):
        try:
            user = InvitationService.accept_invitation(
                token=token,
                password=password
            )

            return AcceptInvitationMutation(
                user=user,
                success=True,
                message='Invitation accepted successfully. You can now log in.'
            )
        except ValueError as e:
            return AcceptInvitationMutation(
                success=False,
                message=str(e)
            )
        except Exception as e:
            raise GraphQLError(f'Failed to accept invitation: {str(e)}')


class ResendInvitationMutation(graphene.Mutation):
    """
    Resend an invitation email.
    Only Super Admin can resend invitations.
    """

    class Arguments:
        invitation_id = graphene.ID(required=True)

    invitation = graphene.Field(UserInvitationType)
    success = graphene.Boolean()
    message = graphene.String()

    @super_admin_required
    def mutate(self, info, invitation_id):
        try:
            invitation = InvitationService.resend_invitation(
                invitation_id=invitation_id,
                resent_by=info.context.user
            )

            return ResendInvitationMutation(
                invitation=invitation,
                success=True,
                message=f'Invitation resent successfully to {invitation.email}'
            )
        except ValueError as e:
            return ResendInvitationMutation(
                success=False,
                message=str(e)
            )
        except Exception as e:
            raise GraphQLError(f'Failed to resend invitation: {str(e)}')


class CancelInvitationMutation(graphene.Mutation):
    """
    Cancel a pending invitation.
    Only Super Admin can cancel invitations.
    """

    class Arguments:
        invitation_id = graphene.ID(required=True)

    invitation = graphene.Field(UserInvitationType)
    success = graphene.Boolean()
    message = graphene.String()

    @super_admin_required
    def mutate(self, info, invitation_id):
        try:
            invitation = InvitationService.cancel_invitation(
                invitation_id=invitation_id,
                cancelled_by=info.context.user
            )

            return CancelInvitationMutation(
                invitation=invitation,
                success=True,
                message=f'Invitation cancelled for {invitation.email}'
            )
        except ValueError as e:
            return CancelInvitationMutation(
                success=False,
                message=str(e)
            )
        except Exception as e:
            raise GraphQLError(f'Failed to cancel invitation: {str(e)}')


class InvitationMutations(graphene.ObjectType):
    """Container for all invitation mutations"""
    invite_user = InviteUserMutation.Field()
    accept_invitation = AcceptInvitationMutation.Field()
    resend_invitation = ResendInvitationMutation.Field()
    cancel_invitation = CancelInvitationMutation.Field()
