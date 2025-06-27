import pytest
from django.urls import reverse
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.tasks.models import TaskType, TaskStatus, Label, Task, TaskComment, TaskAttachment, TaskChecklistItem, TaskLog
from apps.users.models import Role
from apps.workspaces.models import UserWorkspaceRole
from unittest.mock import patch, MagicMock
from django.utils import timezone
from datetime import timedelta
from apps.workspaces.models import Workspace
from apps.users.models import User


@pytest.mark.django_db
def test_task_type_list(auth_client, create_task_type):
    client, admin = auth_client
    create_task_type()
    create_task_type(name="Feature")

    url = reverse("task-types-list")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2


@pytest.mark.django_db
def test_task_type_create(auth_client):
    client, admin = auth_client
    url = reverse("task-types-list")
    data = {"name": "Bug", "icon": "bug", "color": "#ff0000"}
    response = client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert TaskType.objects.count() == 1


@pytest.mark.django_db
def test_task_status_list(auth_client, create_workspace, create_task_status):
    client, admin = auth_client
    workspace = create_workspace(admin)
    role = Role.objects.create(name="Member")
    UserWorkspaceRole.objects.create(user=admin, workspace=workspace, role=role)

    create_task_status(workspace)
    create_task_status(workspace, name="Done")

    url = reverse("task-statuses-list")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2


@pytest.mark.django_db
def test_task_status_create(auth_client, create_workspace):
    client, admin = auth_client
    workspace = create_workspace(admin)
    role = Role.objects.create(name="Member")
    UserWorkspaceRole.objects.create(user=admin, workspace=workspace, role=role)

    url = reverse("task-statuses-list")
    data = {"name": "In Progress", "workspace": workspace.id, "order": 1, "is_default": False, "is_closed": False}
    response = client.post(url, data)
    print(response.text, "BABA")
    print(UserWorkspaceRole.objects.filter(user=admin, workspace=workspace).exists())
    print(client)
    assert response.status_code == status.HTTP_201_CREATED
    assert TaskStatus.objects.count() == 1


@pytest.mark.django_db
def test_label_create(auth_client, create_workspace):
    client, admin = auth_client
    workspace = create_workspace(admin)
    role = Role.objects.create(name="Member")
    UserWorkspaceRole.objects.create(user=admin, workspace=workspace, role=role)

    url = reverse("labels-list")
    data = {"name": "Critical", "workspace": workspace.id, "color": "#ff0000"}
    response = client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert Label.objects.count() == 1


@pytest.mark.django_db
def test_task_create(auth_client, create_workspace, create_task_status, create_task_type):
    client, admin = auth_client
    workspace = create_workspace(admin)
    status_obj = create_task_status(workspace)
    task_type = create_task_type()
    role = Role.objects.create(name="Member")
    UserWorkspaceRole.objects.create(user=admin, workspace=workspace, role=role)

    url = reverse("tasks-list")
    data = {
        "title": "New Task",
        "description": "Task description",
        "workspace": workspace.id,
        "status": status_obj.id,
        "task_type": task_type.id,
        "priority": "high",
    }
    response = client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert Task.objects.count() == 1


@pytest.mark.django_db
def test_task_add_watcher(auth_client, create_task):
    client, admin = auth_client
    task = create_task()
    workspace = task.workspace
    role = Role.objects.create(name="Member")
    UserWorkspaceRole.objects.create(user=admin, workspace=workspace, role=role)

    url = reverse("tasks-add-watcher", kwargs={"pk": task.id})
    response = client.post(url)
    assert response.status_code == status.HTTP_200_OK
    assert task.watchers.count() == 1
    assert admin in task.watchers.all()


@pytest.mark.django_db
def test_task_comment_create(auth_client, create_task):
    client, admin = auth_client
    task = create_task()
    workspace = task.workspace
    role = Role.objects.create(name="Member")
    UserWorkspaceRole.objects.create(user=admin, workspace=workspace, role=role)

    url = reverse("task-comments-list", kwargs={"task_pk": task.id})

    data = {"task": task.id, "content": "Test comment"}
    response = client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert TaskComment.objects.count() == 1
    assert TaskComment.objects.first().author == admin


