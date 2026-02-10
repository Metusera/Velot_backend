from django.db import models


class ProgramQuerySet(models.QuerySet):
    """
    Custom queryset for Program model with common filters.
    """

    def published(self):
        """Return only published programs"""
        return self.filter(status='published')

    def draft(self):
        """Return only draft programs"""
        return self.filter(status='draft')

    def archived(self):
        """Return only archived programs"""
        return self.filter(status='archived')

    def by_category(self, category_slug):
        """Filter by category slug"""
        return self.filter(category__slug=category_slug)

    def by_level(self, level):
        """Filter by level"""
        return self.filter(level=level)


class ProgramManager(models.Manager):
    """
    Custom manager for Program model.
    """

    def get_queryset(self):
        return ProgramQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()

    def draft(self):
        return self.get_queryset().draft()

    def archived(self):
        return self.get_queryset().archived()

    def by_category(self, category_slug):
        return self.get_queryset().by_category(category_slug)

    def by_level(self, level):
        return self.get_queryset().by_level(level)
