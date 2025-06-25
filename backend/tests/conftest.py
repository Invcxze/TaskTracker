import os
import sys
import pytest
from django.conf import settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.config.settings.local")

if not settings.configured:
    from django import setup
    setup()

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass

