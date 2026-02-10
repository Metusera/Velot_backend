import graphene
from graphene_django import DjangoObjectType
from apps.events.models import Testimonial


class TestimonialType(DjangoObjectType):
    """
    GraphQL Type for Testimonial model.
    """
    class Meta:
        model = Testimonial
        fields = ('id', 'name', 'role', 'text', 'rating', 'image', 'is_active', 'order', 'created_at')
