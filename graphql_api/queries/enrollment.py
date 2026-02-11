"""
GraphQL queries for enrollment and learning management.
"""

import graphene
from graphql import GraphQLError
from apps.programs.models import Enrollment, LessonProgress, ProgramModule, Lesson, Program, ProgramInstructor
from graphql_api.types.enrollment import (
    EnrollmentType,
    LessonProgressType,
    ProgramModuleType,
    LessonType,
    ProgramInstructorType
)
from graphql_api.decorators import login_required


class EnrollmentQueries(graphene.ObjectType):
    """Queries for enrollment and learning management"""

    # Get current user's enrollments
    my_enrollments = graphene.List(
        EnrollmentType,
        status=graphene.String()
    )

    # Get specific enrollment details with progress
    enrollment_details = graphene.Field(
        EnrollmentType,
        enrollment_id=graphene.ID(required=True)
    )

    # Get program curriculum (modules and lessons)
    program_curriculum = graphene.List(
        ProgramModuleType,
        program_id=graphene.ID(required=True)
    )

    # Get lesson details
    lesson_details = graphene.Field(
        LessonType,
        lesson_id=graphene.ID(required=True)
    )

    # Get my lesson progress for a specific enrollment
    my_lesson_progress = graphene.List(
        LessonProgressType,
        enrollment_id=graphene.ID(required=True)
    )

    # Get programs assigned to instructor (for instructor role)
    my_assigned_programs = graphene.List(ProgramInstructorType)

    # Check if user is enrolled in a program
    is_enrolled = graphene.Field(
        EnrollmentType,
        program_id=graphene.ID(required=True)
    )

    @login_required
    def resolve_my_enrollments(self, info, status=None):
        """
        Get current user's enrollments.

        Args:
            status: Optional filter by status (active, completed, dropped, etc.)
        """
        user = info.context.user
        queryset = Enrollment.objects.filter(student=user)

        if status:
            queryset = queryset.filter(status=status)

        return queryset.select_related('program', 'program__category')

    @login_required
    def resolve_enrollment_details(self, info, enrollment_id):
        """
        Get detailed enrollment information with progress.

        Args:
            enrollment_id: ID of the enrollment
        """
        user = info.context.user

        try:
            enrollment = Enrollment.objects.select_related(
                'program',
                'program__category'
            ).prefetch_related(
                'lesson_progress__lesson__module'
            ).get(pk=enrollment_id, student=user)

            return enrollment
        except Enrollment.DoesNotExist:
            raise GraphQLError('Enrollment not found or you do not have permission')

    @login_required
    def resolve_program_curriculum(self, info, program_id):
        """
        Get program curriculum (modules and lessons).
        If user is enrolled, includes progress data.

        Args:
            program_id: ID of the program
        """
        user = info.context.user

        try:
            program = Program.objects.get(pk=program_id)
        except Program.DoesNotExist:
            raise GraphQLError('Program not found')

        # Check if user is enrolled
        enrollment = Enrollment.objects.filter(
            student=user,
            program=program
        ).first()

        # For non-enrolled users, only show preview lessons
        modules = ProgramModule.objects.filter(program=program).prefetch_related('lessons')

        if not enrollment:
            # Filter to only show preview lessons if not enrolled
            for module in modules:
                module.lessons_filtered = module.lessons.filter(is_preview=True)
        else:
            # Show all lessons if enrolled
            for module in modules:
                module.lessons_filtered = module.lessons.all()

        return modules

    @login_required
    def resolve_lesson_details(self, info, lesson_id):
        """
        Get lesson details.

        Args:
            lesson_id: ID of the lesson
        """
        user = info.context.user

        try:
            lesson = Lesson.objects.select_related('module', 'module__program').get(pk=lesson_id)
        except Lesson.DoesNotExist:
            raise GraphQLError('Lesson not found')

        # Check if user is enrolled or if lesson is preview
        enrollment = Enrollment.objects.filter(
            student=user,
            program=lesson.module.program
        ).first()

        if not enrollment and not lesson.is_preview:
            raise GraphQLError('You must be enrolled to view this lesson')

        return lesson

    @login_required
    def resolve_my_lesson_progress(self, info, enrollment_id):
        """
        Get lesson progress for a specific enrollment.

        Args:
            enrollment_id: ID of the enrollment
        """
        user = info.context.user

        try:
            enrollment = Enrollment.objects.get(pk=enrollment_id, student=user)
        except Enrollment.DoesNotExist:
            raise GraphQLError('Enrollment not found or you do not have permission')

        return LessonProgress.objects.filter(enrollment=enrollment).select_related('lesson', 'lesson__module')

    @login_required
    def resolve_my_assigned_programs(self, info):
        """
        Get programs assigned to current instructor.
        Only works for users with instructor role.
        """
        user = info.context.user

        if not user.is_instructor:
            raise GraphQLError('This query is only available to instructors')

        return ProgramInstructor.objects.filter(instructor=user).select_related('program', 'assigned_by')

    @login_required
    def resolve_is_enrolled(self, info, program_id):
        """
        Check if current user is enrolled in a program.

        Args:
            program_id: ID of the program

        Returns:
            Enrollment object if enrolled, None otherwise
        """
        user = info.context.user

        try:
            return Enrollment.objects.get(student=user, program_id=program_id)
        except Enrollment.DoesNotExist:
            return None
