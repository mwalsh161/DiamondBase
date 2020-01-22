#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DiamondBase.settings")

    from django.core.management import execute_from_command_line
    sys.path.append('/var/www/DiamondBase/sample_database')

    execute_from_command_line(sys.argv)
