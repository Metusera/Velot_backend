"""
Rename 'viewer' role to 'learner' across User and UserInvitation models.
"""

from django.db import migrations, models


def rename_viewer_to_learner(apps, schema_editor):
    """Update all existing 'viewer' roles to 'learner'."""
    User = apps.get_model('users', 'User')
    UserInvitation = apps.get_model('users', 'UserInvitation')

    User.objects.filter(role='viewer').update(role='learner')
    UserInvitation.objects.filter(role='viewer').update(role='learner')


def rename_learner_to_viewer(apps, schema_editor):
    """Reverse: update all 'learner' roles back to 'viewer'."""
    User = apps.get_model('users', 'User')
    UserInvitation = apps.get_model('users', 'UserInvitation')

    User.objects.filter(role='learner').update(role='viewer')
    UserInvitation.objects.filter(role='learner').update(role='viewer')


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_add_instructor_role_and_invitation_system'),
    ]

    operations = [
        # Update the field choices and default
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(
                choices=[
                    ('super_admin', 'Super Admin'),
                    ('admin', 'Admin'),
                    ('instructor', 'Instructor'),
                    ('editor', 'Editor'),
                    ('learner', 'Learner'),
                ],
                default='learner',
                help_text='User role determines permissions',
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='userinvitation',
            name='role',
            field=models.CharField(
                choices=[
                    ('super_admin', 'Super Admin'),
                    ('admin', 'Admin'),
                    ('instructor', 'Instructor'),
                    ('editor', 'Editor'),
                    ('learner', 'Learner'),
                ],
                help_text='Role that will be assigned when invitation is accepted',
                max_length=20,
            ),
        ),
        # Rename existing data
        migrations.RunPython(rename_viewer_to_learner, rename_learner_to_viewer),
    ]
