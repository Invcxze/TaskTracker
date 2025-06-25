from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

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
            {"error": {"code": 403, "message": "Пользователь не авторизован"}},
            status=status.HTTP_403_FORBIDDEN
        )

    request.user.auth_token.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)