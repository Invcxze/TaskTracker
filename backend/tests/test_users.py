from unittest.mock import MagicMock, patch

import pytest
from django.db.models import signals
from rest_framework import status

from apps.users.models import Role, User
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


@pytest.mark.django_db
def test_user_search_basic(auth_client):
    client, admin = auth_client

    user1 = User.objects.create(email="user1@example.com", fio="John Doe", is_active=True)
    user2 = User.objects.create(email="user2@example.com", fio="Jane Smith", is_active=False)

    mock_search = MagicMock()
    mock_execute = MagicMock()
    mock_execute.hits = [user1, user2]
    mock_search.execute.return_value = mock_execute

    with patch("apps.users.views.search_users", return_value=mock_search) as mock_search_func:
        response = client.get("/api/auth/users/search/", {"search": "john"})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2
    mock_search_func.assert_called_once_with(
        search="john", is_active=None, is_staff=None, is_superuser=None, permission_code=None
    )


@pytest.mark.django_db
def test_user_search_with_filters(auth_client):
    client, admin = auth_client

    mock_search = MagicMock()
    mock_execute = MagicMock()
    mock_execute.hits = [admin]
    mock_search.execute.return_value = mock_execute

    with patch("apps.users.views.search_users", return_value=mock_search):
        response = client.get(
            "/api/auth/users/search/",
            {"is_active": "true", "is_staff": "true", "is_superuser": "true", "permission": "manage_users"},
        )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1


@pytest.mark.django_db
def test_user_search_pagination(auth_client):
    client, admin = auth_client

    for i in range(15):
        User.objects.create(email=f"user{i}@example.com", fio=f"User {i}")

    mock_search = MagicMock()
    mock_execute = MagicMock()
    mock_execute.hits = User.objects.all()
    mock_search.execute.return_value = mock_execute

    with patch("apps.users.views.search_users", return_value=mock_search):
        response1 = client.get("/api/auth/users/search/", {"page": 1})
        assert response1.status_code == status.HTTP_200_OK
        assert len(response1.data["results"]) == 10
        assert response1.data["count"] == 16

        response2 = client.get("/api/auth/users/search/", {"page": 2})
        assert response2.status_code == status.HTTP_200_OK
        assert len(response2.data["results"]) == 6


@pytest.mark.django_db
def test_user_search_permission_filter(auth_client):
    client, admin = auth_client

    mock_search = MagicMock()
    mock_execute = MagicMock()
    mock_execute.hits = [admin]
    mock_search.execute.return_value = mock_execute

    with patch("apps.users.views.search_users", return_value=mock_search):
        response = client.get("/api/auth/users/search/", {"permission": "admin_panel"})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1


@pytest.mark.django_db
def test_user_search_unauthorized(api_client):
    user = User.objects.create(email="regular@example.com", is_active=True)
    api_client.force_authenticate(user)

    response = api_client.get("/api/auth/users/search/")
    assert response.status_code == status.HTTP_403_FORBIDDEN
