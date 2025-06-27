from django.conf import settings
import os
import sys
import pytest
import uuid
from django.db.models import signals

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

if not settings.configured:
    import django
    django.setup()

from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from django_elasticsearch_dsl.registries import registry
from django_elasticsearch_dsl.signals import BaseSignalProcessor

from apps.users.models import User
from apps.tasks.models import Task, Label, TaskStatus, TaskType
from apps.workspaces.models import Workspace

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass

@pytest.fixture(scope="session", autouse=True)
def disable_es_signals():
    registry.signal_processor = BaseSignalProcessor(registry)

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

@pytest.fixture
def create_workspace():
    def make_workspace(created_by, name="Test Workspace"):
        return Workspace.objects.create(name=name, created_by=created_by)
    return make_workspace

@pytest.fixture
def create_task_type():
    def make_task_type(name="Bug", icon="bug", color="#ff0000"):
        return TaskType.objects.create(name=name, icon=icon, color=color)
    return make_task_type

@pytest.fixture
def create_task_status(create_workspace):
    def make_task_status(workspace, name="To Do", is_default=False):
        return TaskStatus.objects.create(
            name=name,
            workspace=workspace,
            order=0,
            is_default=is_default,
            is_closed=False
        )
    return make_task_status

@pytest.fixture
def create_label(create_workspace):
    def make_label(workspace, name="Urgent", color="#ff0000"):
        return Label.objects.create(name=name, workspace=workspace, color=color)
    return make_label

@pytest.fixture
def create_task(create_workspace, create_user):
    def make_task(workspace=None, creator=None, title="Test Task", **kwargs):
        if not workspace:
            workspace = create_workspace(creator or create_user())
        if not creator:
            creator = create_user()
        return Task.objects.create(
            title=title,
            workspace=workspace,
            creator=creator,
            **kwargs
        )
    return make_task

@pytest.fixture(autouse=True)
def disable_signals():
    signals.post_save.receivers = []
    signals.pre_save.receivers = []
    signals.post_delete.receivers = []
