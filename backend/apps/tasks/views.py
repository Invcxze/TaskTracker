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
from ..workspaces.models import Workspace, UserWorkspaceRole


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
        user_workspaces = Workspace.objects.filter(user_roles__user=self.request.user)
        return TaskStatus.objects.filter(workspace__in=user_workspaces)

    def perform_create(self, serializer):
        workspace = serializer.validated_data.get("workspace")
        if not workspace or not UserWorkspaceRole.objects.filter(workspace=workspace, user=self.request.user).exists():
            raise PermissionDenied("You do not have access to this workspace.")
        serializer.save()


class LabelViewSet(viewsets.ModelViewSet):
    serializer_class = LabelSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["workspace"]

    def get_queryset(self):
        user_workspaces = Workspace.objects.filter(user_roles__user=self.request.user)
        return Label.objects.filter(workspace__in=user_workspaces)

    def perform_create(self, serializer):
        workspace = serializer.validated_data.get("workspace")
        if not workspace or not Workspace.objects.filter(id=workspace.id, user_roles__user=self.request.user).exists():
            raise PermissionDenied("You do not have access to this workspace.")
        serializer.save()


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["workspace", "status", "task_type", "assignee", "creator", "priority"]

    def get_queryset(self):
        return Task.objects.filter(workspace__user_roles__user=self.request.user).distinct()

    @action(detail=True, methods=["post"])
    def add_watcher(self, request, pk=None):
        task = self.get_object()
        user = request.user
        task.watchers.add(user)
        return Response({"status": "watcher added"})

    @action(detail=True, methods=["post"])
    def remove_watcher(self, request, pk=None):
        task = self.get_object()
        user = request.user
        task.watchers.remove(user)
        return Response({"status": "watcher removed"})


class TaskDependencyViewSet(viewsets.ModelViewSet):
    serializer_class = TaskDependencySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_tasks = Task.objects.filter(workspace__user_roles__user=self.request.user)
        return TaskDependency.objects.filter(from_task__in=user_tasks, to_task__in=user_tasks)


class TaskCommentViewSet(viewsets.ModelViewSet):
    serializer_class = TaskCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = TaskComment.objects.filter(task__workspace__user_roles__user=self.request.user)
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
        qs = TaskAttachment.objects.filter(task__workspace__user_roles__user=self.request.user)
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
        qs = TaskChecklistItem.objects.filter(task__workspace__user_roles__user=self.request.user)
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
        qs = TaskLog.objects.filter(task__workspace__user_roles__user=self.request.user)
        task_id = self.kwargs.get("task_pk")
        if task_id:
            qs = qs.filter(task_id=task_id)
        return qs
