"""
GraphQL types for enrollment and learning management.
"""

import graphene
from graphene_django import DjangoObjectType
from apps.programs.models import Enrollment, LessonProgress, ProgramModule, Lesson, ProgramInstructor


class EnrollmentType(DjangoObjectType):
    """GraphQL Type for Enrollment model"""

    class Meta:
        model = Enrollment
        fields = (
            'id',
            'student',
            'program',
            'status',
            'enrolled_at',
            'completed_at',
            'progress_percentage',
            'payment_status',
            'payment_amount',
            'payment_reference',
        )

    status_display = graphene.String()
    payment_status_display = graphene.String()
    is_active = graphene.Boolean()
    completed_lessons_count = graphene.Int()
    total_lessons_count = graphene.Int()

    def resolve_status_display(self, info):
        """Return human-readable status"""
        return self.get_status_display()

    def resolve_payment_status_display(self, info):
        """Return human-readable payment status"""
        return self.get_payment_status_display()

    def resolve_is_active(self, info):
        """Check if enrollment is active"""
        return self.is_active

    def resolve_completed_lessons_count(self, info):
        """Get number of completed lessons"""
        return self.completed_lessons_count

    def resolve_total_lessons_count(self, info):
        """Get total number of lessons"""
        return self.total_lessons_count


class LessonProgressType(DjangoObjectType):
    """GraphQL Type for LessonProgress model"""

    class Meta:
        model = LessonProgress
        fields = (
            'id',
            'enrollment',
            'lesson',
            'is_completed',
            'completed_at',
            'time_spent_minutes',
            'last_accessed',
        )


class ProgramModuleType(DjangoObjectType):
    """GraphQL Type for ProgramModule model"""

    class Meta:
        model = ProgramModule
        fields = (
            'id',
            'program',
            'title',
            'description',
            'order',
            'created_at',
            'updated_at',
        )

    lesson_count = graphene.Int()
    total_duration_minutes = graphene.Int()
    lessons = graphene.List(lambda: LessonType)

    def resolve_lesson_count(self, info):
        """Get number of lessons in module"""
        return self.lesson_count

    def resolve_total_duration_minutes(self, info):
        """Get total duration of all lessons"""
        return self.total_duration_minutes

    def resolve_lessons(self, info):
        """Get lessons in this module"""
        return self.lessons.all()


class LessonType(DjangoObjectType):
    """GraphQL Type for Lesson model"""

    class Meta:
        model = Lesson
        fields = (
            'id',
            'module',
            'title',
            'content',
            'duration_minutes',
            'order',
            'video_url',
            'attachments',
            'is_preview',
            'created_at',
            'updated_at',
        )

    progress = graphene.Field(LessonProgressType, enrollment_id=graphene.ID())

    def resolve_progress(self, info, enrollment_id=None):
        """Get progress for this lesson for a specific enrollment"""
        if not enrollment_id:
            return None

        try:
            return LessonProgress.objects.get(
                enrollment_id=enrollment_id,
                lesson=self
            )
        except LessonProgress.DoesNotExist:
            return None


class ProgramInstructorType(DjangoObjectType):
    """GraphQL Type for ProgramInstructor model"""

    class Meta:
        model = ProgramInstructor
        fields = (
            'id',
            'program',
            'instructor',
            'assigned_by',
            'assigned_at',
            'is_primary',
        )
