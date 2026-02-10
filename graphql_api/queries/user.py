import graphene
from graphql import GraphQLError
from apps.users.models import User
from ..types.user import UserType
from ..decorators import login_required, super_admin_required


class UserQueries(graphene.ObjectType):
    """
    GraphQL queries for User model.
    """

    # Current logged-in user
    me = graphene.Field(UserType)

    # All users (Super Admin only)
    all_users = graphene.List(UserType)

    # Single user by ID (Super Admin only)
    user_by_id = graphene.Field(
        UserType,
        id=graphene.ID(required=True)
    )

    @login_required
    def resolve_me(self, info):
        """
        Get current authenticated user.
        """
        return info.context.user

    @super_admin_required
    def resolve_all_users(self, info):
        """
        Get all users. Super Admin only.
        """
        return User.objects.all()

    @super_admin_required
    def resolve_user_by_id(self, info, id):
        """
        Get user by ID. Super Admin only.
        """
        try:
            return User.objects.get(pk=id)
        except User.DoesNotExist:
            raise GraphQLError('User not found')
