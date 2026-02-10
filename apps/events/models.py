from django.db import models


class Testimonial(models.Model):
    """
    Success stories / testimonials displayed on the public site.
    Created via Django admin.
    """
    name = models.CharField(max_length=150, help_text='Full name of the person')
    role = models.CharField(
        max_length=100,
        default='Course Graduate',
        help_text='e.g., "Course Graduate", "Data Analyst at XYZ"'
    )
    text = models.TextField(help_text='Testimonial quote')
    rating = models.PositiveSmallIntegerField(
        default=5,
        help_text='Rating from 1 to 5'
    )
    image = models.ImageField(
        upload_to='testimonials/',
        blank=True,
        null=True,
        help_text='Profile image (optional)'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Only active testimonials are shown on the site'
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text='Display order (lower = first)'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f'{self.name} — {self.role}'
