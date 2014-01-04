"""
To get readthedocs.org to work with this project there needs to be a file
in the Django Project directory that can be loaded instead of the settings file.
This is needed since if settings.py is loaded after a git clone, it will throw
an exception because of a missing local_settings.py file. This will also allow
the documents to be built without the DJANGO_SETTINGS_MODULE environmental
variable being set.

"""
