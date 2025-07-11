# Generated by Django 5.2.3 on 2025-06-26 13:26

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('workspaces', '0002_alter_userworkspacerole_options_workspace_created_by'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='userworkspacerole',
            unique_together={('user', 'workspace', 'role')},
        ),
    ]
