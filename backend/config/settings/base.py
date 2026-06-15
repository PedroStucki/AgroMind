# config/settings/base.py
# Configurações compartilhadas por TODOS os ambientes.
# Nunca execute com este settings diretamente — use development.py ou production.py.

import environ
from pathlib import Path

# ---------------------------------------------------------------------------
# Caminhos base
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# BASE_DIR aponta para AgroGestao/backend/

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
)

# Carrega o arquivo .env a partir da raiz do backend
environ.Env.read_env(BASE_DIR / ".env")

# ---------------------------------------------------------------------------
# Segurança
# ---------------------------------------------------------------------------
SECRET_KEY    = env("DJANGO_SECRET_KEY")
DEBUG         = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

# ---------------------------------------------------------------------------
# Aplicações instaladas
# ---------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]

SITE_ID = 1

THIRD_PARTY_APPS: list[str] = [
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
]

LOCAL_APPS = [
    "apps.users",
    "apps.properties",
    "apps.planting",
    "apps.estoque",
    "apps.weather",
    "apps.operational",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR.parent / "frontend" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# RF-05 | Segurança de senhas — BCrypt como hasher principal
# ---------------------------------------------------------------------------
PASSWORD_HASHERS = [
    # Posição 0 = hasher PADRÃO para novas senhas
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",

    # Hashers legados abaixo: usados APENAS para verificar senhas antigas
    # (usuários migrados de outro sistema). Django faz upgrade automático
    # para BCrypt no próximo login do usuário.
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
]
# Por que BCryptSHA256 e não BCrypt puro?
# O BCrypt tem limite de 72 bytes na entrada. O SHA256PasswordHasher faz um
# pré-hash da senha antes de passar ao BCrypt, eliminando esse limite.

# ---------------------------------------------------------------------------
# Banco de Dados — MySQL
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ---------------------------------------------------------------------------
# RF-02 | Sessões e Segurança de Autenticação
# ---------------------------------------------------------------------------
AUTH_USER_MODEL = "users.CustomUser"

SESSION_ENGINE = "django.contrib.sessions.backends.db"
# Sessões armazenadas no banco — permite invalidação server-side.

SESSION_COOKIE_AGE = env.int("SESSION_COOKIE_AGE", default=28800)
# Padrão: 8 horas (28800 segundos). Configurável via .env.

SESSION_EXPIRE_AT_BROWSER_CLOSE = env.bool(
    "SESSION_EXPIRE_AT_BROWSER_CLOSE", default=False
)

SESSION_COOKIE_HTTPONLY = True
# Impede que JavaScript acesse o cookie de sessão — mitiga XSS.

SESSION_COOKIE_SAMESITE = "Lax"
# Proteção contra CSRF em requisições cross-site.

# ---------------------------------------------------------------------------
# Validação de senha (RF-05 — complementar ao bcrypt)
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internacionalização
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "pt-br"
TIME_ZONE     = "America/Sao_Paulo"
USE_I18N      = True
USE_TZ        = True
# USE_TZ=True é OBRIGATÓRIO. Django armazena tudo em UTC internamente
# e converte para TIME_ZONE na exibição — evita bugs de horário de verão.

# ---------------------------------------------------------------------------
# Arquivos estáticos
# ---------------------------------------------------------------------------
STATIC_URL  = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR.parent / "frontend" / "static",
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# RF-03 | E-mail (configurado por ambiente)
# ---------------------------------------------------------------------------
DEFAULT_FROM_EMAIL     = env("DEFAULT_FROM_EMAIL", default="noreply@agrogestao.com.br")
PASSWORD_RESET_TIMEOUT = 3600  # Link de reset expira em 1 hora

# ---------------------------------------------------------------------------
# Django REST Framework + SimpleJWT
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

from datetime import timedelta  # noqa: E402

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
    

}
LOGIN_URL = "/usuarios/login/"
LOGIN_REDIRECT_URL = "/usuarios/dashboard/"
LOGOUT_REDIRECT_URL = "/usuarios/login/"

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True # Apenas para desenvolvimento local
