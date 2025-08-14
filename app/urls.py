from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.index, name="login"),
    path("control-asistencia/", views.control_asistencia, name="control_asistencia"),
    path("attendance-action/", views.control_asistencia, name="attendance_action"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path(
        "api/attendance-history/",
        views.get_attendance_history_api,
        name="attendance_history_api",
    ),
    path(
        "api/current-status/",
        views.get_current_status_api,
        name="current_status_api",
    ),
]