@pytest.mark.django_db
def test_task_attachment_create(auth_client, create_task):
    client, admin = auth_client
    task = create_task()
    workspace = task.workspace
    role = Role.objects.create(name="Member")
    UserWorkspaceRole.objects.create(user=admin, workspace=workspace, role=role)

    url = reverse("task-attachments-list", kwargs={"task_pk": task.id})

    file = SimpleUploadedFile("test.txt", b"file_content", content_type="text/plain")
    data = {"task": task.id, "file": file, "file_name": file.name, "file_size": file.size}
    response = client.post(url, data, format="multipart")
    print(response.status_code)
    print(response.data)
    assert response.status_code == status.HTTP_201_CREATED
    assert TaskAttachment.objects.count() == 1
    assert TaskAttachment.objects.first().uploaded_by == admin


@pytest.mark.django_db
def test_checklist_item_create(auth_client, create_task):
    client, admin = auth_client
    task = create_task()
    workspace = task.workspace
    role = Role.objects.create(name="Member")
    UserWorkspaceRole.objects.create(user=admin, workspace=workspace, role=role)

    url = reverse("task-checklist-list", kwargs={"task_pk": task.id})
    data = {"task": task.id, "text": "Checklist item 1", "is_completed": False}
    response = client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert TaskChecklistItem.objects.count() == 1


@pytest.mark.django_db
def test_task_log_list(auth_client, create_task):
    client, admin = auth_client
    task = create_task()
    TaskLog.objects.create(task=task, user=admin, action="create", changes={"title": "Test Task"})
    workspace = task.workspace
    role = Role.objects.create(name="Member")
    UserWorkspaceRole.objects.create(user=admin, workspace=workspace, role=role)

    url = reverse("task-logs-list", kwargs={"task_pk": task.id})
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1


