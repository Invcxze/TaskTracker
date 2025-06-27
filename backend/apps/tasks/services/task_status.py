from rest_framework.exceptions import PermissionDenied

from apps.tasks.models import TaskStatus
from apps.tasks.selectors.users import user_has_access_to_workspace


class TaskStatusService:
    @staticmethod
    def create(data, user):
        workspace = data.get("workspace")
        if not user_has_access_to_workspace(user, workspace):
            raise PermissionDenied("You do not have access to this workspace.")
        return TaskStatus.objects.create(**data)
