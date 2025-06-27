import pytest
from django.urls import reverse
from rest_framework import status
from apps.users.models import Role
from apps.workspaces.models import Workspace, UserWorkspaceRole


@pytest.mark.django_db
def test_workspace_list(auth_client, create_workspace):
    client, user = auth_client
    create_workspace(user, name="Workspace 1")
    create_workspace(user, name="Workspace 2")

    url = reverse("workspace-list")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 2


@pytest.mark.django_db
def test_workspace_create(auth_client):
    client, user = auth_client
    url = reverse("workspace-list")
    data = {"name": "New Workspace", "description": "Test workspace"}
    response = client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert Workspace.objects.filter(name="New Workspace").exists()


@pytest.mark.django_db
def test_workspace_update(auth_client, create_workspace):
    client, user = auth_client
    workspace = create_workspace(user, name="Old Name")

    url = reverse("workspace-detail", kwargs={"pk": workspace.id})
    data = {"name": "Updated Name"}
    response = client.patch(url, data)
    assert response.status_code == status.HTTP_200_OK
    workspace.refresh_from_db()
    assert workspace.name == "Updated Name"


@pytest.mark.django_db
def test_user_workspace_role_list(auth_client, create_workspace):
    client, user = auth_client
    workspace = create_workspace(user)
    role = Role.objects.create(name="Member")
    UserWorkspaceRole.objects.create(user=user, workspace=workspace, role=role)

    url = reverse("workspace-roles-list", kwargs={"workspace_pk": workspace.id})
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 1


@pytest.mark.django_db
def test_user_workspace_role_create(auth_client, create_workspace, create_user):
    client, admin = auth_client
    workspace = create_workspace(admin)
    role = Role.objects.create(name="Member")
    other_user = create_user()

    url = reverse("workspace-roles-list", kwargs={"workspace_pk": workspace.id})
    data = {"user": other_user.id, "role": role.id, "workspace": workspace.id}
    response = client.post(url, data)
    print(response.data)
    assert response.status_code == status.HTTP_201_CREATED
    assert UserWorkspaceRole.objects.filter(user=other_user, workspace=workspace, role=role).exists()


@pytest.mark.django_db
def test_user_workspace_role_delete(auth_client, create_workspace):
    client, user = auth_client
    workspace = create_workspace(user)
    role = Role.objects.create(name="Member")
    uwr = UserWorkspaceRole.objects.create(user=user, workspace=workspace, role=role)

    url = reverse("workspace-roles-detail", kwargs={"workspace_pk": workspace.id, "pk": uwr.id})
    response = client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not UserWorkspaceRole.objects.filter(id=uwr.id).exists()