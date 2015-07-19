__author__ = 'johann'

import subprocess
import fileinput
import shutil

import random
random = random.SystemRandom()


def get_random_string(length=12,
                      allowed_chars='abcdefghijklmnopqrstuvwxyz'
                                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    """
    Returns a securely generated random string.

    The default length of 12 with the a-z, A-Z, 0-9 character set returns
    a 71-bit value. log_2((26+26+10)^12) =~ 71 bits.

    Taken from the django.utils.crypto module.
    """
    return ''.join(random.choice(allowed_chars) for i in range(length))


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
subprocess.call("pip install --upgrade -r requirements.txt")

print "Create local settings"
print "-" * 40
shutil.copy("wasa2il/local_settings_sqlite3.py", "wasa2il/local_settings.py")

print "Generate random key and inject to local_settings.py"
print "-" * 40
secretKeyLine = "SECRET_KEY = ''"
for line in fileinput.input('wasa2il/local_settings.py', inplace=1):
    if line.startswith(secretKeyLine):
        print 'SECRET_KEY = \'', get_secret_key(), '\''
    else:
        print line.strip()

print "Creating the database for use"
print "-" * 40
subprocess.call('python wasa2il\manage.py migrate')

print "Move the test file to it's proper location"
print "-" * 40
shutil.move("test", "wasa2il/test")

print "*" * 40
print "Done, to run wasa2il, go to the wasa2il subfolder and type 'python manage.py runserver'"
print "*" * 40


