from elasticsearch.dsl import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from .models import User
from .search_document import UserDocument
from .serializers.manage import UserSerializer, UserPermissionUpdateSerializer

from .serializers.search import UserListSerializer
from .serializers.user import LogSerializer, RegSerializer
from .utils.auth import generate_token_response
from ..workspaces.models import UserWorkspaceRole


@api_view(["POST"])
def log_in_handler(request: Request) -> Response:
    serializer = LogSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)

    user = serializer.validated_data["user"]
    return Response(generate_token_response(user), status=status.HTTP_200_OK)


@api_view(["POST"])
def sign_up_handler(request: Request) -> Response:
    serializer = RegSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = serializer.save()
    return Response(generate_token_response(user), status=status.HTTP_201_CREATED)


@api_view(["POST"])
def log_out_handler(request: Request) -> Response:
    if not request.user.is_authenticated:
        return Response(
            {"error": {"code": 403, "message": "Пользователь не авторизован"}}, status=status.HTTP_403_FORBIDDEN
        )

    request.user.auth_token.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def user_search_view(request):
    search = request.query_params.get("search", "")
    is_active = request.query_params.get("is_active")
    is_staff = request.query_params.get("is_staff")
    is_superuser = request.query_params.get("is_superuser")
    permission_code = request.query_params.get("permission")

    q = Q("match_all")

    if search:
        q &= Q("multi_match", query=search, fields=["email^2", "fio"], fuzziness="auto")

    if is_active is not None:
        q &= Q("term", is_active=is_active.lower() == "true")

    if is_staff is not None:
        q &= Q("term", is_staff=is_staff.lower() == "true")

    if is_superuser is not None:
        q &= Q("term", is_superuser=is_superuser.lower() == "true")

    if permission_code:
        q &= Q("nested", path="permissions", query=Q("term", permissions__code=permission_code))

    search_query = UserDocument.search().query(q)

    paginator = PageNumberPagination()
    paginator.page_size = 10
    page = paginator.paginate_queryset(search_query.execute().hits, request)

    serializer = UserListSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def update_user_permissions(request, pk):
    user = get_object_or_404(User, pk=pk)
    serializer = UserPermissionUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    if "is_staff" in data:
        user.is_staff = data["is_staff"]
    if "is_superuser" in data:
        user.is_superuser = data["is_superuser"]
    user.save()

    if "role_ids" in data:
        workspace_id = data.get("workspace_id")
        if not workspace_id:
            return Response(
                {"detail": "workspace_id обязателен при назначении ролей."}, status=status.HTTP_400_BAD_REQUEST
            )

        user.workspace_roles.filter(workspace_id=workspace_id).delete()

        for role_id in data["role_ids"]:
            UserWorkspaceRole.objects.create(user=user, workspace_id=workspace_id, role_id=role_id)

    return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
