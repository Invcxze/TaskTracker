from rest_framework import serializers
from apps.tasks.models import (
    TaskType,
    TaskStatus,
    Label,
    Task,
    TaskDependency,
    TaskComment,
    TaskAttachment,
    TaskChecklistItem,
    TaskLog,
)
from apps.users.serializers.manage import UserSerializer
from apps.workspaces.serializers.workspace import WorkspaceSerializer


class TaskTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskType
        fields = "__all__"


class TaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskStatus
        fields = "__all__"


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    creator_details = UserSerializer(source="creator", read_only=True)
    assignee_details = UserSerializer(source="assignee", read_only=True)
    status_details = TaskStatusSerializer(source="status", read_only=True)
    task_type_details = TaskTypeSerializer(source="task_type", read_only=True)
    workspace_details = WorkspaceSerializer(source="workspace", read_only=True)
    labels_details = LabelSerializer(source="labels", many=True, read_only=True)
    watchers_details = UserSerializer(source="watchers", many=True, read_only=True)
    parent_task_details = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = "__all__"
        extra_kwargs = {
            "creator": {"write_only": True},
            "assignee": {"write_only": True},
            "status": {"write_only": True},
            "task_type": {"write_only": True},
            "workspace": {"write_only": True},
            "labels": {"write_only": True},
            "watchers": {"write_only": True},
            "parent_task": {"write_only": True},
        }

    def get_parent_task_details(self, obj):
        if obj.parent_task:
            return {
                "id": obj.parent_task.id,
                "title": obj.parent_task.title,
                "status": obj.parent_task.status.name if obj.parent_task.status else None,
            }
        return None

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)


class TaskDependencySerializer(serializers.ModelSerializer):
    from_task_details = serializers.SerializerMethodField()
    to_task_details = serializers.SerializerMethodField()

    class Meta:
        model = TaskDependency
        fields = "__all__"
        extra_kwargs = {
            "from_task": {"write_only": True},
            "to_task": {"write_only": True},
        }

    def get_from_task_details(self, obj):
        return {"id": obj.from_task.id, "title": obj.from_task.title}

    def get_to_task_details(self, obj):
        return {"id": obj.to_task.id, "title": obj.to_task.title}

    def validate(self, data):
        # Проверка, что задачи в одном workspace
        if data["from_task"].workspace != data["to_task"].workspace:
            raise serializers.ValidationError("Tasks must be in the same workspace")
        return data


class TaskCommentSerializer(serializers.ModelSerializer):
    author_details = UserSerializer(source="author", read_only=True)

    class Meta:
        model = TaskComment
        fields = "__all__"
        extra_kwargs = {
            "author": {"write_only": True},
            "task": {"write_only": True},
        }

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class TaskAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_details = UserSerializer(source="uploaded_by", read_only=True)

    class Meta:
        model = TaskAttachment
        fields = "__all__"
        extra_kwargs = {
            "uploaded_by": {"write_only": True},
            "task": {"write_only": True},
        }

    def create(self, validated_data):
        validated_data["uploaded_by"] = self.context["request"].user
        validated_data["file_name"] = validated_data["file"].name
        validated_data["file_size"] = validated_data["file"].size
        return super().create(validated_data)


class TaskChecklistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskChecklistItem
        fields = "__all__"
        extra_kwargs = {
            "task": {"write_only": True},
        }


class TaskLogSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source="user", read_only=True)
    action_display = serializers.CharField(source="get_action_display", read_only=True)

    class Meta:
        model = TaskLog
        fields = "__all__"
