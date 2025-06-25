from rest_framework import serializers

from apps.users.serializers.manage import UserSerializer

from apps.workspaces.models import Workspace, UserWorkspaceRole

from apps.users.models import Role


class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class UserWorkspaceRoleSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    role_details = RoleSerializer(source='role', read_only=True)
    workspace_details = WorkspaceSerializer(source='workspace', read_only=True)

    class Meta:
        model = UserWorkspaceRole
        fields = '__all__'
        extra_kwargs = {
            'user': {'write_only': True},
            'role': {'write_only': True},
            'workspace': {'write_only': True},
        }

    def validate(self, data):
        if self.instance:
            if UserWorkspaceRole.objects.filter(
                user=data.get('user', self.instance.user),
                workspace=data.get('workspace', self.instance.workspace)
            ).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("This user already has a role in this workspace.")
        else:
            if UserWorkspaceRole.objects.filter(
                user=data['user'],
                workspace=data['workspace']
            ).exists():
                raise serializers.ValidationError("This user already has a role in this workspace.")
        return data