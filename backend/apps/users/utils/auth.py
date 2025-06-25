from rest_framework.authtoken.models import Token

from backend.apps.users.models import User


def generate_token_response(user: User) -> dict[str, dict[str, str]]:
    token, _ = Token.objects.get_or_create(user=user)
    return {"data": {"user_token": token.key}}
