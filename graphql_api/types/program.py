import graphene
from graphene_django import DjangoObjectType
from apps.programs.models import Program, Category


class CategoryType(DjangoObjectType):
    """
    GraphQL Type for Category model.
    """
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'created_at', 'updated_at')


class ProgramType(DjangoObjectType):
    """
    GraphQL Type for Program model.
    """
    class Meta:
        model = Program
        fields = (
            'id', 'title', 'slug', 'description', 'category',
            'duration', 'price', 'level', 'thumbnail', 'status',
            'is_new', 'is_hot', 'is_professional', 'auto_calculate_badges',
            'created_by', 'created_at', 'updated_at', 'published_at'
        )
        convert_choices_to_enum = False

    level_display = graphene.String()
    status_display = graphene.String()
    event_count = graphene.Int()
    upcoming_events_count = graphene.Int()
    is_published = graphene.Boolean()
    badges = graphene.List(graphene.String)

    def resolve_level_display(self, info):
        """Return human-readable level name"""
        return self.get_level_display()

    def resolve_status_display(self, info):
        """Return human-readable status name"""
        return self.get_status_display()

    def resolve_event_count(self, info):
        """Return total number of events"""
        return self.event_count

    def resolve_upcoming_events_count(self, info):
        """Return number of upcoming events"""
        return self.upcoming_events_count

    def resolve_is_published(self, info):
        """Return whether program is published"""
        return self.is_published

    def resolve_badges(self, info):
        """Return calculated badges for this program"""
        return self.calculated_badges
