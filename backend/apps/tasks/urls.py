from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter
from .views import (
    TaskTypeViewSet,
    TaskStatusViewSet,
    LabelViewSet,
    TaskViewSet,
    TaskDependencyViewSet,
    TaskCommentViewSet,
    TaskAttachmentViewSet,
    TaskChecklistItemViewSet,
    TaskLogViewSet,
)

router = DefaultRouter()
router.register(r"task-types", TaskTypeViewSet, basename="task-types")
router.register(r"task-statuses", TaskStatusViewSet, basename="task-statuses")
router.register(r"labels", LabelViewSet, basename="labels")
router.register(r"tasks", TaskViewSet, basename="tasks")
router.register(r"task-dependencies", TaskDependencyViewSet, basename="task-dependencies")

task_router = NestedSimpleRouter(router, r"tasks", lookup="task")
task_router.register(r"comments", TaskCommentViewSet, basename="task-comments")
task_router.register(r"attachments", TaskAttachmentViewSet, basename="task-attachments")
task_router.register(r"checklist", TaskChecklistItemViewSet, basename="task-checklist")
task_router.register(r"logs", TaskLogViewSet, basename="task-logs")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(task_router.urls)),
]

urlpatterns = [
    path("", include(router.urls)),
    path("", include(task_router.urls)),
]
