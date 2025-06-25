from django.db import models
from elasticsearch.dsl import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from .models import User
from .permissions import permission_required
from .search_document import UserDocument
from .serializers.search import UserListSerializer
from .serializers.user import LogSerializer, RegSerializer
from .utils.auth import generate_token_response


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

    # Пагинация
    paginator = PageNumberPagination()
    paginator.page_size = 10
    page = paginator.paginate_queryset(search_query.execute().hits, request)

    serializer = UserListSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)
