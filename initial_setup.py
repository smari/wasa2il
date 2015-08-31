#!/usr/bin/env python
__author__ = 'johann'

import os
import subprocess
import fileinput
import shutil
from django.utils.crypto import get_random_string


def get_secret_key():
    """
    Create a random secret key.

    Taken from the Django project.
    """
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return get_random_string(50, chars)

print "*" * 40
print "Initializing and settings up Wasa2il to use sqlite3 with a filebased db called test"
print "This script assumes that pip, git & python are installed"
print "*" * 40

print "Ensure everything is installed and updated"
print "-" * 40
subprocess.call(["pip", "install", "--upgrade", "-r", "requirements.txt"])

print "Create local settings"
print "-" * 40
shutil.copy("wasa2il/local_settings.py-example", "wasa2il/local_settings.py")

print "Inject random key and database settings into local_settings.py"
print "-" * 40
for line in fileinput.input('wasa2il/local_settings.py', inplace=1):
    if line.startswith("SECRET_KEY"):
        print 'SECRET_KEY = \'', get_secret_key(), '\''
    elif line.startswith("DATABASE_ENGINE"):
        print "DATABASE_ENGINE = 'django.db.backends.sqlite3'"
    elif line.startswith("DATABASE_NAME"):
        print "DATABASE_NAME = 'test'"
    else:
        print line.strip()

print "Creating the database for use"
print "-" * 40
subprocess.call(['python', os.path.join(os.getcwd(), 'wasa2il', 'manage.py'), 'migrate'])

print "Move the test file to it's proper location"
print "-" * 40
shutil.move("test", "wasa2il/test")

print "Update database"
print "-" * 40
subprocess.call(['python', os.path.join(os.getcwd(), 'wasa2il', 'manage.py'), 'migrate'])

print "*" * 40
print "Done, to run wasa2il, go to the wasa2il subfolder and type 'python manage.py runserver'"
print "*" * 40
