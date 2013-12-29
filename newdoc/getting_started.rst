Gettings Started
================

This section will detail how to get the development environment up and running.

.. note::
    Since this project blah blah

Getting wasa2il from source
----------------------

You will need to have Git versioning control software installed on your machine

Cloning wasa2il
~~~~~~~~~~~~~~~

To get the most recent development version of the source issuing the following command.

::

    prompt> git clone https://github.com/piratar/wasa2il.git

.. hint::
    The project and code directories share the same name, wasa2il.
    To avoid confusion it is recommanded to rename the project directory.

Initialize submodules
~~~~~~~~~~~~~~~~~~~~~

wasa2il requires a 3rd party library called OpenSTV.
OpenSTV git repository is configured as submodules to wasa2il
To get git to fetch this project run:

::

    prompt> git submodule update --init

This will fetch the libraries project and place it in ``lib/submodules/openSTV``

.. warning::
    This library can't be imported by default. It needs to be on the
    python path.

    .. note::
        A simple workaround is to place a symlink to it's code. From the project directory run:

        ::

            prompt> ln -s lib/submodules/openSTV/SourceCode/OpenSTV-1.6/openstv

.. note::
    wasa2il uses a OpenSTV 1.6 fork since later versions are not free.

.. todo::
    Change submodule configuration to make OpenSTV available by default.


Installing required libraries
-----------------------------

In the project directory there is a file called ``requirements.txt``.
It containes all the standard libraries wasa2il needs to run.
The content of the file is:

.. literalinclude:: ../requirements.txt

These library packages can easily be installed using:

::

    pip install -r requirements.txt

.. warning::
    This will replace a django installation of a different version (1.4)

.. warning::
    This step might fail if you don't have build tools and the python dev package install.

.. note::
    It is recommanded to use a virtual enviroment for development.


Additional development packages
-------------------------------

Documentation
~~~~~~~~~~~~~

The documenation of this project uses Sphinx.
To be able to build the documentation from its reStructuredText
files Sphinx needs to be installed

::

    pip install sphinx

.. todo::
    Add Testing to Additional development libraries

Initial wasa2il configuration
-----------------------------

When you reach this point you should have all
the code and it's dependancies installed.

Enviromental variables
~~~~~~~~~~~~~~~~~~~~~~

For everything to work correctly you will need to set some
enviromental variables.

PYTHONPATH
    The path to the project directory needs to be in here.
DJANGO_SETTINGS_MODLUE
    This variable should be assigned ``wasa2il.settings``

Configuring local_settings
~~~~~~~~~~~~~~~~~~~~~~~~~~

Included in the source is an example file of local_settings.py
called local_settings.py-example that you can see here:

.. literalinclude:: ../wasa2il/local_settings.py-example

Make a copy of this file and call it ``local_settings.py``.

Change the database configuration to match your database
(if sqlite3 then only DATABASE_ENGINE and DATABASE_NAME needs to be defined).
Change the SECRET_KEY variable.
Thats all that is needed to get django running.

Creating initial database
~~~~~~~~~~~~~~~~~~~~~~~~~

To create the inital database you need to create the database
tables from the models of wasa2il and it's installed apps.
The command to run is:

::

  python manage.py syncdb

.. warning::
    If a superuser is created it will not have a
    UserProfile assoiated with it.
    To fix this you need to enter the shell

    ::

        python manage.py shell

    Retrieve the created user (it will have a primary key of 1)
    and add a :class:`~core.models.UserProfile` to it.

    ::

        from django.contrib.auth.models import User
        from core.models import UserProfile

        UserProfile(user=User.objects.get(pk=1)).save()

Collect static media
~~~~~~~~~~~~~~~~~~~~
