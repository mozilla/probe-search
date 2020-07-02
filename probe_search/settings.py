"""
Django settings for probe_search project.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""
import os

from configurations import Configuration, values


class Base(Configuration):

    # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    INSTALLED_APPS = [
        "django.contrib.contenttypes",
        "probes",
    ]
    MIDDLEWARE = []
    ALLOWED_HOSTS = []

    SECRET_KEY = values.SecretValue()

    ROOT_URLCONF = "probe_search.urls"

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
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

    DEBUG = values.BooleanValue(default=False)
    LANGUAGE_CODE = "en-us"
    TIME_ZONE = "UTC"
    USE_I18N = False
    USE_L10N = False
    USE_TZ = True


class Local(Base):

    DATABASES = values.DatabaseURLValue("postgres://postgres:pass@db/postgres")
    DEBUG = True
