Wasa2il on Vagrant machines
===========================

This directory contains Vagrant virtual machine definitions that should be able
to boot up and run the code without problems.

These are here to better make sure that the code runs in various environments, and
to figure out which system packages may be required to get the project running.

All that should be needed is a working Vagrant setup locally (usually backed up by
VirtualBox, or VMWare, or similar), and then you should be able to go into any of
the subdirectories and run `vagrant up` and `vagrant ssh`, naviate to `/app` and run `make test` or `make run` for example.
