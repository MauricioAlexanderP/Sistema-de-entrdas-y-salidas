from django.shortcuts import render, redirect
from django.http import JsonResponse
from app.services.login_service import LoginService
from app.services.attendance_service import AttendanceService


# Create your views here.
def index(request):
    # Si el usuario ya está autenticado, redirigir a control de asistencia
    if LoginService.is_user_authenticated(request):
        return redirect("control_asistencia")

    # Si es una petición POST (formulario de login)
    if request.method == "POST":
        return LoginService.process_login(request)

    # Si es GET, mostrar la página de login
    return render(request, "index.html")


def control_asistencia(request):
    # Verificar que el usuario esté autenticado
    if not LoginService.is_user_authenticated(request):
        return render(request, "index.html")

    # Si es una petición POST para registrar asistencia
    if request.method == "POST":
        return AttendanceService.process_attendance_action(request)

    # Obtener información del usuario actual y su estado de asistencia
    current_user = LoginService.get_current_user(request)
    attendance_status = AttendanceService.get_current_status(current_user["id"])
    # Obtener TODOS los registros del usuario (sin límite de días)
    attendance_history = AttendanceService.get_attendance_history(current_user["id"])

    # Importar json para pasar datos al template
    import json

    context = {
        "user": current_user,
        "attendance_status": attendance_status,
        "attendance_status_json": json.dumps(attendance_status),
        "attendance_history": attendance_history,
        "attendance_history_json": json.dumps(attendance_history),
    }

    return render(request, "controlAsistencia.html", context)


def logout_view(request):
    """
    Vista para cerrar sesión
    """
    if request.method == "POST":
        return LoginService.logout_user(request)

    # Si no es POST, redirigir a login
    return redirect("index")


def get_attendance_history_api(request):
    """
    API endpoint para obtener el historial de asistencia actualizado
    """
    # Verificar que el usuario esté autenticado
    if not LoginService.is_user_authenticated(request):
        return JsonResponse({"success": False, "message": "Usuario no autenticado"})

    # Solo permitir GET requests
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Método no permitido"})

    try:
        # Obtener información del usuario actual
        current_user = LoginService.get_current_user(request)

        # Obtener TODOS los registros del usuario
        attendance_history = AttendanceService.get_attendance_history(
            current_user["id"]
        )

        return JsonResponse(attendance_history)

    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"Error al obtener historial: {str(e)}"}
        )


def get_current_status_api(request):
    """
    API endpoint para obtener el estado actual de asistencia en tiempo real
    """
    # Verificar que el usuario esté autenticado
    if not LoginService.is_user_authenticated(request):
        return JsonResponse({"success": False, "message": "Usuario no autenticado"})

    # Solo permitir GET requests
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Método no permitido"})

    try:
        # Obtener información del usuario actual
        current_user = LoginService.get_current_user(request)

        # Obtener estado actual calculado desde la base de datos
        current_status = AttendanceService.get_current_status(current_user["id"])

        return JsonResponse({"success": True, "status": current_status})

    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"Error al obtener estado: {str(e)}"}
        )
