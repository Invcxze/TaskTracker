from apps.workspaces.models import Workspace


def get_user_workspaces(user):
    return Workspace.objects.filter(user_roles__user=user)


def filter_by_user_workspaces(model_cls, user, workspace_field="workspace"):
    user_workspaces = get_user_workspaces(user)
    filter_kwargs = {f"{workspace_field}__in": user_workspaces}
    return model_cls.objects.filter(**filter_kwargs)


def filter_by_user_workspace_and_related_field(model_cls, user, related_field_path):
    filter_kwargs = {f"{related_field_path}__user_roles__user": user}
    return model_cls.objects.filter(**filter_kwargs)


def user_has_access_to_workspace(user, workspace):
    return workspace and Workspace.objects.filter(id=workspace.id, user_roles__user=user).exists()
