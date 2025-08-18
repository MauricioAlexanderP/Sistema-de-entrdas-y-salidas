from django.utils import timezone
from django.http import JsonResponse
from app.models import User, Attendance
from datetime import time, timedelta
import pytz
from django.conf import settings


class AttendanceService:
    # Horarios establecidos (puedes configurarlos según necesites)
    STANDARD_ENTRY_TIME = time(7, 0)  # 7:00 AM
    STANDARD_EXIT_TIME = time(16, 0)  # 4:00 PM
    TOLERANCE_MINUTES = 30  # 30 minutos de tolerancia

    @staticmethod
    def get_local_time():
        """
        Obtiene la hora actual en la zona horaria configurada de Django
        """
        # Asegurar que siempre use la fecha local correctamente
        utc_time = timezone.now()
        local_tz = pytz.timezone(settings.TIME_ZONE)
        local_time = utc_time.astimezone(local_tz)
        return local_time

    @staticmethod
    def format_time_local(datetime_obj):
        """
        Formatea una fecha/hora en la zona horaria local
        """
        if datetime_obj is None:
            return None

        # Si es UTC, convertir a zona local
        if (
            datetime_obj.tzinfo is None
            or datetime_obj.tzinfo.utcoffset(datetime_obj) is None
        ):
            # Si no tiene zona horaria, asumimos que es UTC
            utc_time = timezone.make_aware(datetime_obj, pytz.UTC)
        else:
            utc_time = datetime_obj

        local_tz = pytz.timezone(settings.TIME_ZONE)
        local_time = utc_time.astimezone(local_tz)
        return local_time.strftime("%I:%M %p")

    @staticmethod
    def get_user_today_attendance(user_id):
        """
        Obtiene el registro de asistencia del día actual para un usuario
        Devuelve el registro MÁS RECIENTE del día actual
        CORREGIDO: Maneja correctamente las zonas horarias
        """
        try:
            # Obtener fecha local actual
            local_time = AttendanceService.get_local_time()
            today = local_time.date()
            print(
                f"🔍 Buscando asistencia para usuario {user_id} en fecha local: {today}"
            )

            # CORREGIDO: Buscar por rango de fechas UTC que corresponda al día local
            local_tz = pytz.timezone(settings.TIME_ZONE)

            # Inicio del día en zona local, convertido a UTC
            start_of_day_local = local_tz.localize(
                timezone.datetime.combine(
                    today, timezone.datetime.min.time().replace(tzinfo=None)
                )
            )
            start_of_day_utc = start_of_day_local.astimezone(pytz.UTC)

            # Fin del día en zona local, convertido a UTC
            end_of_day_local = local_tz.localize(
                timezone.datetime.combine(
                    today,
                    timezone.datetime.max.time()
                    .replace(tzinfo=None)
                    .replace(microsecond=0),
                )
            )
            end_of_day_utc = end_of_day_local.astimezone(pytz.UTC)

            print(f"🔍 Rango de búsqueda UTC: {start_of_day_utc} a {end_of_day_utc}")

            # Obtener el registro MÁS RECIENTE del día actual usando rango UTC
            attendance = (
                Attendance.objects.filter(
                    user_id=user_id,
                    entry_time__range=(start_of_day_utc, end_of_day_utc),
                )
                .order_by("-entry_time")
                .first()
            )

            print(f"🔍 Registro encontrado: {attendance}")
            if attendance:
                print(f"🔍 Entry time UTC: {attendance.entry_time}")
                local_entry = attendance.entry_time.astimezone(local_tz)
                print(f"🔍 Entry time local: {local_entry}")

            return attendance
        except Exception as e:
            print(f"❌ Error en get_user_today_attendance: {str(e)}")
            return None

    @staticmethod
    def can_register_entry(user_id):
        """
        Verifica si el usuario puede registrar una entrada
        Incluye validación robusta para evitar duplicados
        """
        attendance = AttendanceService.get_user_today_attendance(user_id)

        # Si no hay registro del día, puede registrar entrada
        if not attendance:
            return True, "Puede registrar entrada"

        # Si ya registró entrada pero no salida, no puede registrar otra entrada
        if attendance and not attendance.exit_time:
            return False, "Ya tienes una jornada activa. Marca tu salida primero."

        # Si ya completó entrada y salida, no puede registrar otra entrada
        if attendance and attendance.exit_time:
            return False, "Ya has completado tu jornada para hoy"

        return True, "Puede registrar entrada"

    @staticmethod
    def can_register_exit(user_id):
        """
        Verifica si el usuario puede registrar una salida
        """
        attendance = AttendanceService.get_user_today_attendance(user_id)

        # Si no hay registro del día, no puede registrar salida
        if not attendance:
            return False, "Primero debes registrar tu entrada"

        # Si ya registró salida, no puede registrar otra
        if attendance.exit_time:
            return False, "Ya has registrado tu salida para hoy"

        return True, "Puede registrar salida"

    @staticmethod
    def is_outside_schedule(entry_type, current_time):
        """
        Verifica si el registro está fuera del horario establecido
        """
        # Convertir a hora local para la comparación
        local_tz = pytz.timezone(settings.TIME_ZONE)
        local_current_time = current_time.astimezone(local_tz)
        current_hour_minute = local_current_time.time()

        if entry_type == "entry":
            # Calcular ventana de entrada (con tolerancia)
            early_limit = time(
                max(0, AttendanceService.STANDARD_ENTRY_TIME.hour - 1),
                AttendanceService.STANDARD_ENTRY_TIME.minute,
            )
            late_limit = time(
                AttendanceService.STANDARD_ENTRY_TIME.hour,
                AttendanceService.STANDARD_ENTRY_TIME.minute
                + AttendanceService.TOLERANCE_MINUTES,
            )

            # Si está fuera del rango permitido
            if current_hour_minute < early_limit or current_hour_minute > late_limit:
                return (
                    True,
                    f"Horario estándar de entrada: {AttendanceService.STANDARD_ENTRY_TIME.strftime('%I:%M %p')}",
                )

        elif entry_type == "exit":
            # Calcular ventana de salida (con tolerancia)
            early_limit = time(
                AttendanceService.STANDARD_EXIT_TIME.hour,
                max(
                    0,
                    AttendanceService.STANDARD_EXIT_TIME.minute
                    - AttendanceService.TOLERANCE_MINUTES,
                ),
            )
            late_limit = time(
                AttendanceService.STANDARD_EXIT_TIME.hour + 2,
                AttendanceService.STANDARD_EXIT_TIME.minute,
            )

            # Si está fuera del rango permitido
            if current_hour_minute < early_limit or current_hour_minute > late_limit:
                return (
                    True,
                    f"Horario estándar de salida: {AttendanceService.STANDARD_EXIT_TIME.strftime('%I:%M %p')}",
                )

        return False, ""

    @staticmethod
    def register_entry(user_id):
        """
        Registra la entrada de un usuario
        """
        try:
            # Verificar si puede registrar entrada
            can_register, message = AttendanceService.can_register_entry(user_id)
            if not can_register:
                return {
                    "success": False,
                    "message": message,
                    "notification_type": "error",
                }

            # Obtener usuario
            user = User.objects.get(id=user_id)
            current_time = timezone.now()  # Esto sigue siendo UTC para la base de datos

            # Verificar si está fuera de horario
            is_outside, schedule_info = AttendanceService.is_outside_schedule(
                "entry", current_time
            )

            # Crear el registro de asistencia
            attendance = Attendance.objects.create(user=user, entry_time=current_time)

            # Formatear tiempo para mostrar al usuario (zona local)
            local_time_str = AttendanceService.format_time_local(current_time)
            local_time = AttendanceService.get_local_time()

            response_data = {
                "success": True,
                "message": f"Entrada registrada exitosamente a las {local_time_str}",
                "entry_time": local_time_str,
                "date": local_time.strftime("%Y-%m-%d"),
                "attendance_id": attendance.id,
                "notification_type": "success",
            }

            # Si está fuera de horario, agregar notificación
            if is_outside:
                response_data["outside_schedule"] = True
                response_data["schedule_message"] = (
                    f"⚠️ Registro fuera de horario. {schedule_info}"
                )
                response_data["notification_type"] = "warning"

            return response_data

        except User.DoesNotExist:
            return {
                "success": False,
                "message": "Usuario no encontrado",
                "notification_type": "error",
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al registrar entrada: {str(e)}",
                "notification_type": "error",
            }

    @staticmethod
    def register_exit(user_id):
        """
        Registra la salida de un usuario
        """
        try:
            # Verificar si puede registrar salida
            can_register, message = AttendanceService.can_register_exit(user_id)
            if not can_register:
                return {
                    "success": False,
                    "message": message,
                    "notification_type": "error",
                }

            # Obtener el registro de asistencia del día
            attendance = AttendanceService.get_user_today_attendance(user_id)
            current_time = timezone.now()  # UTC para la base de datos

            # Actualizar la hora de salida
            attendance.exit_time = current_time
            attendance.save()

            # Verificar si está fuera de horario
            is_outside, schedule_info = AttendanceService.is_outside_schedule(
                "exit", current_time
            )

            # Calcular horas trabajadas
            work_duration = current_time - attendance.entry_time
            hours_worked = work_duration.total_seconds() / 3600

            # Formatear tiempos para mostrar al usuario (zona local)
            exit_time_str = AttendanceService.format_time_local(current_time)
            entry_time_str = AttendanceService.format_time_local(attendance.entry_time)
            local_time = AttendanceService.get_local_time()

            response_data = {
                "success": True,
                "message": f"Salida registrada exitosamente a las {exit_time_str}",
                "exit_time": exit_time_str,
                "entry_time": entry_time_str,
                "hours_worked": round(hours_worked, 2),
                "date": local_time.strftime("%Y-%m-%d"),
                "attendance_id": attendance.id,
                "notification_type": "success",
            }

            # Si está fuera de horario, agregar notificación
            if is_outside:
                response_data["outside_schedule"] = True
                response_data["schedule_message"] = (
                    f"⚠️ Registro fuera de horario. {schedule_info}"
                )
                response_data["notification_type"] = "warning"

            return response_data

        except Exception as e:
            return {
                "success": False,
                "message": f"Error al registrar salida: {str(e)}",
                "notification_type": "error",
            }

    @staticmethod
    def get_current_status(user_id):
        """
        Obtiene el estado actual de asistencia del usuario
        Calcula el tiempo trabajado en tiempo real desde la base de datos
        """
        try:
            print(f"🔍 get_current_status llamado para usuario: {user_id}")
            attendance = AttendanceService.get_user_today_attendance(user_id)
            print(f"🔍 Registro de asistencia encontrado: {attendance}")

            if attendance:
                print(f"🔍 Entry time: {attendance.entry_time}")
                print(f"🔍 Exit time: {attendance.exit_time}")

            if not attendance:
                print("🔍 No hay registro de asistencia para hoy - Estado: OUT")
                return {
                    "status": "out",
                    "message": "No has iniciado tu jornada",
                    "can_register_entry": True,
                    "can_register_exit": False,
                    "hours_worked": 0,
                    "entry_time": None,
                    "exit_time": None,
                }

            # Si tiene entrada pero no salida (jornada en progreso)
            if attendance and not attendance.exit_time:
                print("🔍 Jornada EN PROGRESO detectada - Estado: IN")
                # SIEMPRE calcular desde la base de datos usando timezone.now()
                current_time = timezone.now()  # Tiempo actual del servidor
                work_duration = current_time - attendance.entry_time
                hours_worked = work_duration.total_seconds() / 3600

                # Formatear tiempos
                entry_time_str = AttendanceService.format_time_local(
                    attendance.entry_time
                )

                # Calcular tiempo transcurrido para mostrar
                hours = int(hours_worked)
                minutes = int((hours_worked - hours) * 60)

                result = {
                    "status": "in",
                    "message": f"Jornada iniciada a las {entry_time_str}",
                    "entry_time": entry_time_str,
                    "exit_time": None,
                    "hours_worked": round(hours_worked, 2),
                    "hours_worked_display": f"{hours}h {minutes}m",
                    "can_register_entry": False,
                    "can_register_exit": True,
                    "attendance_id": attendance.id,
                }
                print(f"🔍 Resultado para jornada EN PROGRESO: {result}")
                return result

            # Si tiene entrada Y salida (jornada completada)
            if attendance and attendance.exit_time:
                print("🔍 Jornada COMPLETADA detectada - Estado: COMPLETED")
                work_duration = attendance.exit_time - attendance.entry_time
                hours_worked = work_duration.total_seconds() / 3600

                entry_time_str = AttendanceService.format_time_local(
                    attendance.entry_time
                )
                exit_time_str = AttendanceService.format_time_local(
                    attendance.exit_time
                )

                # Calcular tiempo transcurrido para mostrar
                hours = int(hours_worked)
                minutes = int((hours_worked - hours) * 60)

                result = {
                    "status": "completed",
                    "message": f"Jornada completada ({round(hours_worked, 2)} horas)",
                    "entry_time": entry_time_str,
                    "exit_time": exit_time_str,
                    "hours_worked": round(hours_worked, 2),
                    "hours_worked_display": f"{hours}h {minutes}m",
                    "can_register_entry": False,
                    "can_register_exit": False,
                    "attendance_id": attendance.id,
                }
                print(f"🔍 Resultado para jornada COMPLETADA: {result}")
                return result

        except Exception as e:
            print(f"❌ Error en get_current_status: {str(e)}")
            return {
                "status": "error",
                "message": f"Error al obtener estado: {str(e)}",
                "can_register_entry": False,
                "can_register_exit": False,
                "hours_worked": 0,
            }

    @staticmethod
    def process_attendance_action(request):
        """
        Procesa las acciones de asistencia (entrada/salida)
        """
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Método no permitido"})

        action = request.POST.get("action")
        user_id = request.session.get("user_id")

        if not user_id:
            return JsonResponse({"success": False, "message": "Usuario no autenticado"})

        # Log para depuración
        print(f"Acción recibida: {action}, Usuario ID: {user_id}")

        if action == "entry":
            result = AttendanceService.register_entry(user_id)
        elif action == "exit":
            result = AttendanceService.register_exit(user_id)
        else:
            return JsonResponse({"success": False, "message": "Acción no válida"})

        # Log para depuración del resultado
        print(f"Resultado de la acción {action}: {result}")

        return JsonResponse(result)

    @staticmethod
    def get_attendance_history(user_id, days=None):
        """
        Obtiene el historial de asistencia completo del usuario o de los últimos N días
        Si days es None, obtiene TODOS los registros
        """
        try:
            # CORREGIDO: Definir local_now siempre, independientemente del valor de days
            local_now = AttendanceService.get_local_time()

            # Si no se especifica days, obtener todos los registros
            if days is None:
                # Obtener TODOS los registros de asistencia del usuario
                attendances = Attendance.objects.filter(user_id=user_id).order_by(
                    "-entry_time"
                )
            else:
                # Calcular fecha límite usando hora local
                end_date = local_now.date()
                start_date = end_date - timedelta(days=days - 1)

                # Obtener registros de asistencia en el rango
                attendances = Attendance.objects.filter(
                    user_id=user_id, entry_time__date__range=[start_date, end_date]
                ).order_by("-entry_time__date")

            history_data = []
            local_tz = pytz.timezone(settings.TIME_ZONE)

            for attendance in attendances:
                # Convertir tiempos a zona local
                entry_local = attendance.entry_time.astimezone(local_tz)

                # Calcular horas trabajadas
                if attendance.exit_time:
                    exit_local = attendance.exit_time.astimezone(local_tz)
                    work_duration = attendance.exit_time - attendance.entry_time
                    hours_worked = work_duration.total_seconds() / 3600
                    exit_time = exit_local.strftime("%I:%M %p")
                    status = "completed"
                else:
                    hours_worked = 0
                    exit_time = None
                    # Verificar si es el día actual y está en curso
                    if entry_local.date() == local_now.date():
                        status = "in_progress"
                        # Calcular horas actuales
                        current_duration = timezone.now() - attendance.entry_time
                        hours_worked = current_duration.total_seconds() / 3600
                    else:
                        status = "incomplete"

                # Usar nombres de días y meses en español
                day_names = {
                    "Monday": "Lunes",
                    "Tuesday": "Martes",
                    "Wednesday": "Miércoles",
                    "Thursday": "Jueves",
                    "Friday": "Viernes",
                    "Saturday": "Sábado",
                    "Sunday": "Domingo",
                }

                month_names = {
                    "January": "enero",
                    "February": "febrero",
                    "March": "marzo",
                    "April": "abril",
                    "May": "mayo",
                    "June": "junio",
                    "July": "julio",
                    "August": "agosto",
                    "September": "septiembre",
                    "October": "octubre",
                    "November": "noviembre",
                    "December": "diciembre",
                }

                day_name_en = entry_local.strftime("%A")
                month_name_en = entry_local.strftime("%B")

                history_data.append(
                    {
                        "date": entry_local.date().strftime("%Y-%m-%d"),
                        "day_name": day_names.get(day_name_en, day_name_en),
                        "day_number": entry_local.day,
                        "month_name": month_names.get(month_name_en, month_name_en),
                        "entry_time": entry_local.strftime("%I:%M %p"),
                        "exit_time": exit_time,
                        "hours_worked": round(hours_worked, 2),
                        "status": status,
                    }
                )

            return {
                "success": True,
                "history": history_data,
                "total_records": len(history_data),
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error al obtener historial: {str(e)}",
                "history": [],
            }
