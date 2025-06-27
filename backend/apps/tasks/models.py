from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

from apps.users.models import User
from apps.workspaces.models import Workspace


class TaskType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon = models.CharField(max_length=30, blank=True, null=True)  # Иконка для визуального отображения
    color = models.CharField(max_length=7, default="#3498db")  # HEX-цвет

    def __str__(self):
        return self.name


class TaskStatus(models.Model):
    name = models.CharField(max_length=50)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="statuses")
    order = models.PositiveIntegerField(default=0)
    is_default = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("name", "workspace")
        ordering = ["order"]

    def __str__(self):
        return f"{self.name} ({self.workspace.name})"


class Label(models.Model):
    name = models.CharField(max_length=50)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="labels")
    color = models.CharField(max_length=7, default="#3498db")  # HEX-цвет

    class Meta:
        unique_together = ("name", "workspace")

    def __str__(self):
        return f"{self.name} ({self.workspace.name})"


class Task(models.Model):
    PRIORITY_CHOICES = (
        ("low", "Низкий"),
        ("medium", "Средний"),
        ("high", "Высокий"),
        ("critical", "Критический"),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="medium")
    estimated_time = models.PositiveIntegerField(null=True, blank=True, help_text="Оценка времени в часах")
    actual_time = models.PositiveIntegerField(null=True, blank=True, help_text="Фактически затраченное время в часах")

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="tasks")
    status = models.ForeignKey(TaskStatus, on_delete=models.SET_NULL, null=True, blank=True)
    task_type = models.ForeignKey(TaskType, on_delete=models.SET_NULL, null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_tasks")
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tasks")
    parent_task = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="subtasks")

    labels = models.ManyToManyField(Label, blank=True, related_name="tasks")
    watchers = models.ManyToManyField(User, blank=True, related_name="watched_tasks")

    history = GenericRelation("TaskLog")

    def __str__(self):
        return f"{self.title} ({self.workspace.name})"


class TaskDependency(models.Model):
    DEPENDENCY_TYPES = (
        ("blocks", "Блокирует"),
        ("is_blocked_by", "Блокируется"),
        ("relates_to", "Связана с"),
    )

    from_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="outgoing_dependencies")
    to_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="incoming_dependencies")
    dependency_type = models.CharField(max_length=20, choices=DEPENDENCY_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("from_task", "to_task", "dependency_type")

    def __str__(self):
        return f"{self.from_task} {self.get_dependency_type_display()} {self.to_task}"


class TaskComment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_pinned = models.BooleanField(default=False)

    def __str__(self):
        return f"Комментарий к {self.task} от {self.author}"


class TaskAttachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="task_attachments/%Y/%m/%d/")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        if not self.file_name:
            self.file_name = self.file.name
        if not self.file_size and self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.file_name} ({self.task})"


class TaskChecklistItem(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="checklist_items")
    text = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def save(self, *args, **kwargs):
        if self.is_completed and not self.completed_at:
            self.completed_at = timezone.now()
        elif not self.is_completed and self.completed_at:
            self.completed_at = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.text} ({'✓' if self.is_completed else '✗'})"


class TaskLog(models.Model):
    ACTION_CHOICES = (
        ("create", "Создание"),
        ("update", "Обновление"),
        ("delete", "Удаление"),
        ("comment", "Комментарий"),
        ("attachment", "Вложение"),
    )

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="change_logs")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    changes = models.JSONField(null=True, blank=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return f"{self.get_action_display()} для {self.task} в {self.timestamp}"
