#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from unittest import mock
from djongo.base import DatabaseWrapper

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dusty_shelf.settings')
    
    try:
        # If the test command is being run, mock the close method for DatabaseWrapper
        if 'test' in sys.argv:
            with mock.patch.object(DatabaseWrapper, 'close', return_value=None):
                from django.core.management import execute_from_command_line
                execute_from_command_line(sys.argv)
        else:
            from django.core.management import execute_from_command_line
            execute_from_command_line(sys.argv)
    
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc


if __name__ == '__main__':
    main()