from django.urls import path

from .views import sign_up_handler, log_in_handler, log_out_handler

urlpatterns = [
    path("sign-up/", sign_up_handler, name="sign_up"),
    path("log-in/", log_in_handler, name="log_in"),
    path("log-out/", log_out_handler, name="log_out"),
]
