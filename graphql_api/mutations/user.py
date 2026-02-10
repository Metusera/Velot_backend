import graphene
from graphql import GraphQLError
from apps.users.models import User
from ..types.user import UserType
from ..decorators import super_admin_required


class CreateUserMutation(graphene.Mutation):
    """
    Create a new user. Super Admin only.
    """
    class Arguments:
        email = graphene.String(required=True)
        full_name = graphene.String(required=True)
        password = graphene.String(required=True)
        role = graphene.String(required=True)
        is_active = graphene.Boolean()

    user = graphene.Field(UserType)
    success = graphene.Boolean()
    message = graphene.String()

    @super_admin_required
    def mutate(self, info, email, full_name, password, role, is_active=True):
        # Validate role
        valid_roles = [choice[0] for choice in User.ROLE_CHOICES]
        if role not in valid_roles:
            return CreateUserMutation(
                success=False,
                message=f'Invalid role. Must be one of: {", ".join(valid_roles)}'
            )

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return CreateUserMutation(
                success=False,
                message='User with this email already exists'
            )

        try:
            # Create user
            user = User.objects.create_user(
                email=email,
                full_name=full_name,
                password=password,
                role=role,
                is_active=is_active
            )

            return CreateUserMutation(
                user=user,
                success=True,
                message='User created successfully'
            )
        except Exception as e:
            return CreateUserMutation(
                success=False,
                message=str(e)
            )


class UpdateUserMutation(graphene.Mutation):
    """
    Update user details. Super Admin only.
    """
    class Arguments:
        id = graphene.ID(required=True)
        full_name = graphene.String()
        role = graphene.String()
        is_active = graphene.Boolean()

    user = graphene.Field(UserType)
    success = graphene.Boolean()
    message = graphene.String()

    @super_admin_required
    def mutate(self, info, id, full_name=None, role=None, is_active=None):
        try:
            user = User.objects.get(pk=id)

            # Update fields if provided
            if full_name is not None:
                user.full_name = full_name

            if role is not None:
                valid_roles = [choice[0] for choice in User.ROLE_CHOICES]
                if role not in valid_roles:
                    return UpdateUserMutation(
                        success=False,
                        message=f'Invalid role. Must be one of: {", ".join(valid_roles)}'
                    )
                user.role = role

            if is_active is not None:
                user.is_active = is_active

            user.save()

            return UpdateUserMutation(
                user=user,
                success=True,
                message='User updated successfully'
            )
        except User.DoesNotExist:
            return UpdateUserMutation(
                success=False,
                message='User not found'
            )
        except Exception as e:
            return UpdateUserMutation(
                success=False,
                message=str(e)
            )


class DeleteUserMutation(graphene.Mutation):
    """
    Delete a user. Super Admin only.
    """
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    @super_admin_required
    def mutate(self, info, id):
        try:
            user = User.objects.get(pk=id)

            # Prevent deleting yourself
            if user.id == info.context.user.id:
                return DeleteUserMutation(
                    success=False,
                    message='You cannot delete yourself'
                )

            user.delete()

            return DeleteUserMutation(
                success=True,
                message='User deleted successfully'
            )
        except User.DoesNotExist:
            return DeleteUserMutation(
                success=False,
                message='User not found'
            )


class UserMutations(graphene.ObjectType):
    """
    User management mutations.
    """
    create_user = CreateUserMutation.Field()
    update_user = UpdateUserMutation.Field()
    delete_user = DeleteUserMutation.Field()