@pytest.mark.django_db
def test_no_access_to_other_workspace(auth_client, create_workspace, create_user):
    client, admin = auth_client
    other_user = create_user()
    workspace = create_workspace(other_user)

    url = reverse("task-statuses-list")
    data = {"name": "Blocked", "workspace": workspace.id, "order": 1, "is_default": False, "is_closed": False}
    response = client.post(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert TaskStatus.objects.count() == 0


@pytest.mark.django_db
def test_task_search_basic(auth_client):
    client, admin = auth_client

    workspace = Workspace.objects.create(name="Test Workspace", created_by=admin)
    role = Role.objects.create(name="Member")
    UserWorkspaceRole.objects.create(user=admin, workspace=workspace, role=role)

    task1 = Task.objects.create(
        title="Important task", description="This is a very important task", workspace=workspace, creator=admin
    )
    task2 = Task.objects.create(
        title="Regular task", description="Just a regular task", workspace=workspace, creator=admin
    )

    mock_search = MagicMock()
    mock_execute = MagicMock()
    mock_execute.hits = [MagicMock(id=task1.id)]
    mock_search.execute.return_value = mock_execute

    with patch("apps.tasks.views.task_search", return_value=Task.objects.filter(id=task1.id)):
        url = reverse("tasks-search")
        response = client.get(url, {"q": "important"})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1  # Исправлено: response.data вместо response.data["results"]
    assert response.data[0]["title"] == "Important task"  # Исправлено: обращение по индексу


@pytest.mark.django_db
def test_task_search_with_filters(auth_client):
    client, admin = auth_client

    workspace1 = Workspace.objects.create(name="Workspace 1", created_by=admin)
    workspace2 = Workspace.objects.create(name="Workspace 2", created_by=admin)

    role = Role.objects.create(name="Member")
    UserWorkspaceRole.objects.create(user=admin, workspace=workspace1, role=role)
    UserWorkspaceRole.objects.create(user=admin, workspace=workspace2, role=role)

    status_open = TaskStatus.objects.create(name="Open", workspace=workspace1)
    status_closed = TaskStatus.objects.create(name="Closed", workspace=workspace1)

    label_urgent = Label.objects.create(name="Urgent", workspace=workspace1)

    user1 = User.objects.create(email="user1@example.com")
    user2 = User.objects.create(email="user2@example.com")

    task1 = Task.objects.create(
        title="Task 1",
        workspace=workspace1,
        status=status_open,
        priority="high",
        assignee=user1,
        creator=admin,
        due_date=timezone.now() + timedelta(days=1),
    )
    task1.labels.add(label_urgent)

    task2 = Task.objects.create(
        title="Task 2",
        workspace=workspace2,
        status=status_closed,
        priority="low",
        assignee=user2,
        creator=admin,
        due_date=timezone.now() - timedelta(days=1),
    )

    with patch("apps.tasks.views.task_search", return_value=Task.objects.filter(id=task1.id)):
        url = reverse("tasks-search")
        response = client.get(
            url,
            {
                "workspace": workspace1.id,
                "status": status_open.id,
                "priority": "high",
                "assignee": user1.id,
                "creator": admin.id,
                "is_closed": "false",
                "labels": [label_urgent.id],
                "due_date_after": (timezone.now() - timedelta(days=1)).isoformat(),
                "due_date_before": (timezone.now() + timedelta(days=2)).isoformat(),
            },
        )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["title"] == "Task 1"


@pytest.mark.django_db
def test_task_search_pagination(auth_client):
    client, admin = auth_client

    workspace = Workspace.objects.create(name="Pagination Workspace", created_by=admin)
    role = Role.objects.create(name="Member")
    UserWorkspaceRole.objects.create(user=admin, workspace=workspace, role=role)

    tasks = []
    for i in range(15):
        task = Task.objects.create(title=f"Task {i}", workspace=workspace, creator=admin)
        tasks.append(task)

    mock_search = MagicMock()
    mock_execute = MagicMock()
    mock_execute.hits = [MagicMock(id=task.id) for task in tasks]
    mock_search.execute.return_value = mock_execute

    with patch("apps.tasks.views.task_search", return_value=Task.objects.filter(workspace=workspace)):
        url = reverse("tasks-search")

        response1 = client.get(url, {"page": 1})
        assert response1.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_task_search_unauthorized(api_client):
    user = User.objects.create(email="regular@example.com")
    api_client.force_authenticate(user)

    with patch("apps.tasks.views.task_search", return_value=Task.objects.none()):
        url = reverse("tasks-search")
        response = api_client.get(url, {"q": "test"})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0


@pytest.mark.django_db
def test_task_search_priority_filter(auth_client):
    client, admin = auth_client

    workspace = Workspace.objects.create(name="Priority Workspace", created_by=admin)
    role = Role.objects.create(name="Member")
    UserWorkspaceRole.objects.create(user=admin, workspace=workspace, role=role)

    task_high = Task.objects.create(title="High Priority", priority="high", workspace=workspace, creator=admin)
    task_medium = Task.objects.create(title="Medium Priority", priority="medium", workspace=workspace, creator=admin)
    task_low = Task.objects.create(title="Low Priority", priority="low", workspace=workspace, creator=admin)

    with patch("apps.tasks.views.task_search", return_value=Task.objects.filter(priority__in=["high", "medium"])):
        url = reverse("tasks-search")
        response = client.get(url, {"priority": ["high", "medium"]})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    priorities = {result["priority"] for result in response.data}
    assert priorities == {"high", "medium"}


@pytest.mark.django_db
def test_task_search_due_date_filter(auth_client):
    client, admin = auth_client

    workspace = Workspace.objects.create(name="Due Date Workspace", created_by=admin)
    role = Role.objects.create(name="Member")
    UserWorkspaceRole.objects.create(user=admin, workspace=workspace, role=role)

    today = timezone.now().date()
    task_past = Task.objects.create(
        title="Past Due", due_date=today - timedelta(days=5), workspace=workspace, creator=admin
    )
    task_future = Task.objects.create(
        title="Future Due", due_date=today + timedelta(days=5), workspace=workspace, creator=admin
    )
    task_range = Task.objects.create(
        title="In Range", due_date=today + timedelta(days=2), workspace=workspace, creator=admin
    )

    with patch("apps.tasks.views.task_search", return_value=Task.objects.filter(id=task_range.id)):
        url = reverse("tasks-search")
        response = client.get(
            url,
            {
                "due_date_after": (today + timedelta(days=1)).isoformat(),
                "due_date_before": (today + timedelta(days=3)).isoformat(),
            },
        )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["title"] == "In Range"
