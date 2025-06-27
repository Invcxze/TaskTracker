from rest_framework.decorators import api_view, permission_classes
from django.core.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from .models import User
from .serializers.manage import UserSerializer, UserPermissionUpdateSerializer
from .serializers.search import UserListSerializer
from .serializers.user import LogSerializer, RegSerializer
from .services.users import update_user_permissions
from .selectors.users import search_users
from apps.users.services.auth import generate_token_response


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
        return Response({"error": {"code": 403, "message": "Пользователь не авторизован"}}, status=403)

    request.user.auth_token.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def user_search_view(request):
    search_query = search_users(
        search=request.query_params.get("search"),
        is_active=request.query_params.get("is_active"),
        is_staff=request.query_params.get("is_staff"),
        is_superuser=request.query_params.get("is_superuser"),
        permission_code=request.query_params.get("permission"),
    )

    paginator = PageNumberPagination()
    paginator.page_size = 10
    page = paginator.paginate_queryset(search_query.execute().hits, request)

    serializer = UserListSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def update_user_permissions_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    serializer = UserPermissionUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        updated_user = update_user_permissions(user, serializer.validated_data)
    except ValidationError as e:
        error_message = e.messages[0] if e.messages else str(e)
        return Response({"detail": error_message}, status=status.HTTP_400_BAD_REQUEST)
    return Response(UserSerializer(updated_user).data, status=status.HTTP_200_OK)
