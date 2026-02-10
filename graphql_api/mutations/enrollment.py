"""
GraphQL mutations for enrollment and learning management.
"""

import graphene
from graphql import GraphQLError
from apps.programs.models import Enrollment, LessonProgress, Program, Lesson, ProgramInstructor
from apps.users.models import User
from graphql_api.types.enrollment import (
    EnrollmentType,
    LessonProgressType,
    ProgramInstructorType
)
from graphql_api.decorators import login_required, admin_required


class EnrollInProgramMutation(graphene.Mutation):
    """
    Enroll current user in a program.
    Free programs = immediate enrollment, paid programs = pending status.
    """

    class Arguments:
        program_id = graphene.ID(required=True)

    enrollment = graphene.Field(EnrollmentType)
    success = graphene.Boolean()
    message = graphene.String()
    requires_payment = graphene.Boolean()

    @login_required
    def mutate(self, info, program_id):
        user = info.context.user

        try:
            program = Program.objects.get(pk=program_id)
        except Program.DoesNotExist:
            raise GraphQLError('Program not found')

        # Check if program is published
        if not program.is_published:
            raise GraphQLError('This program is not available for enrollment')

        # Check if already enrolled
        if Enrollment.objects.filter(student=user, program=program).exists():
            existing = Enrollment.objects.get(student=user, program=program)
            return EnrollInProgramMutation(
                enrollment=existing,
                success=False,
                message='You are already enrolled in this program',
                requires_payment=False
            )

        # Create enrollment
        enrollment = Enrollment.objects.create(
            student=user,
            program=program,
            status=Enrollment.STATUS_PENDING if program.price > 0 else Enrollment.STATUS_ACTIVE
        )

        requires_payment = program.price > 0

        return EnrollInProgramMutation(
            enrollment=enrollment,
            success=True,
            message='Enrollment successful' if not requires_payment else 'Please complete payment to activate enrollment',
            requires_payment=requires_payment
        )


class CompleteLessonMutation(graphene.Mutation):
    """
    Mark a lesson as completed for the current user.
    Updates lesson progress and recalculates overall progress.
    """

    class Arguments:
        lesson_id = graphene.ID(required=True)
        time_spent_minutes = graphene.Int(required=False)

    lesson_progress = graphene.Field(LessonProgressType)
    enrollment = graphene.Field(EnrollmentType)
    success = graphene.Boolean()
    message = graphene.String()

    @login_required
    def mutate(self, info, lesson_id, time_spent_minutes=0):
        user = info.context.user

        try:
            lesson = Lesson.objects.get(pk=lesson_id)
        except Lesson.DoesNotExist:
            raise GraphQLError('Lesson not found')

        # Get enrollment for this program
        try:
            enrollment = Enrollment.objects.get(
                student=user,
                program=lesson.module.program,
                status=Enrollment.STATUS_ACTIVE
            )
        except Enrollment.DoesNotExist:
            raise GraphQLError('You are not enrolled in this program or your enrollment is not active')

        # Get or create lesson progress
        lesson_progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson,
            defaults={'time_spent_minutes': time_spent_minutes}
        )

        # Update time spent if provided
        if not created and time_spent_minutes > 0:
            lesson_progress.time_spent_minutes += time_spent_minutes
            lesson_progress.save(update_fields=['time_spent_minutes'])

        # Mark as complete
        lesson_progress.mark_complete()

        return CompleteLessonMutation(
            lesson_progress=lesson_progress,
            enrollment=enrollment,
            success=True,
            message='Lesson completed successfully'
        )


class DropProgramMutation(graphene.Mutation):
    """
    Drop from a program (change enrollment status to dropped).
    """

    class Arguments:
        enrollment_id = graphene.ID(required=True)

    enrollment = graphene.Field(EnrollmentType)
    success = graphene.Boolean()
    message = graphene.String()

    @login_required
    def mutate(self, info, enrollment_id):
        user = info.context.user

        try:
            enrollment = Enrollment.objects.get(pk=enrollment_id, student=user)
        except Enrollment.DoesNotExist:
            raise GraphQLError('Enrollment not found or you do not have permission')

        # Can only drop active enrollments
        if enrollment.status != Enrollment.STATUS_ACTIVE:
            return DropProgramMutation(
                enrollment=enrollment,
                success=False,
                message=f'Cannot drop enrollment with status: {enrollment.get_status_display()}'
            )

        enrollment.status = Enrollment.STATUS_DROPPED
        enrollment.save(update_fields=['status'])

        return DropProgramMutation(
            enrollment=enrollment,
            success=True,
            message='Successfully dropped from program'
        )


class AssignInstructorToProgramMutation(graphene.Mutation):
    """
    Assign an instructor to a program.
    Only admins can assign instructors.
    """

    class Arguments:
        program_id = graphene.ID(required=True)
        instructor_id = graphene.ID(required=True)
        is_primary = graphene.Boolean(required=False, default_value=False)

    assignment = graphene.Field(ProgramInstructorType)
    success = graphene.Boolean()
    message = graphene.String()

    @admin_required
    def mutate(self, info, program_id, instructor_id, is_primary=False):
        admin = info.context.user

        try:
            program = Program.objects.get(pk=program_id)
        except Program.DoesNotExist:
            raise GraphQLError('Program not found')

        try:
            instructor = User.objects.get(pk=instructor_id)
        except User.DoesNotExist:
            raise GraphQLError('Instructor not found')

        # Verify instructor role
        if not instructor.is_instructor:
            return AssignInstructorToProgramMutation(
                success=False,
                message='User must have instructor role'
            )

        # Check if already assigned
        if ProgramInstructor.objects.filter(program=program, instructor=instructor).exists():
            return AssignInstructorToProgramMutation(
                success=False,
                message='Instructor is already assigned to this program'
            )

        # If marking as primary, unmark other primary instructors
        if is_primary:
            ProgramInstructor.objects.filter(
                program=program,
                is_primary=True
            ).update(is_primary=False)

        # Create assignment
        assignment = ProgramInstructor.objects.create(
            program=program,
            instructor=instructor,
            assigned_by=admin,
            is_primary=is_primary
        )

        return AssignInstructorToProgramMutation(
            assignment=assignment,
            success=True,
            message=f'{instructor.full_name} assigned to {program.title}'
        )


class RemoveInstructorFromProgramMutation(graphene.Mutation):
    """
    Remove an instructor from a program.
    Only admins can remove instructors.
    """

    class Arguments:
        assignment_id = graphene.ID(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    @admin_required
    def mutate(self, info, assignment_id):
        try:
            assignment = ProgramInstructor.objects.get(pk=assignment_id)
            instructor_name = assignment.instructor.full_name
            program_title = assignment.program.title
            assignment.delete()

            return RemoveInstructorFromProgramMutation(
                success=True,
                message=f'Removed {instructor_name} from {program_title}'
            )
        except ProgramInstructor.DoesNotExist:
            raise GraphQLError('Assignment not found')


class EnrollmentMutations(graphene.ObjectType):
    """Container for all enrollment mutations"""
    enroll_in_program = EnrollInProgramMutation.Field()
    complete_lesson = CompleteLessonMutation.Field()
    drop_program = DropProgramMutation.Field()
    assign_instructor_to_program = AssignInstructorToProgramMutation.Field()
    remove_instructor_from_program = RemoveInstructorFromProgramMutation.Field()
