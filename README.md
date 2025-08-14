# 🕐 Sistema de Entradas y Salidas

Sistema web desarrollado en Django para el control y registro de asistencia de empleados, permitiendo marcar horarios de entrada y salida con seguimiento en tiempo real.

## 🚀 Características

### ✅ Funcionalidades principales
- **Registro de entrada y salida** con timestamps precisos
- **Cálculo automático** de horas trabajadas en tiempo real
- **Gestión de zonas horarias** para registros precisos
- **Historial completo** de asistencias con filtros y búsqueda
- **Validación de horarios** con notificaciones fuera de horario
- **Interfaz responsive** con Tailwind CSS
- **Persistencia de estado** con localStorage y cookies
- **Sincronización automática** con el servidor

### 🛡️ Seguridad y validaciones
- Sistema de autenticación de usuarios
- Prevención de registros duplicados
- Validación de jornadas activas
- Manejo de sesiones seguras

## 🛠️ Tecnologías utilizadas

### Backend
- **Django 5.2.5** - Framework web
- **MySQL** - Base de datos principal
- **pytz** - Manejo de zonas horarias

### Frontend
- **HTML5/CSS3** - Estructura y estilos
- **JavaScript ES6+** - Interactividad
- **Tailwind CSS** - Framework de estilos
- **SweetAlert2** - Notificaciones elegantes
- **Font Awesome** - Iconografía

## 📋 Requisitos del sistema

- **Python 3.8+**
- **MySQL 5.7+** o **MariaDB 10.3+**
- **pip** (gestor de paquetes de Python)
- **Git** (control de versiones)

## 🚀 Configuración del entorno de desarrollo

### 1. Clonar el repositorio
```bash
git clone https://github.com/MauricioAlexanderP/Sistema-de-entrdas-y-salidas.git
cd Sistema-de-entrdas-y-salidas
```

### 2. Crear y activar entorno virtual
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos

#### Crear base de datos en MySQL:
```sql
CREATE DATABASE sistema_asistencia CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'usuario_asistencia'@'localhost' IDENTIFIED BY 'tu_password_segura';
GRANT ALL PRIVILEGES ON sistema_asistencia.* TO 'usuario_asistencia'@'localhost';
FLUSH PRIVILEGES;
```

#### Configurar Django (settings.py):
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sistema_asistencia',
        'USER': 'usuario_asistencia',
        'PASSWORD': 'tu_password_segura',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 5. Ejecutar migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Crear superusuario (opcional)
```bash
python manage.py createsuperuser
```

### 7. Ejecutar servidor de desarrollo
```bash
python manage.py runserver
```

El sistema estará disponible en: `http://127.0.0.1:8000/`

## 📁 Estructura del proyecto

```
sistema-entrada-salida/
├── app/                          # Aplicación principal
│   ├── migrations/              # Migraciones de base de datos
│   ├── services/               # Lógica de negocio
│   │   ├── attendance_service.py  # Servicio de asistencia
│   │   └── login_service.py       # Servicio de autenticación
│   ├── templates/              # Plantillas HTML
│   │   ├── controlAsistencia.html
│   │   └── index.html
│   ├── models.py              # Modelos de datos
│   ├── views.py               # Vistas/controladores
│   ├── urls.py                # URLs de la aplicación
│   └── admin.py               # Configuración admin
├── sistema_entrada_salida/     # Configuración del proyecto
│   ├── settings.py            # Configuración principal
│   ├── urls.py                # URLs principales
│   └── wsgi.py                # WSGI configuration
├── venv/                      # Entorno virtual (ignorado en git)
├── manage.py                  # Script de gestión Django
├── requirements.txt           # Dependencias del proyecto
├── .gitignore                # Archivos ignorados por git
└── README.md                 # Este archivo
```

## 🗄️ Modelos de datos

### Usuario (User)
- `name`: Nombre del usuario
- `email`: Correo electrónico (único)
- `password`: Contraseña encriptada

