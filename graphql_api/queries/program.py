import graphene
from graphql import GraphQLError
from apps.programs.models import Program, Category
from ..types.program import ProgramType, CategoryType
from ..decorators import login_required


class ProgramQueries(graphene.ObjectType):
    """
    GraphQL queries for Program model.
    """

    # Public queries
    published_programs = graphene.List(
        ProgramType,
        category=graphene.String(),
        level=graphene.String()
    )
    program_by_slug = graphene.Field(
        ProgramType,
        slug=graphene.String(required=True)
    )

    # Protected queries
    all_programs = graphene.List(ProgramType)
    program_by_id = graphene.Field(
        ProgramType,
        id=graphene.ID(required=True)
    )

    # Category queries (public)
    categories = graphene.List(CategoryType)
    category_by_slug = graphene.Field(
        CategoryType,
        slug=graphene.String(required=True)
    )

    def resolve_published_programs(self, info, category=None, level=None):
        """
        Get all published programs. Public query with optional filters.
        """
        queryset = Program.objects.filter(status='published')

        if category:
            queryset = queryset.filter(category__slug=category)
        if level:
            queryset = queryset.filter(level=level)

        return queryset.select_related('category', 'created_by')

    def resolve_program_by_slug(self, info, slug):
        """
        Get program by slug. Public query but respects status.
        """
        try:
            program = Program.objects.select_related('category', 'created_by').get(slug=slug)

            # Non-authenticated users can only see published programs
            if not info.context.user.is_authenticated:
                if program.status != 'published':
                    raise GraphQLError('Program not found')

            return program
        except Program.DoesNotExist:
            raise GraphQLError('Program not found')

    @login_required
    def resolve_all_programs(self, info):
        """
        Get all programs. Protected query - authenticated users only.
        Viewers and Editors see only published programs.
        Admins and Super Admins see all programs.
        """
        user = info.context.user

        # Viewers and Editors can only see published programs
        if user.role in ['viewer', 'editor']:
            return Program.objects.filter(status='published').select_related('category', 'created_by')

        # Admins and Super Admins can see all
        return Program.objects.all().select_related('category', 'created_by')

    @login_required
    def resolve_program_by_id(self, info, id):
        """
        Get program by ID. Protected query - authenticated users only.
        """
        try:
            program = Program.objects.select_related('category', 'created_by').get(pk=id)

            # Viewers and Editors can only see published programs
            user = info.context.user
            if user.role in ['viewer', 'editor'] and program.status != 'published':
                raise GraphQLError('Program not found')

            return program
        except Program.DoesNotExist:
            raise GraphQLError('Program not found')

    def resolve_categories(self, info):
        """
        Get all categories. Public query.
        """
        return Category.objects.all()

    def resolve_category_by_slug(self, info, slug):
        """
        Get category by slug. Public query.
        """
        try:
            return Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            raise GraphQLError('Category not found')
