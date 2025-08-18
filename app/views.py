from django.shortcuts import render, redirect
from django.http import JsonResponse
from app.services.login_service import LoginService
from app.services.attendance_service import AttendanceService
from app.models import Attendance, User





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

def dashboard_view(request):
    # Verificar que el usuario esté autenticado
    if not LoginService.is_user_authenticated(request):
        return redirect("index")

    # Obtener información del usuario actual
    current_user = LoginService.get_current_user(request)
    email = current_user.get("email", "")
    
    # Validar si el usuario es administrador por extensión de correo
    if not email.endswith("@admin.com"):
        return render(request, "no_autorizado.html")

    # Obtener datos dinámicos para el dashboard
    from django.utils import timezone
    from datetime import timedelta
    
    # Obtener fecha local actual
    from app.services.attendance_service import AttendanceService
    local_now = AttendanceService.get_local_time()
    
    # Obtener fecha de filtro desde parámetros GET
    filter_date = request.GET.get('date')
    if filter_date:
        try:
            from datetime import datetime
            # Handle both YYYY-MM-DD and YYYY-DD-MM formats
            try:
                selected_date = datetime.strptime(filter_date, '%Y-%m-%d').date()
            except ValueError:
                # Try YYYY-DD-MM format if the first fails
                selected_date = datetime.strptime(filter_date, '%Y-%d-%m').date()
        except ValueError:
            selected_date = local_now.date()
    else:
        selected_date = local_now.date()
    
    # Obtener registros de asistencia filtrados por fecha
    if filter_date:
        # Use timezone-aware date filtering
        from django.utils import timezone
        start_of_day = timezone.make_aware(
            datetime.combine(selected_date, datetime.min.time())
        )
        end_of_day = timezone.make_aware(
            datetime.combine(selected_date, datetime.max.time())
        )
        
        recent_attendances = Attendance.objects.select_related('user').filter(
            entry_time__range=(start_of_day, end_of_day)
        ).order_by('-entry_time')
    else:
        recent_attendances = Attendance.objects.select_related('user').order_by('-entry_time')[:10]
    
    # Calcular estadísticas para la fecha seleccionada
    today_attendances = Attendance.objects.filter(entry_time__date=selected_date)
    
    # Estadísticas del día
    total_today = today_attendances.count()
    late_arrivals = 0
    on_time = 0
    for attendance in today_attendances:
        entry_time = attendance.entry_time.time()
        if entry_time > timezone.datetime.strptime('08:30', '%H:%M').time():
            late_arrivals += 1
        else:
            on_time += 1

    # Update context to reflect filtered data
    
    # Preparar contexto con datos dinámicos
    context = {
        'recent_attendances': recent_attendances,
        'total_today': total_today,
        'late_arrivals': late_arrivals,
        'on_time': on_time,
        'attendance_percentage': (on_time / max(total_today, 1)) * 100,
        'current_user': current_user,
        'selected_date': selected_date,
        'is_filtered': bool(filter_date),
    }
    
    return render(request, "dashboard.html", context)

