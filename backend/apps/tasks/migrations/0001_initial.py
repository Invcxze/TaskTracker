# Generated by Django 5.2.3 on 2025-06-25 22:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('workspaces', '0002_alter_userworkspacerole_options_workspace_created_by'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('icon', models.CharField(blank=True, max_length=30, null=True)),
                ('color', models.CharField(default='#3498db', max_length=7)),
            ],
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('color', models.CharField(default='#3498db', max_length=7)),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='labels', to='workspaces.workspace')),
            ],
            options={
                'unique_together': {('name', 'workspace')},
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('due_date', models.DateTimeField(blank=True, null=True)),
                ('priority', models.CharField(choices=[('low', 'Низкий'), ('medium', 'Средний'), ('high', 'Высокий'), ('critical', 'Критический')], default='medium', max_length=20)),
                ('estimated_time', models.PositiveIntegerField(blank=True, help_text='Оценка времени в часах', null=True)),
                ('actual_time', models.PositiveIntegerField(blank=True, help_text='Фактически затраченное время в часах', null=True)),
                ('assignee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_tasks', to=settings.AUTH_USER_MODEL)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_tasks', to=settings.AUTH_USER_MODEL)),
                ('labels', models.ManyToManyField(blank=True, related_name='tasks', to='tasks.label')),
                ('parent_task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subtasks', to='tasks.task')),
                ('watchers', models.ManyToManyField(blank=True, related_name='watched_tasks', to=settings.AUTH_USER_MODEL)),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='workspaces.workspace')),
            ],
        ),
        migrations.CreateModel(
            name='TaskAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='task_attachments/%Y/%m/%d/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('file_name', models.CharField(max_length=255)),
                ('file_size', models.PositiveIntegerField()),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='tasks.task')),
                ('uploaded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TaskChecklistItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
                ('is_completed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checklist_items', to='tasks.task')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='TaskComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_pinned', models.BooleanField(default=False)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='tasks.task')),
            ],
        ),
        migrations.CreateModel(
            name='TaskLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('create', 'Создание'), ('update', 'Обновление'), ('delete', 'Удаление'), ('comment', 'Комментарий'), ('attachment', 'Вложение')], max_length=20)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('changes', models.JSONField(blank=True, null=True)),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.contenttype')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='change_logs', to='tasks.task')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TaskStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('order', models.PositiveIntegerField(default=0)),
                ('is_default', models.BooleanField(default=False)),
                ('is_closed', models.BooleanField(default=False)),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='statuses', to='workspaces.workspace')),
            ],
            options={
                'ordering': ['order'],
                'unique_together': {('name', 'workspace')},
            },
        ),
        migrations.AddField(
            model_name='task',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tasks.taskstatus'),
        ),
        migrations.AddField(
            model_name='task',
            name='task_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tasks.tasktype'),
        ),
        migrations.CreateModel(
            name='TaskDependency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dependency_type', models.CharField(choices=[('blocks', 'Блокирует'), ('is_blocked_by', 'Блокируется'), ('relates_to', 'Связана с')], max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('from_task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outgoing_dependencies', to='tasks.task')),
                ('to_task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incoming_dependencies', to='tasks.task')),
            ],
            options={
                'unique_together': {('from_task', 'to_task', 'dependency_type')},
            },
        ),
    ]
