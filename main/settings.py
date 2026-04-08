# type: ignore[reportAttributeAccessIssue]
import sys
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


env = environ.Env(
    # Django
    DEBUG=(bool, False),
    DJANGO_SECRET_KEY=str,
    ADDITIONAL_ALLOWED_HOSTS=(list, []),  # Eg: api.example.org
    APP_ENVIRONMENT=str,  # DEV, STAGE, PROD
    APP_TYPE=str,  # WEB, WORKER, WORKER-BEAT
    APP_RELEASE=(str, None),  # As fallback we will try to use .git/HEAD
    APP_LOG_LEVEL=(str, "INFO"),
    # Domain configs
    APP_DOMAIN=str,  # Eg: https://api.example.org
    FRONTEND_DOMAIN=str,  # Eg: https://web.example.org
    SESSION_COOKIE_DOMAIN=str,  # .example.com
    CSRF_COOKIE_DOMAIN=str,  # .example.com
    ADDITIONAL_TRUSTED_ORIGINS=(list, []),  # https://app1.example.com,https://app2.example.com
    # NOTE: Changing TIME_ZONE will break celery periodic tasks https://django-celery-beat.readthedocs.io/en/latest/#important-warning-about-time-zones
    TIME_ZONE=(str, "UTC"),
    # Database
    POSTGRES_DB=str,
    POSTGRES_USER=str,
    POSTGRES_PASSWORD=str,
    POSTGRES_HOST=str,
    POSTGRES_PORT=(int, 5432),
    # Storage
    MEDIA_URL=(str, "media/"),
    STATIC_URL=(str, "static/"),
    TEMP_DIR=(str, "/tmp/"),  # noqa: S108
    # -- S3 storage
    AWS_S3_ENABLED=(bool, False),
    AWS_S3_ENDPOINT_URL=(str, None),
    AWS_S3_ACCESS_KEY_ID=str,
    AWS_S3_SECRET_ACCESS_KEY=str,
    AWS_S3_REGION_NAME=str,
    AWS_S3_MEDIA_BUCKET_NAME=str,
    AWS_S3_STATIC_BUCKET_NAME=str,
    # -- Filesystem (default) XXX: Don't use in production
    MEDIA_ROOT=(str, BASE_DIR / "data/media"),
    STATIC_ROOT=(str, BASE_DIR / "data/static"),
    # Pytest
    PYTEST_XDIST_WORKER=(str, None),
    # Email
    EMAIL_API_URL=(str, None),
    EMAIL_API_KEY=(str, None),
    EMAIL_BACKEND=(str, None),
    EMAIL_API_TIMEOUT=(int, None),
    EMAIL_HOST=(str, None),
    EMAIL_PORT=(str, None),
    EMAIL_HOST_USER=(str, None),
    EMAIL_HOST_PASSWORD=(str, None),
    DEFAULT_FROM_EMAIL=(str, None),
    EMAIL_TO=(str, None),
    EMAIL_USE_TLS=(bool, False),
    # celery
    CELERY_REDIS_URL=str,  # redis://redis:6379/0
    # Cache
    CACHE_REDIS_URL=str,  # redis://redis:6379/1
    TEST_CACHE_REDIS_URL=(str, None),  # redis://redis:6379/11
)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

APP_LOG_LEVEL = env("APP_LOG_LEVEL")
APP_DOMAIN = env.url("APP_DOMAIN")
FRONTEND_DOMAIN = env.url("FRONTEND_DOMAIN")
APP_ENVIRONMENT = env("APP_ENVIRONMENT").upper()
APP_TYPE = env("APP_TYPE").upper()
SECRET_KEY = env("DJANGO_SECRET_KEY")
STATICFILES_DIRS = (str(BASE_DIR.joinpath("static")),)
DEBUG = env("DEBUG")

ALLOWED_HOSTS = [
    APP_DOMAIN.hostname,
    "web",
    *env("ADDITIONAL_ALLOWED_HOSTS"),
]

# See if we are inside a test environment (pytest)
IS_TESTING = (
    any(
        [
            arg in sys.argv
            for arg in [
                "test",
                "pytest",
                "/usr/local/bin/pytest",
                "py.test",
                "/usr/local/bin/py.test",
                "/usr/local/lib/python3.6/dist-packages/py/test.py",
            ]
            # Provided by pytest-xdist
        ],
    )
    or env("PYTEST_XDIST_WORKER") is not None
)

# Application definition

INSTALLED_APPS = [
    # Core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # External
    "strawberry_django",
    "corsheaders",
    "django_premailer",
    "djangoql",
    "rest_framework",
    "mdeditor",
    "captcha",
    # - Health-check
    "health_check",  # required
    "health_check.db",
    "health_check.cache",
    "health_check.storage",
    "health_check.contrib.migrations",
    # Internal
    "apps.common",
    "apps.tool_picker",
    "apps.resources",
    "apps.user",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "main.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [(BASE_DIR / "templates")],
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

WSGI_APPLICATION = "main.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST"),
        "PORT": env("POSTGRES_PORT"),
    },
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "user.User"

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = env("TIME_ZONE")

USE_I18N = True

USE_TZ = True

X_FRAME_OPTIONS = "SAMEORIGIN"

