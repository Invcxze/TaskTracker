import os
import sys
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

from django.conf import settings
if not settings.configured:
    import django
    django.setup()

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass