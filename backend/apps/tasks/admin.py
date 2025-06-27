from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    TaskType,
    TaskStatus,
    Label,
    Task,
    TaskDependency,
    TaskComment,
    TaskAttachment,
    TaskChecklistItem,
    TaskLog,
)


# 1. Вспомогательные классы
class TaskStatusInline(admin.TabularInline):
    model = TaskStatus
    extra = 0
    ordering = ["order"]
    fields = ["name", "order", "is_default", "is_closed"]
    show_change_link = True


class LabelInline(admin.TabularInline):
    model = Label
    extra = 0
    fields = ["name", "color"]
    show_change_link = True


class TaskDependencyInline(admin.TabularInline):
    model = TaskDependency
    fk_name = "from_task"
    extra = 0
    fields = ["to_task", "dependency_type", "created_at"]
    readonly_fields = ["created_at"]
    autocomplete_fields = ["to_task"]


class TaskCommentInline(admin.TabularInline):
    model = TaskComment
    extra = 0
    fields = ["author", "content", "is_pinned", "created_at"]
    readonly_fields = ["created_at"]
    autocomplete_fields = ["author"]


class TaskAttachmentInline(admin.StackedInline):
    model = TaskAttachment
    extra = 0
    fields = ["file", "file_name", "file_size", "uploaded_by", "uploaded_at"]
    readonly_fields = ["file_name", "file_size", "uploaded_at"]
    autocomplete_fields = ["uploaded_by"]


class TaskChecklistItemInline(admin.TabularInline):
    model = TaskChecklistItem
    extra = 0
    fields = ["text", "is_completed", "order", "completed_at"]
    readonly_fields = ["completed_at"]
    ordering = ["order"]


class TaskLogInline(admin.TabularInline):
    model = TaskLog
    extra = 0
    fields = ["action", "user", "timestamp", "related_object"]
    readonly_fields = ["action", "user", "timestamp", "related_object"]
    can_delete = False

    def related_object(self, obj):
        if obj.content_type and obj.object_id:
            model = obj.content_type.model_class()
            try:
                instance = model.objects.get(pk=obj.object_id)
                url = reverse(f"admin:{model._meta.app_label}_{model._meta.model_name}_change", args=[obj.object_id])
                return format_html('<a href="{}">{}</a>', url, str(instance))
            except model.DoesNotExist:
                return "-"
        return "-"

    related_object.short_description = "Связанный объект"


# 2. Основные классы ModelAdmin
@admin.register(TaskType)
class TaskTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "color_display", "tasks_count")
    search_fields = ("name", "icon")
    list_editable = ("icon",)
    ordering = ("name",)

    def color_display(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #000;"></div>', obj.color
        )

    color_display.short_description = "Цвет"

    def tasks_count(self, obj):
        return obj.task_set.count()

    tasks_count.short_description = "Задач"


