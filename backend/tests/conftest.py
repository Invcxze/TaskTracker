
from django.conf import settings
import os
import sys
import pytest

from django_elasticsearch_dsl.registries import registry
from django_elasticsearch_dsl.signals import BaseSignalProcessor

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

if not settings.configured:
    import django
    django.setup()

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass
@pytest.fixture(scope="session", autouse=True)
def disable_es_signals():
    registry.signal_processor = BaseSignalProcessor(registry)