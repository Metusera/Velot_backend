import graphene
from graphene_django import DjangoObjectType
from apps.users.models import User


class UserType(DjangoObjectType):
    """
    GraphQL Type for User model.
    """
    class Meta:
        model = User
        fields = (
            'id', 'email', 'full_name', 'role',
            'is_active', 'date_joined', 'updated_at'
        )
        convert_choices_to_enum = False

    role_display = graphene.String()

    def resolve_role_display(self, info):
        """Return human-readable role name"""
        return self.get_role_display()
