"""
Permission decorators for GraphQL resolvers.
These decorators check user authentication and permissions before allowing access.
"""
from functools import wraps
from graphql import GraphQLError


def login_required(func):
    """
    Decorator to require authentication.
    Raises GraphQLError if user is not authenticated.
    """
    @wraps(func)
    def wrapper(root, info, *args, **kwargs):
        if not info.context.user or not info.context.user.is_authenticated:
            raise GraphQLError('Authentication required')
        return func(root, info, *args, **kwargs)
    return wrapper


def permission_required(*roles):
    """
    Decorator to require specific roles.
    Accepts one or more role names.

    Usage:
        @permission_required('super_admin', 'admin')
        def resolve_something(root, info, ...):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(root, info, *args, **kwargs):
            user = info.context.user
            if not user or not user.is_authenticated:
                raise GraphQLError('Authentication required')

            if user.role not in roles:
                raise GraphQLError('Insufficient permissions')

            return func(root, info, *args, **kwargs)
        return wrapper
    return decorator


def super_admin_required(func):
    """
    Decorator for super admin only operations.
    """
    @wraps(func)
    def wrapper(root, info, *args, **kwargs):
        user = info.context.user
        if not user or not user.is_authenticated:
            raise GraphQLError('Authentication required')

        if not user.is_super_admin:
            raise GraphQLError('Super admin access required')

        return func(root, info, *args, **kwargs)
    return wrapper


def admin_required(func):
    """
    Decorator for admin level access (Admin and Super Admin).
    """
    @wraps(func)
    def wrapper(root, info, *args, **kwargs):
        user = info.context.user
        if not user or not user.is_authenticated:
            raise GraphQLError('Authentication required')

        if not user.is_admin:
            raise GraphQLError('Admin access required')

        return func(root, info, *args, **kwargs)
    return wrapper


def editor_required(func):
    """
    Decorator for editor level access (Editor, Admin, and Super Admin).
    """
    @wraps(func)
    def wrapper(root, info, *args, **kwargs):
        user = info.context.user
        if not user or not user.is_authenticated:
            raise GraphQLError('Authentication required')

        if not user.is_editor:
            raise GraphQLError('Editor access required')

        return func(root, info, *args, **kwargs)
    return wrapper
