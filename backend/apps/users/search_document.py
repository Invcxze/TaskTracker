from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl.registries import registry

from .models import User, Permission, Role, RolePermission
from ..workspaces.models import Workspace

user_index = Index("users")
user_index.settings(number_of_shards=1, number_of_replicas=0)


@registry.register_document
@user_index.document
class UserDocument(Document):
    # Статичные поля пользователя
    email = fields.TextField()
    fio = fields.TextField()
    is_active = fields.BooleanField()
    is_staff = fields.BooleanField()
    is_superuser = fields.BooleanField()

    # Права пользователя по ролям в воркспейсах
    permissions = fields.NestedField(
        properties={
            "code": fields.KeywordField(),  # Для фильтрации и агрегаций
            "description": fields.TextField(),  # Для полнотекстового поиска
        }
    )

    # Список рабочих пространств, к которым привязан пользователь
    workspaces = fields.NestedField(
        properties={
            "id": fields.IntegerField(),
            "name": fields.KeywordField(),  # Для точной фильтрации по имени
        }
    )

    class Django:
        model = User
        related_models = [Role, Permission, RolePermission, Workspace]

    def prepare_permissions(self, instance: User):
        """
        Подготовка прав пользователя через роли.
        """
        qs = (
            instance.workspace_roles.select_related("role")
            .prefetch_related("role__role_permissions__permission")
            .values_list("role__role_permissions__permission__code", "role__role_permissions__permission__description")
            .distinct()
        )
        return [{"code": code, "description": description} for code, description in qs if code]

    def prepare_workspaces(self, instance: User):
        """
        Подготовка рабочих пространств, к которым пользователь привязан.
        """
        qs = (
            instance.workspace_roles.select_related("workspace")
            .values_list("workspace__id", "workspace__name")
            .distinct()
        )
        return [{"id": wid, "name": wname} for wid, wname in qs if wid and wname]
