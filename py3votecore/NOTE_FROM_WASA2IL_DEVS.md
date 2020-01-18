# Notes on this directory from Wasa2il developers

The original package of python-vote-core is at:

    https://github.com/bradbeattie/python-vote-core/

This is the package which is available as `python-vote-full` in the `pip` repository. It is only compatible with Python 2.x and its author no longer maintains it.

Another author upgraded the package to work with Python 3, which is located here:

    https://github.com/the-maldridge/python-vote-core

However, this package is not available in the `pip` repository at the time of this writing (2019-07-24).

For this reason, the directory `py3votecore` has been copied to this project without any modifications. **Please do not make Wasa2il-specific modifications to the code in this directory, because we need it compatible with future versions of `py3votecore`.** Hopefully one day a version that is compatible with Python 3 will become available in the `pip` repository, at which point this directory should be removed and the package name (whatever it will be) added to `requirements.txt`.
