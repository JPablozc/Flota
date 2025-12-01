import os
from pathlib import Path

import dj_database_url

# =========================
# Paths base
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# Seguridad / entorno
# =========================

# En producción pon SECRET_KEY en variables de entorno
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "cambia-esta-clave-en-produccion"
)

# DEBUG a partir de variable de entorno
DEBUG = os.environ.get("DEBUG", "True") == "True"

ALLOWED_HOSTS = [
    "flota-o3i2.onrender.com",
    "127.0.0.1",
    "localhost",
]


# =========================
# Apps
# =========================

INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Terceros
    'cloudinary',
    'cloudinary_storage',

    # App local
    'gestion_flota',
]


# =========================
# Middleware
# =========================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise para static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# =========================
# URLs / WSGI
# =========================

ROOT_URLCONF = 'flota.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',  # carpeta global de templates
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'flota.wsgi.application'


# =========================
# Base de datos
# =========================

if os.environ.get("DATABASE_URL"):
    # Producción: usar PostgreSQL
    DATABASES = {
        'default': dj_database_url.parse(os.environ["DATABASE_URL"])
    }
else:
    # Desarrollo local: SQLite
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# =========================
# Password validators
# =========================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# =========================
# Internacionalización
# =========================

LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True


# =========================
# Static files (CSS, JS, imágenes estáticas)
# =========================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Carpeta de static en desarrollo (tu Bootstrap, JS, etc.)
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# WhiteNoise: sirve static comprimido y con hash de contenido
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# =========================
# Media files (subidas por el usuario) -> Cloudinary
# =========================

# CLOUDINARY_URL debe venir del entorno (Render + local)
CLOUDINARY_URL = os.environ.get("CLOUDINARY_URL")

# Fuerza HTTPS en las URLs de Cloudinary si está definido
os.environ.setdefault("CLOUDINARY_SECURE", "True")

# Todos los FileField / ImageField usan Cloudinary
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Django sigue usando estos valores, pero el storage genera URLs de Cloudinary
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# =========================
# Config general
# =========================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =========================
# Login / autenticación
# =========================

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'


# =========================
# Email (desarrollo)
# =========================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'flotadmin@miempresa.com'

# Correo al que llegarán las alertas
ALERTAS_EMAIL_DESTINO = 'tu.correo@miempresa.com'
