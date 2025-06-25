from .base import *

import os

DEBUG = os.getenv("DEBUG", "False") == "True"
SECRET_KEY = os.getenv("SECRET_KEY", "dummy-secret-key")

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost").split(",")

DATABASES = {
    'default': {
        'ENGINE': os.getenv("DB_ENGINE", 'django.db.backends.postgresql'),
        'NAME': os.getenv("DB_NAME", 'mydb'),
        'USER': os.getenv("DB_USER", 'myuser'),
        'PASSWORD': os.getenv("DB_PASSWORD", 'mypassword'),
        'HOST': os.getenv("DB_HOST", 'localhost'),
        'PORT': os.getenv("DB_PORT", '5432'),
    }
}