@admin.register(TaskStatus)
class TaskStatusAdmin(admin.ModelAdmin):
    list_display = ("name", "workspace_link", "order", "is_default", "is_closed", "tasks_count")
    list_filter = ("is_default", "is_closed", "workspace")
    list_editable = ("order", "is_default", "is_closed")
    search_fields = ("name", "workspace__name")
    autocomplete_fields = ["workspace"]
    ordering = ["workspace", "order"]

    def workspace_link(self, obj):
        url = reverse("admin:workspaces_workspace_change", args=[obj.workspace.id])
        return format_html('<a href="{}">{}</a>', url, obj.workspace.name)

    workspace_link.short_description = "Рабочее пространство"

    def tasks_count(self, obj):
        return obj.task_set.count()

    tasks_count.short_description = "Задач"


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ("name", "workspace_link", "color_display", "tasks_count")
    list_filter = ("workspace",)
    search_fields = ("name", "workspace__name")
    autocomplete_fields = ["workspace"]
    ordering = ["workspace", "name"]

    def workspace_link(self, obj):
        url = reverse("admin:workspaces_workspace_change", args=[obj.workspace.id])
        return format_html('<a href="{}">{}</a>', url, obj.workspace.name)

    workspace_link.short_description = "Рабочее пространство"

    def color_display(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #000;"></div>', obj.color
        )

    color_display.short_description = "Цвет"

    def tasks_count(self, obj):
        return obj.tasks.count()

    tasks_count.short_description = "Задач"


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "workspace_link",
        "status_link",
        "priority_display",
        "assignee_link",
        "due_date",
        "created_at",
    )
    list_filter = ("workspace", "status", "priority", "task_type", "created_at", "due_date")
    search_fields = ("title", "description", "workspace__name", "status__name", "assignee__email")
    autocomplete_fields = [
        "workspace",
        "status",
        "task_type",
        "creator",
        "assignee",
        "parent_task",
        "labels",
        "watchers",
    ]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [TaskDependencyInline, TaskCommentInline, TaskAttachmentInline, TaskChecklistItemInline, TaskLogInline]
    fieldsets = (
        (
            "Основное",
            {"fields": ("title", "description", "workspace", "status", "task_type", "priority", "parent_task")},
        ),
        (
            "Время",
            {
                "fields": ("due_date", "estimated_time", "actual_time", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
        ("Участники", {"fields": ("creator", "assignee", "watchers")}),
        ("Классификация", {"fields": ("labels",), "classes": ("collapse",)}),
    )
    date_hierarchy = "created_at"
    list_per_page = 25

    def workspace_link(self, obj):
        url = reverse("admin:workspaces_workspace_change", args=[obj.workspace.id])
        return format_html('<a href="{}">{}</a>', url, obj.workspace.name)

    workspace_link.short_description = "Пространство"

    def status_link(self, obj):
        if obj.status:
            url = reverse("admin:tasks_taskstatus_change", args=[obj.status.id])
            return format_html('<a href="{}">{}</a>', url, obj.status.name)
        return "-"

    status_link.short_description = "Статус"

    def assignee_link(self, obj):
        if obj.assignee:
            url = reverse("admin:users_user_change", args=[obj.assignee.id])
            return format_html('<a href="{}">{}</a>', url, obj.assignee.email)
        return "-"

    assignee_link.short_description = "Исполнитель"

    def priority_display(self, obj):
        priorities = dict(Task.PRIORITY_CHOICES)
        colors = {"low": "#3498db", "medium": "#2ecc71", "high": "#f39c12", "critical": "#e74c3c"}
        color = colors.get(obj.priority, "#000")
        return format_html(
            '<div style="display: inline-block; padding: 2px 8px; background-color: {}; color: white;'
            ' border-radius: 4px;">{}</div>',
            color,
            priorities.get(obj.priority, obj.priority),
        )

    priority_display.short_description = "Приоритет"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("workspace", "status", "task_type", "creator", "assignee", "parent_task")
            .prefetch_related("labels", "watchers")
        )


@admin.register(TaskDependency)
class TaskDependencyAdmin(admin.ModelAdmin):
    list_display = ("from_task_link", "to_task_link", "dependency_type_display", "created_at")
    list_filter = ("dependency_type", "created_at")
    search_fields = ("from_task__title", "to_task__title", "dependency_type")
    autocomplete_fields = ["from_task", "to_task"]
    date_hierarchy = "created_at"
    readonly_fields = ["created_at"]

    def from_task_link(self, obj):
        url = reverse("admin:tasks_task_change", args=[obj.from_task.id])
        return format_html('<a href="{}">{}</a>', url, obj.from_task.title)

    from_task_link.short_description = "Исходная задача"

    def to_task_link(self, obj):
        url = reverse("admin:tasks_task_change", args=[obj.to_task.id])
        return format_html('<a href="{}">{}</a>', url, obj.to_task.title)

    to_task_link.short_description = "Зависимая задача"

    def dependency_type_display(self, obj):
        return obj.get_dependency_type_display()

    dependency_type_display.short_description = "Тип зависимости"


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ("task_link", "author_link", "is_pinned", "created_at", "content_preview")
    list_filter = ("is_pinned", "created_at")
    search_fields = ("task__title", "author__email", "content")
    autocomplete_fields = ["task", "author"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"

    def task_link(self, obj):
        url = reverse("admin:tasks_task_change", args=[obj.task.id])
        return format_html('<a href="{}">{}</a>', url, obj.task.title)

    task_link.short_description = "Задача"

    def author_link(self, obj):
        if obj.author:
            url = reverse("admin:users_user_change", args=[obj.author.id])
            return format_html('<a href="{}">{}</a>', url, obj.author.email)
        return "-"

    author_link.short_description = "Автор"

    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content

    content_preview.short_description = "Содержание"


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ("task_link", "file_name", "file_size_mb", "uploaded_by_link", "uploaded_at")
    list_filter = ("uploaded_at",)
    search_fields = ("task__title", "file_name", "uploaded_by__email")
    autocomplete_fields = ["task", "uploaded_by"]
    readonly_fields = ["uploaded_at", "file_size"]
    date_hierarchy = "uploaded_at"

    def task_link(self, obj):
        url = reverse("admin:tasks_task_change", args=[obj.task.id])
        return format_html('<a href="{}">{}</a>', url, obj.task.title)

    task_link.short_description = "Задача"

    def uploaded_by_link(self, obj):
        if obj.uploaded_by:
            url = reverse("admin:users_user_change", args=[obj.uploaded_by.id])
            return format_html('<a href="{}">{}</a>', url, obj.uploaded_by.email)
        return "-"

    uploaded_by_link.short_description = "Загрузил"

    def file_size_mb(self, obj):
        return f"{obj.file_size / (1024 * 1024):.2f} MB" if obj.file_size else "-"

    file_size_mb.short_description = "Размер"


@admin.register(TaskChecklistItem)
class TaskChecklistItemAdmin(admin.ModelAdmin):
    list_display = ("task_link", "text_preview", "is_completed", "completed_at", "order")
    list_filter = ("is_completed", "created_at", "completed_at")
    list_editable = ("is_completed", "order")
    search_fields = ("task__title", "text")
    autocomplete_fields = ["task"]
    readonly_fields = ["created_at", "completed_at"]
    ordering = ["task", "order"]

    def task_link(self, obj):
        url = reverse("admin:tasks_task_change", args=[obj.task.id])
        return format_html('<a href="{}">{}</a>', url, obj.task.title)

    task_link.short_description = "Задача"

    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text

    text_preview.short_description = "Пункт"


@admin.register(TaskLog)
class TaskLogAdmin(admin.ModelAdmin):
    list_display = ("task_link", "action_display", "user_link", "timestamp", "related_object_link")
    list_filter = ("action", "timestamp")
    search_fields = ("task__title", "user__email")
    readonly_fields = ["task", "user", "action", "timestamp", "changes", "content_type", "object_id"]
    date_hierarchy = "timestamp"

    def task_link(self, obj):
        url = reverse("admin:tasks_task_change", args=[obj.task.id])
        return format_html('<a href="{}">{}</a>', url, obj.task.title)

    task_link.short_description = "Задача"

    def user_link(self, obj):
        if obj.user:
            url = reverse("admin:users_user_change", args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.email)
        return "-"

    user_link.short_description = "Пользователь"

    def action_display(self, obj):
        return obj.get_action_display()

    action_display.short_description = "Действие"

    def related_object_link(self, obj):
        if obj.content_type and obj.object_id:
            model = obj.content_type.model_class()
            try:
                instance = model.objects.get(pk=obj.object_id)
                url = reverse(f"admin:{model._meta.app_label}_{model._meta.model_name}_change", args=[obj.object_id])
                return format_html('<a href="{}">{}</a>', url, str(instance))
            except model.DoesNotExist:
                return "-"
        return "-"

    related_object_link.short_description = "Связанный объект"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("task", "user", "content_type")
