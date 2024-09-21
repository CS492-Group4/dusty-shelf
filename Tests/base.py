# tests/base.py

from django.test import TestCase

class NoDbTestCase(TestCase):
    def _post_teardown(self):
        # Bypass database connection close during test teardown
        try:
            super()._post_teardown()
        except NotImplementedError:
            pass
