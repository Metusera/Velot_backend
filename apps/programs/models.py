from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.utils import timezone


class Category(models.Model):
    """
    Program categories for organizing programs.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True, max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Program(models.Model):
    """
    Main program model for courses, trainings, workshops, etc.
    """

    LEVEL_BEGINNER = 'beginner'
    LEVEL_INTERMEDIATE = 'intermediate'
    LEVEL_ADVANCED = 'advanced'

    LEVEL_CHOICES = [
        (LEVEL_BEGINNER, 'Beginner'),
        (LEVEL_INTERMEDIATE, 'Intermediate'),
        (LEVEL_ADVANCED, 'Advanced'),
    ]

    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_ARCHIVED = 'archived'

    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
        (STATUS_ARCHIVED, 'Archived'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255, blank=True)
    description = models.TextField(help_text='Rich text content (HTML)')
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='programs',
        help_text='Program category'
    )
    duration = models.CharField(
        max_length=100,
        help_text='e.g., "8 weeks", "3 months", "6 sessions"'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Price in USD'
    )
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default=LEVEL_BEGINNER
    )
    thumbnail = models.ImageField(
        upload_to='thumbnails/programs/',
        blank=True,
        null=True,
        help_text='Program thumbnail image'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_programs',
        help_text='User who created this program'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    # Badge system fields
    is_new = models.BooleanField(
        default=False,
        help_text='Manually mark as NEW'
    )
    is_hot = models.BooleanField(
        default=False,
        help_text='Manually mark as HOT'
    )
    is_professional = models.BooleanField(
        default=False,
        help_text='Manually mark as PROFESSIONAL'
    )
    auto_calculate_badges = models.BooleanField(
        default=True,
        help_text='Auto-calculate badges based on rules'
    )

    class Meta:
        ordering = ['-created_at']
        permissions = [
            ("publish_program", "Can publish program"),
            ("unpublish_program", "Can unpublish program"),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Auto-generate slug from title if not provided
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            # Ensure slug is unique
            while Program.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        # Set published_at timestamp when status changes to published
        if self.status == self.STATUS_PUBLISHED and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    @property
    def is_published(self):
        """Check if program is published"""
        return self.status == self.STATUS_PUBLISHED

    @property
    def event_count(self):
        """Get number of events for this program"""
        try:
            return self.events.count()
        except Exception:
            return 0

    @property
    def upcoming_events_count(self):
        """Get number of upcoming events"""
        try:
            return self.events.filter(status='upcoming').count()
        except Exception:
            return 0

    @property
    def calculated_badges(self):
        """
        Auto-calculate and return badges based on rules.
        Returns list of badge strings: ['new', 'hot', 'professional']
        """
        badges = []

        if self.auto_calculate_badges and self.published_at:
            # NEW: Published within last 30 days
            days_since_publish = (timezone.now() - self.published_at).days
            if days_since_publish <= 30:
                badges.append('new')

            # HOT: High enrollment count (> 50 active enrollments)
            try:
                enrollment_count = self.enrollments.filter(status='active').count()
                if enrollment_count > 50:
                    badges.append('hot')
            except Exception:
                pass

            # PROFESSIONAL: Advanced level AND long duration (contains "12" or "month")
            if self.level == self.LEVEL_ADVANCED:
                duration_lower = self.duration.lower()
                if '12' in duration_lower or 'month' in duration_lower:
                    badges.append('professional')

        # Add manual badges (manual badges override auto-calculated)
        if self.is_new and 'new' not in badges:
            badges.append('new')
        if self.is_hot and 'hot' not in badges:
            badges.append('hot')
        if self.is_professional and 'professional' not in badges:
            badges.append('professional')

        return badges


class ProgramModule(models.Model):
    """
    Groups related lessons together within a program.
    Example: "Week 1: Introduction to Python", "Module 2: Data Structures"
    """
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name='modules',
        help_text='Program this module belongs to'
    )
    title = models.CharField(max_length=255, help_text='Module title')
    description = models.TextField(blank=True, help_text='Module description/overview')
    order = models.IntegerField(default=0, help_text='Display order within program')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'program module'
        verbose_name_plural = 'program modules'

    def __str__(self):
        return f"{self.program.title} - {self.title}"

    @property
    def lesson_count(self):
        """Get number of lessons in this module"""
        return self.lessons.count()

    @property
    def total_duration_minutes(self):
        """Calculate total duration of all lessons in module"""
        return sum(lesson.duration_minutes for lesson in self.lessons.all())


class Lesson(models.Model):
    """
    Individual lesson within a module.
    Contains the actual learning content (video, text, attachments).
    """
    module = models.ForeignKey(
        ProgramModule,
        on_delete=models.CASCADE,
        related_name='lessons',
        help_text='Module this lesson belongs to'
    )
    title = models.CharField(max_length=255, help_text='Lesson title')
    content = models.TextField(help_text='Rich text lesson content (HTML)')
    duration_minutes = models.IntegerField(
        default=0,
        help_text='Estimated duration in minutes'
    )
    order = models.IntegerField(default=0, help_text='Display order within module')
    video_url = models.URLField(
        blank=True,
        null=True,
        help_text='YouTube, Vimeo, or other video URL'
    )
    attachments = models.JSONField(
        default=list,
        blank=True,
        help_text='List of attachment URLs/files'
    )
    is_preview = models.BooleanField(
        default=False,
        help_text='Allow non-enrolled students to preview this lesson'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'lesson'
        verbose_name_plural = 'lessons'

    def __str__(self):
        return f"{self.module.title} - {self.title}"

    @property
    def program(self):
        """Get the program this lesson belongs to"""
        return self.module.program


class Enrollment(models.Model):
    """
    Tracks student enrollments in programs.
    Manages enrollment status, payment, and progress tracking.
    """

    STATUS_PENDING = 'pending'
    STATUS_ACTIVE = 'active'
    STATUS_COMPLETED = 'completed'
    STATUS_DROPPED = 'dropped'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_DROPPED, 'Dropped'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    PAYMENT_NOT_REQUIRED = 'not_required'
    PAYMENT_PENDING = 'pending'
    PAYMENT_PAID = 'paid'
    PAYMENT_REFUNDED = 'refunded'

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_NOT_REQUIRED, 'Not Required'),
        (PAYMENT_PENDING, 'Pending'),
        (PAYMENT_PAID, 'Paid'),
        (PAYMENT_REFUNDED, 'Refunded'),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        help_text='Student enrolled in the program'
    )
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name='enrollments',
        help_text='Program the student is enrolled in'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Overall completion percentage (0-100)'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default=PAYMENT_NOT_REQUIRED
    )
    payment_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    payment_reference = models.CharField(
        max_length=255,
        blank=True,
        help_text='Payment gateway reference/transaction ID'
    )

    class Meta:
        unique_together = ['student', 'program']
        ordering = ['-enrolled_at']
        verbose_name = 'enrollment'
        verbose_name_plural = 'enrollments'

    def __str__(self):
        return f"{self.student.full_name} - {self.program.title}"

    def save(self, *args, **kwargs):
        # Set payment status based on program price
        if self.program.price == 0:
            self.payment_status = self.PAYMENT_NOT_REQUIRED
            if self.status == self.STATUS_PENDING:
                self.status = self.STATUS_ACTIVE
        else:
            self.payment_amount = self.program.price

        super().save(*args, **kwargs)

    def calculate_progress(self):
        """
        Calculate and update progress percentage based on completed lessons.
        """
        total_lessons = Lesson.objects.filter(module__program=self.program).count()

        if total_lessons == 0:
            self.progress_percentage = 0
        else:
            completed_lessons = self.lesson_progress.filter(is_completed=True).count()
            self.progress_percentage = (completed_lessons / total_lessons) * 100

        # Mark as completed if all lessons done
        if self.progress_percentage >= 100 and self.status == self.STATUS_ACTIVE:
            self.status = self.STATUS_COMPLETED
            self.completed_at = timezone.now()

        self.save(update_fields=['progress_percentage', 'status', 'completed_at'])

    @property
    def is_active(self):
        """Check if enrollment is active"""
        return self.status == self.STATUS_ACTIVE

    @property
    def completed_lessons_count(self):
        """Get number of completed lessons"""
        return self.lesson_progress.filter(is_completed=True).count()

    @property
    def total_lessons_count(self):
        """Get total number of lessons in program"""
        return Lesson.objects.filter(module__program=self.program).count()


class LessonProgress(models.Model):
    """
    Tracks individual lesson completion for each enrollment.
    Records completion status, time spent, and last access time.
    """
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='lesson_progress',
        help_text='Enrollment this progress belongs to'
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='student_progress',
        help_text='Lesson being tracked'
    )
    is_completed = models.BooleanField(
        default=False,
        help_text='Whether student has completed this lesson'
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the lesson was completed'
    )
    time_spent_minutes = models.IntegerField(
        default=0,
        help_text='Total time spent on this lesson'
    )
    last_accessed = models.DateTimeField(
        auto_now=True,
        help_text='Last time student accessed this lesson'
    )

    class Meta:
        unique_together = ['enrollment', 'lesson']
        ordering = ['lesson__module__order', 'lesson__order']
        verbose_name = 'lesson progress'
        verbose_name_plural = 'lesson progress records'

    def __str__(self):
        status = "✓" if self.is_completed else "○"
        return f"{status} {self.enrollment.student.full_name} - {self.lesson.title}"

    def mark_complete(self):
        """Mark lesson as completed and update enrollment progress"""
        if not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
            self.save(update_fields=['is_completed', 'completed_at'])

            # Recalculate enrollment progress
            self.enrollment.calculate_progress()


class ProgramInstructor(models.Model):
    """
    Links instructors to programs they can teach.
    Allows multiple instructors per program and tracks assignment.
    """
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name='assigned_instructors',
        help_text='Program being taught'
    )
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_programs',
        help_text='Instructor teaching this program',
        limit_choices_to={'role': 'instructor'}
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='instructor_assignments',
        help_text='Admin who made the assignment'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_primary = models.BooleanField(
        default=False,
        help_text='Primary instructor for this program'
    )

    class Meta:
        unique_together = ['program', 'instructor']
        ordering = ['-is_primary', 'assigned_at']
        verbose_name = 'program instructor'
        verbose_name_plural = 'program instructors'

    def __str__(self):
        primary = " (Primary)" if self.is_primary else ""
        return f"{self.instructor.full_name} → {self.program.title}{primary}"
