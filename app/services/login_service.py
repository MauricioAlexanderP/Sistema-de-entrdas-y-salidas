from django.shortcuts import redirect
from django.http import JsonResponse
from app.models import User
import hashlib


class LoginService:
    @staticmethod
    def validate_user(email, password):
        """
        Valida las credenciales del usuario contra la tabla app_user
        Returns: dict con resultado de la validación
        """
        try:
            # Buscar usuario por email
            user = User.objects.get(email=email)

            # Verificar contraseña (asumiendo que está almacenada en texto plano por ahora)
            # En producción deberías usar hash de contraseñas
            if user.password == password:
                return {"success": True, "user": user, "message": "Login exitoso"}
            else:
                return {
                    "success": False,
                    "user": None,
                    "message": "Contraseña incorrecta",
                }
        except User.DoesNotExist:
            return {"success": False, "user": None, "message": "Usuario no encontrado"}
        except Exception as e:
            return {
                "success": False,
                "user": None,
                "message": f"Error en la validación: {str(e)}",
            }

    @staticmethod
    def process_login(request):
        """
        Procesa el login y maneja la redirección
        Returns: Response apropiada (redirect o JSON error)
        """
        if request.method == "POST":
            email = request.POST.get("email")
            password = request.POST.get("password")

            if not email or not password:
                # Si es una petición AJAX, devolver JSON
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse(
                        {
                            "success": False,
                            "message": "Email y contraseña son requeridos",
                        }
                    )
                # Si no es AJAX, renderizar la página con error
                return JsonResponse(
                    {"success": False, "message": "Email y contraseña son requeridos"}
                )

            # Validar usuario
            validation_result = LoginService.validate_user(email, password)

            if validation_result["success"]:
                # Guardar información del usuario en la sesión
                request.session["user_id"] = validation_result["user"].id
                request.session["user_name"] = validation_result["user"].name
                request.session["user_email"] = validation_result["user"].email
                request.session["is_logged_in"] = True

                # Redireccionar a controlAsistencia.html
                return redirect("control_asistencia")
            else:
                # Si es una petición AJAX, devolver JSON
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse(
                        {"success": False, "message": validation_result["message"]}
                    )
                # Si no es AJAX, podrías renderizar la página con error
                return JsonResponse(
                    {"success": False, "message": validation_result["message"]}
                )

        return JsonResponse({"success": False, "message": "Método no permitido"})

    @staticmethod
    def is_user_authenticated(request):
        """
        Verifica si el usuario está autenticado
        Returns: bool
        """
        return request.session.get("is_logged_in", False)

    @staticmethod
    def get_current_user(request):
        """
        Obtiene la información del usuario actual desde la sesión
        Returns: dict con información del usuario o None
        """
        if LoginService.is_user_authenticated(request):
            return {
                "id": request.session.get("user_id"),
                "name": request.session.get("user_name"),
                "email": request.session.get("user_email"),
            }
        return None

    @staticmethod
    def logout_user(request):
        """
        Cierra la sesión del usuario
        """
        request.session.flush()
        return redirect("index")

    @staticmethod
    def hash_password(password):
        """
        Hash de contraseña usando SHA256 (para uso futuro)
        Returns: string con hash de la contraseña
        """
        return hashlib.sha256(password.encode()).hexdigest()
