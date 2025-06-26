import pytest
from apps.users.models import User, Role
from apps.workspaces.models import UserWorkspaceRole, Workspace
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
import uuid
from django.db.models import signals

@pytest.fixture
def admin_user(create_user):
    return create_user(is_staff=True, is_superuser=True)

@pytest.fixture
def auth_client(api_client):
    admin = User.objects.create_superuser(
        fio="Admin User",
        email=f"admin_{uuid.uuid4().hex[:6]}@example.com",
        password="adminpass",
        is_staff=True,
        is_superuser=True
    )
    token = Token.objects.create(user=admin)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.key}")
    return api_client, admin

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_data():
    unique_id = uuid.uuid4().hex[:6]
    return {
        "email": f"test_{unique_id}@example.com",
        "fio": "Test User",
        "password": "TestPass123"
    }


@pytest.fixture
def create_user():
    def make_user(email=None, fio='Test User', password='TestPass123', **kwargs):
        if email is None:
            email = f"test_{uuid.uuid4().hex[:6]}@example.com"
        user = User.objects.create_user(fio=fio, email=email, password=password, **kwargs)
        Token.objects.create(user=user)
        return user
    return make_user

@pytest.mark.django_db
def test_sign_up_success(api_client, user_data):
    response = api_client.post("/api/auth/sign-up/", data=user_data, format="json")
    assert response.status_code == 201
    assert "data" in response.data
    assert "user_token" in response.data["data"]


@pytest.mark.django_db
def test_log_in_success(api_client, create_user, user_data):
    user = create_user(email=user_data["email"])
    payload = {"email": user_data["email"], "password": user_data["password"]}
    response = api_client.post("/api/auth/log-in/", data=payload, format="json")
    assert response.status_code == 200


@pytest.mark.django_db
def test_log_in_invalid_password(api_client, create_user, user_data):
    create_user()
    payload = {"email": user_data["email"], "password": "wrongpassword"}
    response = api_client.post("/api/auth/log-in/", data=payload, format="json")
    assert response.status_code == 400
    assert "non_field_errors" in response.data


@pytest.mark.django_db
def test_log_out_authorized(api_client, create_user, user_data):
    user = create_user()
    token = user.auth_token.key
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    response = api_client.post("/api/auth/log-out/")
    assert response.status_code == 204


@pytest.mark.django_db
def test_log_out_unauthorized(api_client):
    response = api_client.post("/api/auth/log-out/")
    assert response.status_code == 403
    assert response.data["error"]["code"] == 403


@pytest.mark.django_db
def test_update_permissions_is_staff_and_superuser(auth_client, create_user):
    client, admin = auth_client
    user = create_user()

    payload = {"is_staff": True, "is_superuser": True}

    url = f"/api/auth/users/{user.pk}/update-permissions/"
    response = client.patch(url, data=payload, format="json")

    assert response.status_code == 200
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

        assert response.status_code == 200
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

    payload = {
        "role_ids": [role.id]
    }

    url = f"/api/auth/users/{user.pk}/update-permissions/"
    response = client.patch(url, data=payload, format="json")

    assert response.status_code == 400
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

    assert response.status_code == 403
