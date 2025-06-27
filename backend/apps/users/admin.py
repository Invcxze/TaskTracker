from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Role, Permission, RolePermission


class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 1
    autocomplete_fields = ["permission"]
    verbose_name = "Разрешение роли"
    verbose_name_plural = "Разрешения роли"


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "permissions_count", "users_count")
    search_fields = ("name",)
    inlines = [RolePermissionInline]
    ordering = ["name"]

    def permissions_count(self, obj):
        return obj.role_permissions.count()

    permissions_count.short_description = "Разрешений"

    def users_count(self, obj):
        return User.objects.filter(workspace_roles__role=obj).distinct().count()

    users_count.short_description = "Пользователей"

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("role_permissions")


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("code", "description", "roles_count")
    search_fields = ("code", "description")
    list_filter = ("permission_roles__role",)
    ordering = ["code"]

    def roles_count(self, obj):
        return obj.permission_roles.count()

    roles_count.short_description = "Ролей"

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("permission_roles")


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ("role", "permission")
    list_filter = ("role",)
    autocomplete_fields = ["role", "permission"]
    search_fields = ("role__name", "permission__code")
    ordering = ["role__name", "permission__code"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("role", "permission")


class UserWorkspaceRoleInline(admin.TabularInline):
    from apps.workspaces.models import UserWorkspaceRole

    model = UserWorkspaceRole
    extra = 1
    autocomplete_fields = ["workspace", "role"]
    verbose_name = "Роль в рабочем пространстве"
    verbose_name_plural = "Роли в рабочих пространствах"
    fields = ("workspace", "role")  # Исправлено


class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Персональная информация", {"fields": ("fio",)}),
        (
            "Права доступа",
            {
                "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
            },
        ),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "fio", "password1", "password2", "is_staff", "is_superuser"),
            },
        ),
    )
    list_display = ("email", "fio", "is_active", "is_staff", "is_superuser", "last_login")
    list_filter = ("is_active", "is_staff", "is_superuser", "last_login")
    search_fields = ("email", "fio")
    ordering = ("email",)
    filter_horizontal = ("groups", "user_permissions")
    readonly_fields = ("last_login", "date_joined")
    inlines = [UserWorkspaceRoleInline]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("workspace_roles")


admin.site.register(User, CustomUserAdmin)
