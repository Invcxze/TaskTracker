from rest_framework.exceptions import PermissionDenied
from apps.tasks.models import Label
from apps.tasks.selectors.users import user_has_access_to_workspace


class LabelService:
    @staticmethod
    def create(data, user):
        workspace = data.get("workspace")
        if not user_has_access_to_workspace(user, workspace):
            raise PermissionDenied("You do not have access to this workspace.")
        return Label.objects.create(**data)

    @staticmethod
    def update(label: Label, data, user):
        if not user_has_access_to_workspace(user, label.workspace):
            raise PermissionDenied("You do not have access to this workspace.")
        for attr, value in data.items():
            setattr(label, attr, value)
        label.save()
        return label
