"""Configuracion local con una base SQLite independiente."""

from .settings import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS += ['localhost', '127.0.0.1', 'testserver']  # noqa: F405
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db_local.sqlite3",  # noqa: F405
    }
}
