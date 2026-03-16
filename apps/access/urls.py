from django.urls import path

from .views import (
    ActionListView,
    ResourceListView,
    RoleListView,
    RolePermissionDeleteView,
    RolePermissionListCreateView,
    UserRoleDeleteView,
    UserRoleListCreateView,
)

urlpatterns = [
    path("roles/", RoleListView.as_view(), name="role-list"),
    path("resources/", ResourceListView.as_view(), name="resource-list"),
    path("actions/", ActionListView.as_view(), name="action-list"),
    path(
        "user-roles/",
        UserRoleListCreateView.as_view(),
        name="user-role-list-create"
    ),
    path(
        "user-roles/<int:user_role_id>/",
        UserRoleDeleteView.as_view(),
        name="user-role-delete",
    ),
    path(
        "role-permissions/",
        RolePermissionListCreateView.as_view(),
        name="role-permission-list-create",
    ),
    path(
        "role-permissions/<int:role_permission_id>/",
        RolePermissionDeleteView.as_view(),
        name="role-permission-delete",
    ),
]
