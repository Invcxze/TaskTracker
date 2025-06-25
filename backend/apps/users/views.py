from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_403_FORBIDDEN

from .serializers.user import LogSerializer, RegSerializer


@api_view(["POST"])
def log_in_handler(request: Request) -> Response:
    serializer = LogSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data["user"]

    token, _ = Token.objects.get_or_create(user=user)
    return Response({"data": {"user_token": token.key}}, status=HTTP_200_OK)


@api_view(["POST"])
def sign_up_handler(request: Request) -> Response:
    serializer = RegSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    token = Token.objects.create(user=user)
    return Response({"data": {"user_token": token.key}}, status=HTTP_201_CREATED)


@api_view(["POST"])
def log_out_handler(request: Request) -> Response:
    if not request.user.is_authenticated:
        return Response({"error": {"code": 403, "message": "Пользователь не авторизован"}}, status=HTTP_403_FORBIDDEN)

    request.user.auth_token.delete()
    return Response(status=HTTP_204_NO_CONTENT)