### Asistencia (Attendance)
- `user`: Relación con Usuario
- `entry_time`: Hora de entrada (UTC)
- `exit_time`: Hora de salida (UTC, opcional)
- Timestamps automáticos de creación y actualización

## 🔧 Comandos útiles

### Desarrollo
```bash
# Ejecutar servidor de desarrollo
python manage.py runserver

# Hacer migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recolectar archivos estáticos
python manage.py collectstatic

# Ejecutar tests
python manage.py test
```

### Base de datos
```bash
# Resetear migraciones (¡CUIDADO! Borra datos)
python manage.py reset_db
python manage.py makemigrations
python manage.py migrate

# Backup de base de datos
mysqldump -u usuario_asistencia -p sistema_asistencia > backup.sql

# Restaurar backup
mysql -u usuario_asistencia -p sistema_asistencia < backup.sql
```

## 🌐 API Endpoints

### Autenticación
- `GET /` - Página de login
- `POST /` - Procesar login
- `POST /logout/` - Cerrar sesión

### Control de asistencia
- `GET /control-asistencia/` - Panel principal
- `POST /control-asistencia/` - Registrar entrada/salida

### APIs
- `GET /api/current-status/` - Estado actual del usuario
- `GET /api/attendance-history/` - Historial de asistencias

## 🚨 Troubleshooting

### Problemas comunes

#### Error de conexión a MySQL
```bash
# Verificar que MySQL esté ejecutándose
mysql --version
mysql -u root -p

# Instalar cliente MySQL si es necesario
pip install mysqlclient
```

#### Error de zona horaria
```python
# En settings.py
TIME_ZONE = 'America/Mexico_City'  # Ajustar según ubicación
USE_TZ = True
```

#### Problemas con migraciones
```bash
# Borrar archivos de migración (excepto __init__.py)
rm app/migrations/00*.py

# Recrear migraciones
python manage.py makemigrations
python manage.py migrate
```

## 📝 Configuración de producción

### Variables de entorno recomendadas
```bash
# .env file
DEBUG=False
SECRET_KEY=tu_clave_secreta_super_segura
DATABASE_URL=mysql://user:password@host:port/database
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
```

### Configuraciones adicionales
- Configurar servidor web (Nginx/Apache)
- Usar servidor WSGI (Gunicorn/uWSGI)
- Configurar SSL/HTTPS
- Implementar backups automáticos
- Configurar logs de producción

## 🤝 Contribuir al proyecto

### 1. Fork del repositorio
```bash
git fork https://github.com/MauricioAlexanderP/Sistema-de-entrdas-y-salidas.git
```

### 2. Crear rama para nueva funcionalidad
```bash
git checkout -b feature/nueva-funcionalidad
```

### 3. Realizar cambios y commit
```bash
git add .
git commit -m "feat: descripción de la nueva funcionalidad"
```

### 4. Push y crear Pull Request
```bash
git push origin feature/nueva-funcionalidad
# Crear PR desde GitHub
```

### Estándares de código
- Seguir PEP 8 para Python
- Usar nombres descriptivos para variables y funciones
- Documentar funciones complejas
- Escribir tests para nuevas funcionalidades
- Mantener commits atómicos y descriptivos

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 👥 Equipo de desarrollo

- **Mauricio Alexander P.** - Desarrollador principal
- Contribuciones bienvenidas de la comunidad

## 📞 Soporte

Para reportar bugs o solicitar nuevas funcionalidades, por favor crear un issue en:
https://github.com/MauricioAlexanderP/Sistema-de-entrdas-y-salidas/issues

## 🔄 Changelog

### v1.0.0 (2025-08-14)
- ✅ Sistema básico de registro de entrada/salida
- ✅ Cálculo de horas trabajadas en tiempo real
- ✅ Historial completo con filtros
- ✅ Validación de horarios estándar
- ✅ Interfaz responsive
- ✅ Persistencia de estado con localStorage/cookies
- ✅ Manejo correcto de zonas horarias

---

🚀 **¡Listo para desarrollar!** Si tienes alguna pregunta, no dudes en crear un issue o contactar al equipo de desarrollo.
