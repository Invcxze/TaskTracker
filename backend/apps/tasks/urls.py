from django.urls import path, include
from rest_framework import routers
from .views import (
    TaskTypeViewSet, TaskStatusViewSet, LabelViewSet,
    TaskViewSet, TaskDependencyViewSet, TaskCommentViewSet,
    TaskAttachmentViewSet, TaskChecklistItemViewSet, TaskLogViewSet
)

router = routers.DefaultRouter()
router.register(r'task-types', TaskTypeViewSet)
router.register(r'task-statuses', TaskStatusViewSet)
router.register(r'labels', LabelViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'task-dependencies', TaskDependencyViewSet)

task_router = routers.NestedSimpleRouter(router, r'tasks', lookup='task')
task_router.register(r'comments', TaskCommentViewSet, basename='task-comments')
task_router.register(r'attachments', TaskAttachmentViewSet, basename='task-attachments')
task_router.register(r'checklist', TaskChecklistItemViewSet, basename='task-checklist')
task_router.register(r'logs', TaskLogViewSet, basename='task-logs')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(task_router.urls)),
]