MDEDITOR_CONFIGS = {
    "default": {
        "width": "80% ",  # Custom edit box width
        "height": 500,  # Custom edit box height
        "toolbar": [
            "undo",
            "redo",
            "|",
            "bold",
            "del",
            "italic",
            "quote",
            "ucwords",
            "uppercase",
            "lowercase",
            "|",
            "h1",
            "h2",
            "h3",
            "h5",
            "h6",
            "|",
            "list-ul",
            "list-ol",
            "hr",
            "|",
            "link",
            "reference-link",
            "image",
            "code",
            "preformatted-text",
            "code-block",
            "table",
            "datetime",
            "emoji",
            "html-entities",
            "pagebreak",
            "goto-line",
            "|",
            "help",
            "info",
            "||",
            "preview",
            "watch",
            "fullscreen",
        ],  # custom edit box toolbar
        # image upload format type
        "upload_image_formats": ["jpg", "jpeg", "gif", "png", "bmp", "webp", "svg"],
        "image_folder": "editor",  # image save the folder name
        "theme": "default",  # edit box theme, dark / default
        "preview_theme": "default",  # Preview area theme, dark / default
        "editor_theme": "default",  # edit area theme, pastel-on-dark / default
        "toolbar_autofixed": False,  # Whether the toolbar capitals
        "search_replace": True,  # Whether to open the search for replacement
        "emoji": True,  # whether to open the expression function
        "tex": True,  # whether to open the tex chart function
        "flow_chart": True,  # whether to open the flow chart function
        "sequence": True,  # Whether to open the sequence diagram function
        "watch": True,  # Live preview
        "lineWrapping": True,  # lineWrapping
        "lineNumbers": True,  # lineNumbers
        "language": "en",  # zh / en / es
    },
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

TEMP_DIR = env("TEMP_DIR")
MEDIA_URL = env("MEDIA_URL")
STATIC_URL = env("STATIC_URL")

if env("AWS_S3_ENABLED"):
    AWS_S3_CONFIG_OPTIONS = {
        "endpoint_url": env("AWS_S3_ENDPOINT_URL"),
        "access_key": env("AWS_S3_ACCESS_KEY_ID"),
        "secret_key": env("AWS_S3_SECRET_ACCESS_KEY"),
        "region_name": env("AWS_S3_REGION_NAME"),
    }

    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                **AWS_S3_CONFIG_OPTIONS,
                "bucket_name": env("AWS_S3_MEDIA_BUCKET_NAME"),
                "querystring_auth": False,
                "location": "media/",
                "file_overwrite": False,
            },
        },
        "staticfiles": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                **AWS_S3_CONFIG_OPTIONS,
                "bucket_name": env("AWS_S3_STATIC_BUCKET_NAME"),
                "querystring_auth": False,
                "location": "static/",
                "file_overwrite": True,
            },
        },
    }

else:
    # Filesystem
    MEDIA_ROOT = env("MEDIA_ROOT")
    STATIC_ROOT = env("STATIC_ROOT")


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

PREMAILER_OPTIONS = dict(
    disable_validation=not DEBUG,  # Enable validation in DEBUG only
)

HEALTHCHECK_CACHE_KEY = "rc_select_healthcheck_key"

# Security Header configuration

TRUSTED_ORIGINS = [
    APP_DOMAIN.geturl(),
    FRONTEND_DOMAIN.geturl(),
    *env("ADDITIONAL_TRUSTED_ORIGINS"),
]

SESSION_COOKIE_NAME = f"RC-SELECT-{APP_ENVIRONMENT}-SESSIONID"
CSRF_COOKIE_NAME = f"RC-SELECT-{APP_ENVIRONMENT}-CSRFTOKEN"
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
CSP_DEFAULT_SRC = ["'self'"]
SECURE_REFERRER_POLICY = "same-origin"
if APP_DOMAIN.scheme == "https":
    SESSION_COOKIE_NAME = f"__Secure-{SESSION_COOKIE_NAME}"
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SECURE_HSTS_SECONDS = 30  # TODO: Increase this slowly
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    CSRF_TRUSTED_ORIGINS = TRUSTED_ORIGINS

# -- https://docs.djangoproject.com/en/3.2/ref/settings/#std:setting-SESSION_COOKIE_DOMAIN
SESSION_COOKIE_DOMAIN = env("SESSION_COOKIE_DOMAIN")
# https://docs.djangoproject.com/en/3.2/ref/settings/#csrf-cookie-domain
CSRF_COOKIE_DOMAIN = env("CSRF_COOKIE_DOMAIN")


# CORS
CORS_ALLOWED_ORIGINS = TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS = TRUSTED_ORIGINS

CORS_ALLOW_CREDENTIALS = True
CORS_URLS_REGEX = r"(^/media/.*$)|(^/graphql/$)|(^/health-check/$)|(^/captcha/.*$)"
CORS_ALLOW_METHODS = (
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
)

CORS_ALLOW_HEADERS = (
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
)

# Strawberry
STRAWBERRY_DJANGO = {
    "FIELD_DESCRIPTION_FROM_HELP_TEXT": True,
    "TYPE_DESCRIPTION_FROM_MODEL_DOCSTRING": True,
    "MUTATIONS_DEFAULT_HANDLE_ERRORS": True,
    "PAGINATION_DEFAULT_LIMIT": 20,
    "DEFAULT_PK_FIELD_NAME": "id",
}
# Email
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
EMAIL_API_URL = env("EMAIL_API_URL")
EMAIL_API_KEY = env("EMAIL_API_KEY")
EMAIL_API_TIMEOUT = env("EMAIL_API_TIMEOUT", default=30)
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_USE_TLS = env("EMAIL_USE_TLS")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
EMAIL_TO = env("EMAIL_TO")

# Celery
CELERY_REDIS_URL = env("CELERY_REDIS_URL")
CACHE_REDIS_URL = env("CACHE_REDIS_URL")
CELERY_BROKER_URL = CELERY_REDIS_URL
CELERY_RESULT_BACKEND = CELERY_REDIS_URL
