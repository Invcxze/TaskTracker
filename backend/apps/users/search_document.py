
from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl.registries import registry

from .models import User, Permission, Role, RolePermission
from ..workspaces.models import Workspace

user_index = Index("users")
user_index.settings(number_of_shards=1, number_of_replicas=0)


@registry.register_document
@user_index.document
class UserDocument(Document):
    email = fields.TextField()
    fio = fields.TextField()
    is_active = fields.BooleanField()
    is_staff = fields.BooleanField()
    is_superuser = fields.BooleanField()

    permissions = fields.NestedField(
        properties={
            "code": fields.KeywordField(),
            "description": fields.TextField(),
        }
    )

    workspaces = fields.NestedField(
        properties={
            "id": fields.IntegerField(),
            "name": fields.KeywordField(),
        }
    )

    class Django:
        model = User
        related_models = [Role, Permission, RolePermission, Workspace]

    def prepare_permissions(self, instance: User):
        qs = (
            instance.workspace_roles.select_related("role")
            .prefetch_related("role__role_permissions__permission")
            .values_list("role__role_permissions__permission__code", "role__role_permissions__permission__description")
            .distinct()
        )
        return [{"code": code, "description": description} for code, description in qs if code]

    def prepare_workspaces(self, instance: User):
        qs = (
            instance.workspace_roles.select_related("workspace")
            .values_list("workspace__id", "workspace__name")
            .distinct()
        )
        return [{"id": wid, "name": wname} for wid, wname in qs if wid and wname]

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Role|Permission|RolePermission|Workspace):
            return User.objects.filter(workspace_roles__role=related_instance).distinct()
        return []