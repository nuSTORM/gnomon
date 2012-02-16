Frequently Asked Questions
=====================================


On a Mac, I get "Fatal Python Error: PyThreadState"?!
-----------------------------------------------------------------

This obscure error means that you somehow mixed python versions.  Make sure that you create your virtual environment with the ``virtualenv -p my_python_version`` where you tell it to clone the correct python version.  This should agree with the version that's selected in ``sudo port select --list python``.

Does Python 3 work?
----------------------

Currently it's not supported.  If you can get it working, notify the developers where your branch and it can be included.  However, initial attempts at getting ROOT, g4py, and Python 3 to work together were less than successful.  Use the arguments for specifying g4py's include and library locations.