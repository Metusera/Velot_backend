import graphene
from apps.events.models import Testimonial
from ..types.testimonial import TestimonialType


class CreateTestimonial(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        role = graphene.String(required=True)
        text = graphene.String(required=True)
        rating = graphene.Int()
        is_active = graphene.Boolean()
        order = graphene.Int()

    testimonial = graphene.Field(TestimonialType)

    @staticmethod
    def mutate(root, info, name, role, text, rating=5, is_active=True, order=0):
        testimonial = Testimonial.objects.create(
            name=name,
            role=role,
            text=text,
            rating=rating,
            is_active=is_active,
            order=order
        )
        return CreateTestimonial(testimonial=testimonial)


class UpdateTestimonial(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        role = graphene.String()
        text = graphene.String()
        rating = graphene.Int()
        is_active = graphene.Boolean()
        order = graphene.Int()

    testimonial = graphene.Field(TestimonialType)

    @staticmethod
    def mutate(root, info, id, **kwargs):
        testimonial = Testimonial.objects.get(pk=id)
        for key, value in kwargs.items():
            if value is not None:
                setattr(testimonial, key.replace('_', ''), value)
        testimonial.save()
        return UpdateTestimonial(testimonial=testimonial)


class DeleteTestimonial(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    @staticmethod
    def mutate(root, info, id):
        testimonial = Testimonial.objects.get(pk=id)
        testimonial.delete()
        return DeleteTestimonial(success=True)


class TestimonialMutations(graphene.ObjectType):
    create_testimonial = CreateTestimonial.Field()
    update_testimonial = UpdateTestimonial.Field()
    delete_testimonial = DeleteTestimonial.Field()