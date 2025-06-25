from django.urls import path

from .views import sign_up_handler, log_in_handler, log_out_handler, user_search_view, update_user_permissions


urlpatterns = [
    path("sign-up/", sign_up_handler, name="sign_up"),
    path("log-in/", log_in_handler, name="log_in"),
    path("log-out/", log_out_handler, name="log_out"),
    path("users/search/", user_search_view, name="user_search"),
    path("users/<int:pk>/update-permissions/", update_user_permissions, name="update_user_permissions"),
]
