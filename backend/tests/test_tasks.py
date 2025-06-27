import pytest
from django.urls import reverse
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.tasks.models import TaskType, TaskStatus, Label, Task, TaskComment, TaskAttachment, TaskChecklistItem, TaskLog
from apps.users.models import Role
from apps.workspaces.models import UserWorkspaceRole


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
