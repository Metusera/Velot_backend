import graphene
from django.contrib.auth import authenticate
from graphql import GraphQLError
from graphql_jwt.shortcuts import get_token, create_refresh_token
from apps.users.models import User
from ..types.user import UserType


class LoginMutation(graphene.Mutation):
    """
    Login mutation - authenticates user and returns JWT tokens.
    """
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(UserType)
    token = graphene.String()
    refresh_token = graphene.String()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, email, password):
        # Authenticate user
        user = authenticate(username=email, password=password)

        if user is None:
            return LoginMutation(
                success=False,
                message='Invalid credentials'
            )

        if not user.is_active:
            return LoginMutation(
                success=False,
                message='Account is deactivated'
            )

        # Generate JWT tokens
        token = get_token(user)
        refresh_token = create_refresh_token(user)

        return LoginMutation(
            user=user,
            token=token,
            refresh_token=refresh_token,
            success=True,
            message='Login successful'
        )


class VerifyTokenMutation(graphene.Mutation):
    """
    Verify JWT token and return user data.
    """
    class Arguments:
        token = graphene.String(required=True)

    user = graphene.Field(UserType)
    valid = graphene.Boolean()

    def mutate(self, info, token):
        # Token verification is handled by graphql-jwt middleware
        user = info.context.user

        if user and user.is_authenticated:
            return VerifyTokenMutation(user=user, valid=True)

        return VerifyTokenMutation(valid=False)


class AuthMutations(graphene.ObjectType):
    """
    Authentication mutations.
    """
    login = LoginMutation.Field()
    verify_token = VerifyTokenMutation.Field()
