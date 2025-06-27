from django.contrib import admin
from .models import Workspace, UserWorkspaceRole
from apps.tasks.admin import TaskStatusInline, LabelInline


class UserWorkspaceRoleInline(admin.TabularInline):
    model = UserWorkspaceRole
    extra = 1
    autocomplete_fields = ["user", "role"]
    verbose_name = "Роль пользователя"
    verbose_name_plural = "Роли пользователей"
    fields = ("user", "role")  # Исправлено


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    search_fields = ["name"]  # Добавлено
    list_filter = ["created_at"]  # Добавлено
    inlines = [TaskStatusInline, LabelInline, UserWorkspaceRoleInline]  # Добавлен инлайн
    list_display = ("name", "statuses_count", "labels_count", "tasks_count")

    def statuses_count(self, obj):
        return obj.statuses.count()

    statuses_count.short_description = "Статусов"

    def labels_count(self, obj):
        return obj.labels.count()

    labels_count.short_description = "Меток"

    def tasks_count(self, obj):
        return obj.tasks.count()

    tasks_count.short_description = "Задач"


@admin.register(UserWorkspaceRole)
class UserWorkspaceRoleAdmin(admin.ModelAdmin):
    list_display = ("user", "workspace", "role")
    list_filter = ("workspace", "role")
    search_fields = ("user__email", "workspace__name", "role__name")
    autocomplete_fields = ["user", "workspace", "role"]
    list_select_related = ["user", "workspace", "role"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "workspace", "role")
