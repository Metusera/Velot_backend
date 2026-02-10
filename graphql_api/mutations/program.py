import graphene
from graphql import GraphQLError
from django.utils import timezone
from apps.programs.models import Program, Category
from ..types.program import ProgramType, CategoryType
from ..decorators import editor_required, admin_required


class CreateProgramMutation(graphene.Mutation):
    """
    Create a new program. Editor, Admin, and Super Admin only.
    """
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String(required=True)
        category_id = graphene.ID(required=True)
        duration = graphene.String(required=True)
        price = graphene.Decimal(required=True)
        level = graphene.String(required=True)
        slug = graphene.String()

    program = graphene.Field(ProgramType)
    success = graphene.Boolean()
    message = graphene.String()

    @editor_required
    def mutate(self, info, title, description, category_id, duration, price, level, slug=None):
        user = info.context.user

        # Validate level
        valid_levels = [choice[0] for choice in Program.LEVEL_CHOICES]
        if level not in valid_levels:
            return CreateProgramMutation(
                success=False,
                message=f'Invalid level. Must be one of: {", ".join(valid_levels)}'
            )

        # Validate category exists
        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            return CreateProgramMutation(
                success=False,
                message='Category not found'
            )

        # Validate price
        if price < 0:
            return CreateProgramMutation(
                success=False,
                message='Price must be a positive number'
            )

        try:
            # Create program
            program = Program.objects.create(
                title=title,
                slug=slug if slug else None,  # Will auto-generate if None
                description=description,
                category=category,
                duration=duration,
                price=price,
                level=level,
                created_by=user
            )

            return CreateProgramMutation(
                program=program,
                success=True,
                message='Program created successfully'
            )
        except Exception as e:
            return CreateProgramMutation(
                success=False,
                message=str(e)
            )


class UpdateProgramMutation(graphene.Mutation):
    """
    Update an existing program. Editor, Admin, and Super Admin only.
    """
    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String()
        description = graphene.String()
        category_id = graphene.ID()
        duration = graphene.String()
        price = graphene.Decimal()
        level = graphene.String()
        slug = graphene.String()

    program = graphene.Field(ProgramType)
    success = graphene.Boolean()
    message = graphene.String()

    @editor_required
    def mutate(self, info, id, **kwargs):
        try:
            program = Program.objects.get(pk=id)

            # Validate level if provided
            if 'level' in kwargs and kwargs['level'] is not None:
                valid_levels = [choice[0] for choice in Program.LEVEL_CHOICES]
                if kwargs['level'] not in valid_levels:
                    return UpdateProgramMutation(
                        success=False,
                        message=f'Invalid level. Must be one of: {", ".join(valid_levels)}'
                    )

            # Validate category if provided
            if 'category_id' in kwargs and kwargs['category_id'] is not None:
                try:
                    category = Category.objects.get(pk=kwargs['category_id'])
                    program.category = category
                except Category.DoesNotExist:
                    return UpdateProgramMutation(
                        success=False,
                        message='Category not found'
                    )

            # Validate price if provided
            if 'price' in kwargs and kwargs['price'] is not None:
                if kwargs['price'] < 0:
                    return UpdateProgramMutation(
                        success=False,
                        message='Price must be a positive number'
                    )

            # Update other fields
            for field in ['title', 'description', 'duration', 'price', 'level', 'slug']:
                if field in kwargs and kwargs[field] is not None:
                    setattr(program, field, kwargs[field])

            program.save()

            return UpdateProgramMutation(
                program=program,
                success=True,
                message='Program updated successfully'
            )
        except Program.DoesNotExist:
            return UpdateProgramMutation(
                success=False,
                message='Program not found'
            )
        except Exception as e:
            return UpdateProgramMutation(
                success=False,
                message=str(e)
            )


class PublishProgramMutation(graphene.Mutation):
    """
    Publish a program. Editor, Admin, and Super Admin only.
    """
    class Arguments:
        id = graphene.ID(required=True)

    program = graphene.Field(ProgramType)
    success = graphene.Boolean()
    message = graphene.String()

    @editor_required
    def mutate(self, info, id):
        try:
            program = Program.objects.get(pk=id)
            program.status = Program.STATUS_PUBLISHED

            if not program.published_at:
                program.published_at = timezone.now()

            program.save()

            return PublishProgramMutation(
                program=program,
                success=True,
                message='Program published successfully'
            )
        except Program.DoesNotExist:
            return PublishProgramMutation(
                success=False,
                message='Program not found'
            )


class UnpublishProgramMutation(graphene.Mutation):
    """
    Unpublish a program (set to draft). Editor, Admin, and Super Admin only.
    """
    class Arguments:
        id = graphene.ID(required=True)

    program = graphene.Field(ProgramType)
    success = graphene.Boolean()
    message = graphene.String()

    @editor_required
    def mutate(self, info, id):
        try:
            program = Program.objects.get(pk=id)
            program.status = Program.STATUS_DRAFT
            program.save()

            return UnpublishProgramMutation(
                program=program,
                success=True,
                message='Program unpublished successfully'
            )
        except Program.DoesNotExist:
            return UnpublishProgramMutation(
                success=False,
                message='Program not found'
            )


class DeleteProgramMutation(graphene.Mutation):
    """
    Delete a program. Admin and Super Admin only.
    """
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    @admin_required
    def mutate(self, info, id):
        try:
            program = Program.objects.get(pk=id)
            program.delete()

            return DeleteProgramMutation(
                success=True,
                message='Program deleted successfully'
            )
        except Program.DoesNotExist:
            return DeleteProgramMutation(
                success=False,
                message='Program not found'
            )


class CreateCategoryMutation(graphene.Mutation):
    """
    Create a new category. Admin and Super Admin only.
    """
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String()
        slug = graphene.String()

    category = graphene.Field(CategoryType)
    success = graphene.Boolean()
    message = graphene.String()

    @admin_required
    def mutate(self, info, name, description='', slug=None):
        try:
            category = Category.objects.create(
                name=name,
                description=description,
                slug=slug if slug else None  # Will auto-generate if None
            )

            return CreateCategoryMutation(
                category=category,
                success=True,
                message='Category created successfully'
            )
        except Exception as e:
            return CreateCategoryMutation(
                success=False,
                message=str(e)
            )


class ProgramMutations(graphene.ObjectType):
    """
    Program management mutations.
    """
    create_program = CreateProgramMutation.Field()
    update_program = UpdateProgramMutation.Field()
    publish_program = PublishProgramMutation.Field()
    unpublish_program = UnpublishProgramMutation.Field()
    delete_program = DeleteProgramMutation.Field()
    create_category = CreateCategoryMutation.Field()
