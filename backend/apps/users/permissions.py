from rest_framework import status
from rest_framework.response import Response


def permission_required(perm_code: str):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return Response(
                    {"error": {"code": 403, "message": "Пользователь не авторизован"}}, status=status.HTTP_403_FORBIDDEN
                )
            if not user.has_perm_in_workspace(perm_code, workspace=None):
                return Response(
                    {"error": {"code": 403, "message": "Нет прав для доступа"}}, status=status.HTTP_403_FORBIDDEN
                )
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
