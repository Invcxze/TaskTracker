from django.core.exceptions import ValidationError
from ..models import User
from apps.workspaces.models import UserWorkspaceRole


def update_user_permissions(user: User, data: dict) -> User:
    if "is_staff" in data:
        user.is_staff = data["is_staff"]
    if "is_superuser" in data:
        user.is_superuser = data["is_superuser"]
    user.save()

    if "role_ids" in data:
        workspace_id = data.get("workspace_id")
        if not workspace_id:
            raise ValidationError("workspace_id обязателен при назначении ролей.")

        user.workspace_roles.filter(workspace_id=workspace_id).delete()

        UserWorkspaceRole.objects.bulk_create([
            UserWorkspaceRole(user=user, workspace_id=workspace_id, role_id=role_id)
            for role_id in data["role_ids"]
        ])

    return user