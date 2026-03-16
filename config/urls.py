from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/users/", include("apps.users.urls")),
    path("api/access/", include("apps.access.urls")),
    path("api/mock/", include("apps.mock_resources.urls")),
]
