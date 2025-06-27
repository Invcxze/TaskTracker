import pytest
from django.db.models import signals
from rest_framework import status

from apps.users.models import Role
from apps.workspaces.models import UserWorkspaceRole, Workspace


@pytest.mark.django_db
def test_sign_up_success(api_client, user_data):
    response = api_client.post("/api/auth/sign-up/", data=user_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert "data" in response.data
    assert "user_token" in response.data["data"]


@pytest.mark.django_db
def test_log_in_success(api_client, create_user, user_data):
    create_user(email=user_data["email"])
    payload = {"email": user_data["email"], "password": user_data["password"]}
    response = api_client.post("/api/auth/log-in/", data=payload, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert "data" in response.data
    assert "user_token" in response.data["data"]


@pytest.mark.django_db
def test_log_in_invalid_password(api_client, create_user, user_data):
    create_user()
    payload = {"email": user_data["email"], "password": "wrongpassword"}
    response = api_client.post("/api/auth/log-in/", data=payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "non_field_errors" in response.data


@pytest.mark.django_db
def test_log_out_authorized(api_client, create_user):
    user = create_user()
    token = user.auth_token.key
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    response = api_client.post("/api/auth/log-out/")
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_log_out_unauthorized(api_client):
    response = api_client.post("/api/auth/log-out/")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["error"]["code"] == 403


@pytest.mark.django_db
def test_update_permissions_is_staff_and_superuser(auth_client, create_user):
    client, admin = auth_client
    user = create_user()

    payload = {"is_staff": True, "is_superuser": True}

    url = f"/api/auth/users/{user.pk}/update-permissions/"
    response = client.patch(url, data=payload, format="json")
    print(payload, "dasd")
    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.is_staff is True
    assert user.is_superuser is True


@pytest.mark.django_db
def test_update_permissions_with_roles(auth_client, create_user):
    original_receivers = signals.post_save.receivers
    signals.post_save.receivers = []

    try:
        client, admin = auth_client
        user = create_user()

        workspace = Workspace.objects.create(name="Test Workspace", created_by=admin)
        role1 = Role.objects.create(name="Manager")
        role2 = Role.objects.create(name="Editor")

        payload = {"workspace_id": workspace.id, "role_ids": [role1.id, role2.id]}

        url = f"/api/auth/users/{user.pk}/update-permissions/"
        response = client.patch(url, data=payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        roles_qs = UserWorkspaceRole.objects.filter(user=user, workspace_id=workspace.id)
        assert roles_qs.count() == 2
        assert set(roles_qs.values_list("role_id", flat=True)) == {role1.id, role2.id}
    finally:
        signals.post_save.receivers = original_receivers


@pytest.mark.django_db
def test_update_permissions_missing_workspace_id(auth_client, create_user):
    client, admin = auth_client
    user = create_user()

    role = Role.objects.create(name="Manager")
    payload = {"role_ids": [role.id]}

    url = f"/api/auth/users/{user.pk}/update-permissions/"
    response = client.patch(url, data=payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["detail"] == "workspace_id обязателен при назначении ролей."


@pytest.mark.django_db
def test_update_permissions_denied_for_non_admin(api_client, create_user):
    user = create_user()
    target_user = create_user(email="target@example.com")

    token = user.auth_token.key
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    payload = {"is_staff": True}
    url = f"/api/auth/users/{target_user.pk}/update-permissions/"
    response = api_client.patch(url, data=payload, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN