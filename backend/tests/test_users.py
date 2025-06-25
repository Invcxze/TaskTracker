import pytest
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from apps.users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_data():
    return {"email": "test@example.com", "fio": "Test User", "password": "TestPass123"}


@pytest.fixture
def create_user(user_data):
    def make_user(**overrides):
        user = User.objects.create_user(**user_data, **overrides)
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
    create_user()
    payload = {"email": user_data["email"], "password": user_data["password"]}
    response = api_client.post("/api/auth/log-in/", data=payload, format="json")
    assert response.status_code == 200
    assert "data" in response.data
    assert "user_token" in response.data["data"]


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
