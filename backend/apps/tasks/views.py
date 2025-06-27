from rest_framework import viewsets, permissions
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
from .services.label import LabelService
from .services.task_status import TaskStatusService


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
        TaskStatusService.create(serializer.validated_data, self.request.user)


class LabelViewSet(viewsets.ModelViewSet):
    serializer_class = LabelSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["workspace"]

    def get_queryset(self):
        return filter_by_user_workspaces(Label, self.request.user)

    def perform_create(self, serializer):
        LabelService.create(serializer.validated_data, self.request.user)

    def perform_update(self, serializer):
        LabelService.update(self.get_object(), serializer.validated_data, self.request.user)


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

    @action(detail=False, methods=["get"])
    def search(self, request):
        base_queryset = self.get_queryset()

        search_query = request.GET.get("q", "")
        filters = {
            "workspace": request.GET.get("workspace"),
            "status": request.GET.get("status"),
            "priority": request.GET.getlist("priority"),
            "assignee": request.GET.get("assignee"),
            "creator": request.GET.get("creator"),
            "is_closed": request.GET.get("is_closed"),
            "labels": request.GET.getlist("labels"),
            "due_date_before": request.GET.get("due_date_before"),
            "due_date_after": request.GET.get("due_date_after"),
        }

        result_queryset = task_search(base_queryset, search_query, filters)

        page = self.paginate_queryset(result_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(result_queryset, many=True)
        return Response(serializer.data)


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
