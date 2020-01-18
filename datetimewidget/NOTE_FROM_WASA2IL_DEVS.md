# Notes on this directory from Wasa2il developers

This code was copied from:

    https://github.com/cjsoftuk/django-datetime-widget

This package is a fork of the original django-datetime-widget, which can be found here:

    https://github.com/asaglimbeni/django-datetime-widget

The latter can be found via `pip` as the package `django-datetime-widget`.

The problem with the original widget is that it has been unmaintained since the spring of 2015 and the author does not seem to accept push requests from other users who are willing and able to provide fixes. As a result, the original package breaks at Django 2.1 and later. The package we've copied (from `cjsoftuk`) is identical to the original package except that it has been fixed to work with Django 2.1 and later.

Now, a proper fix would be to stop using `datetimewidget` altogether and find something which is still maintained. However, at the time of this writing we are still using Bootstrap 3.x, whereas an upgrade to Bootstrap 4.x is being worked on, and may even be complete as a pull request that needs verification and approval.

For this reason, we'll temporarily keep this code copied here in the project directory itself, until a more permanent solution is found to our datetime-widget needs. A good time to replace `django-datetime-widget` with something else, is when the Bootstrap 4.x upgrade has been complete.

At that point in time, this directory should be removed in favor of whatever will be used instead.

