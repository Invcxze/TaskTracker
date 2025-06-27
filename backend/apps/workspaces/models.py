from django.db import models
from apps.users.models import User, Role


class Workspace(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_workspaces")

    def __str__(self):
        return self.name


class UserWorkspaceRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="workspace_roles")
    workspace = models.ForeignKey("Workspace", on_delete=models.CASCADE, related_name="user_roles")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="user_workspace_roles")

    class Meta:
        unique_together = ("user", "workspace", "role")
        ordering = ["workspace", "user"]

    def __str__(self):
        return f"{self.user.email} - {self.role.name} в {self.workspace.name}"
