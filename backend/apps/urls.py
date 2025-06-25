from django.urls import path, include

urlpatterns = [
    path('auth/', include('apps.users.urls')),
    path('workspaces/', include('apps.workspaces.urls')),
]
