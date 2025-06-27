from django.db import models
from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl.registries import registry

from .models import Task, TaskStatus, TaskType, Label, User, Workspace, TaskComment, TaskChecklistItem

task_index = Index("tasks")
task_index.settings(number_of_shards=1, number_of_replicas=0)


@registry.register_document
@task_index.document
class TaskDocument(Document):
    id = fields.IntegerField()
    title = fields.TextField(
        analyzer="standard", fields={"keyword": fields.KeywordField(), "suggest": fields.CompletionField()}
    )
    description = fields.TextField(analyzer="standard")
    created_at = fields.DateField()
    updated_at = fields.DateField()
    due_date = fields.DateField()
    priority = fields.KeywordField()
    estimated_time = fields.IntegerField()
    actual_time = fields.IntegerField()
    is_closed = fields.BooleanField()

    workspace = fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
            "name": fields.KeywordField(),
        }
    )

    status = fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
            "name": fields.KeywordField(),
            "is_closed": fields.BooleanField(),
        }
    )

    task_type = fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
            "name": fields.KeywordField(),
            "icon": fields.KeywordField(),
            "color": fields.KeywordField(),
        }
    )

    creator = fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
            "email": fields.KeywordField(),
            "fio": fields.TextField(),
        }
    )

    assignee = fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
            "email": fields.KeywordField(),
            "fio": fields.TextField(),
        }
    )

    parent_task = fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
            "title": fields.TextField(),
        }
    )

    labels = fields.NestedField(
        properties={
            "id": fields.IntegerField(),
            "name": fields.KeywordField(),
            "color": fields.KeywordField(),
        }
    )

    watchers = fields.NestedField(
        properties={
            "id": fields.IntegerField(),
            "email": fields.KeywordField(),
            "fio": fields.TextField(),
        }
    )

    comments = fields.NestedField(
        properties={
            "id": fields.IntegerField(),
            "content": fields.TextField(analyzer="standard"),
            "author": fields.ObjectField(
                properties={
                    "id": fields.IntegerField(),
                    "fio": fields.TextField(),
                }
            ),
        }
    )

    checklist_items = fields.NestedField(
        properties={
            "id": fields.IntegerField(),
            "text": fields.TextField(),
            "is_completed": fields.BooleanField(),
        }
    )

    class Django:
        model = Task
        related_models = [TaskStatus, TaskType, Label, User, Workspace, TaskComment, TaskChecklistItem]

    def prepare_is_closed(self, instance: Task):
        """Вычисляемое поле: закрыта ли задача"""
        return instance.status.is_closed if instance.status else False

    def prepare_workspace(self, instance: Task):
        if instance.workspace:
            return {"id": instance.workspace.id, "name": instance.workspace.name}
        return None

    def prepare_status(self, instance: Task):
        if instance.status:
            return {"id": instance.status.id, "name": instance.status.name, "is_closed": instance.status.is_closed}
        return None

    def prepare_task_type(self, instance: Task):
        if instance.task_type:
            return {
                "id": instance.task_type.id,
                "name": instance.task_type.name,
                "icon": instance.task_type.icon,
                "color": instance.task_type.color,
            }
        return None

    def prepare_creator(self, instance: Task):
        if instance.creator:
            return {"id": instance.creator.id, "email": instance.creator.email, "fio": instance.creator.fio}
        return None

    def prepare_assignee(self, instance: Task):
        if instance.assignee:
            return {"id": instance.assignee.id, "email": instance.assignee.email, "fio": instance.assignee.fio}
        return None

    def prepare_parent_task(self, instance: Task):
        if instance.parent_task:
            return {"id": instance.parent_task.id, "title": instance.parent_task.title}
        return None

    def prepare_labels(self, instance: Task):
        return [{"id": label.id, "name": label.name, "color": label.color} for label in instance.labels.all()]

    def prepare_watchers(self, instance: Task):
        return [{"id": user.id, "email": user.email, "fio": user.fio} for user in instance.watchers.all()]

    def prepare_comments(self, instance: Task):
        return [
            {
                "id": comment.id,
                "content": comment.content,
                "author": {"id": comment.author.id, "fio": comment.author.fio} if comment.author else None,
            }
            for comment in instance.comments.all()
        ]

    def prepare_checklist_items(self, instance: Task):
        return [
            {"id": item.id, "text": item.text, "is_completed": item.is_completed}
            for item in instance.checklist_items.all()
        ]

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, TaskStatus):
            return related_instance.tasks.all()

        if isinstance(related_instance, TaskType):
            return related_instance.task_set.all()

        if isinstance(related_instance, Label):
            return related_instance.tasks.all()

        if isinstance(related_instance, User):
            return Task.objects.filter(
                models.Q(creator=related_instance)
                | models.Q(assignee=related_instance)
                | models.Q(watchers=related_instance)
            ).distinct()

        if isinstance(related_instance, Workspace):
            return related_instance.tasks.all()

        if isinstance(related_instance, TaskComment):
            return [related_instance.task]

        if isinstance(related_instance, TaskChecklistItem):
            return [related_instance.task]

        return None
