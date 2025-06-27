from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
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
from .selectors.users import (
    filter_by_user_workspaces,
    filter_by_user_workspace_and_related_field,
    user_has_access_to_workspace,
)
from .serializers.tasks import (
    TaskTypeSerializer,
    TaskStatusSerializer,
    LabelSerializer,
    TaskSerializer,
    TaskDependencySerializer,
    TaskCommentSerializer,
    TaskAttachmentSerializer,
    TaskChecklistItemSerializer,
    TaskLogSerializer,
)


class TaskTypeViewSet(viewsets.ModelViewSet):
    queryset = TaskType.objects.all()
    serializer_class = TaskTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


class TaskStatusViewSet(viewsets.ModelViewSet):
    serializer_class = TaskStatusSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["workspace"]

    def get_queryset(self):
        return filter_by_user_workspaces(TaskStatus, self.request.user)

    def perform_create(self, serializer):
        workspace = serializer.validated_data.get("workspace")
        if not user_has_access_to_workspace(self.request.user, workspace):
            raise PermissionDenied("You do not have access to this workspace.")
        serializer.save()


class LabelViewSet(viewsets.ModelViewSet):
    serializer_class = LabelSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["workspace"]

    def get_queryset(self):
        return filter_by_user_workspaces(Label, self.request.user)

    def perform_create(self, serializer):
        workspace = serializer.validated_data.get("workspace")
        if not user_has_access_to_workspace(self.request.user, workspace):
            raise PermissionDenied("You do not have access to this workspace.")
        serializer.save()


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["workspace", "status", "task_type", "assignee", "creator", "priority"]

    def get_queryset(self):
        return filter_by_user_workspaces(Task, self.request.user)

    @action(detail=True, methods=["post"])
    def add_watcher(self, request, pk=None):
        task = self.get_object()
        task.watchers.add(request.user)
        return Response({"status": "watcher added"})

    @action(detail=True, methods=["post"])
    def remove_watcher(self, request, pk=None):
        task = self.get_object()
        task.watchers.remove(request.user)
        return Response({"status": "watcher removed"})


class TaskDependencyViewSet(viewsets.ModelViewSet):
    serializer_class = TaskDependencySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_tasks = filter_by_user_workspaces(Task, self.request.user)
        return TaskDependency.objects.filter(from_task__in=user_tasks, to_task__in=user_tasks)


class TaskCommentViewSet(viewsets.ModelViewSet):
    serializer_class = TaskCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = filter_by_user_workspace_and_related_field(TaskComment, self.request.user, "task__workspace")
        task_id = self.kwargs.get("task_pk")
        if task_id:
            qs = qs.filter(task_id=task_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TaskAttachmentViewSet(viewsets.ModelViewSet):
    serializer_class = TaskAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = filter_by_user_workspace_and_related_field(TaskAttachment, self.request.user, "task__workspace")
        task_id = self.kwargs.get("task_pk")
        if task_id:
            qs = qs.filter(task_id=task_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class TaskChecklistItemViewSet(viewsets.ModelViewSet):
    serializer_class = TaskChecklistItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = filter_by_user_workspace_and_related_field(TaskChecklistItem, self.request.user, "task__workspace")
        task_id = self.kwargs.get("task_pk")
        if task_id:
            qs = qs.filter(task_id=task_id)
        return qs


class TaskLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TaskLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["task", "user", "action"]

    def get_queryset(self):
        qs = filter_by_user_workspace_and_related_field(TaskLog, self.request.user, "task__workspace")
        task_id = self.kwargs.get("task_pk")
        if task_id:
            qs = qs.filter(task_id=task_id)
        return qs
