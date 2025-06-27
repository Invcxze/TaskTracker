from django.urls import path, include
from rest_framework_nested import routers
from .views import WorkspaceViewSet, UserWorkspaceRoleViewSet

router = routers.DefaultRouter()
router.register(r"workspaces", WorkspaceViewSet)

workspace_router = routers.NestedSimpleRouter(router, r"workspaces", lookup="workspace")
workspace_router.register(r"roles", UserWorkspaceRoleViewSet, basename="workspace-roles")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(workspace_router.urls)),
]
