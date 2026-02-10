from django.contrib import admin
from .models import Category, Program


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for Category model.
    """
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    """
    Admin interface for Program model.
    """
    list_display = ['title', 'category', 'level', 'price', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'level', 'category', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at', 'published_at', 'created_by']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'category')
        }),
        ('Details', {
            'fields': ('duration', 'price', 'level', 'thumbnail')
        }),
        ('Status', {
            'fields': ('status', 'published_at')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """
        Override to set created_by to current user if not set.
        """
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
