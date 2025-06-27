from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Workspace, UserWorkspaceRole
from .serializers.workspace import WorkspaceSerializer, UserWorkspaceRoleSerializer


class WorkspaceViewSet(viewsets.ModelViewSet):
    queryset = Workspace.objects.all()
    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class UserWorkspaceRoleViewSet(viewsets.ModelViewSet):
    serializer_class = UserWorkspaceRoleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserWorkspaceRole.objects.filter(workspace_id=self.kwargs.get("workspace_pk"))

    def perform_create(self, serializer):
        workspace = Workspace.objects.get(pk=self.kwargs["workspace_pk"])
        serializer.save(workspace=workspace)
