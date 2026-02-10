import graphene
from apps.events.models import Testimonial
from ..types.testimonial import TestimonialType


class TestimonialQueries(graphene.ObjectType):
    """
    Public query: returns active testimonials ordered by display order.
    """
    testimonials = graphene.List(TestimonialType)

    def resolve_testimonials(self, info):
        return Testimonial.objects.filter(is_active=True)
