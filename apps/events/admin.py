from django.contrib import admin
from .models import Testimonial


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    """
    Admin interface for managing testimonials / success stories.
    """
    list_display = ['name', 'role', 'rating', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'rating']
    list_editable = ['is_active', 'order', 'rating']
    search_fields = ['name', 'text']
    ordering = ['order', '-created_at']
