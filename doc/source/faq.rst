Frequently Asked Questions
=====================================

On a Mac, I get "Fatal Python Error: PyThreadState"?!
-----------------------------------------------------

This obscure error means that you somehow mixed python versions.  Make sure that you create your virtual environment with the ``virtualenv -p my_python_version`` where you tell it to clone the correct python version.  This should agree with the version that's selected in ``sudo port select --list python``.

How do I check my CMake version?
--------------------------------

Run the command ``cmake --version``.

How do I upgrade my CMake version?
----------------------------------

You can download CMake from their `download page <http://cmake.org/cmake/resources/software.html>`_ or you can use your package manager.  Worst case: discuss with your system administrator and tell them how many years old your version of CMake is.

You can also build CMake much like Xerces C++ is built in the installation instructions to install it in your virtual environment.

Does Python 3.X work?
----------------------

Currently it's not supported.  If you can get it working, notify the developers where your branch and it can be included.  However, initial attempts in January 2012 at getting ROOT, g4py, and Python 3 to work together were less than successful.

How do I check my Python version
--------------------------------

Run the command ``python --version``.

Install Numpy and Scipy on Mac Lion
-----------------------------------

As of the 8th of March, 2012, you have to branch the git repositories.  Make sure an install of either doesn't already exist since they have to be in sync.

I also had to do ``swig install swig swig-python`` and (ugly-ly) install umfpack with HomeBrew.

How do I change my Python version?
----------------------------------

Normally one should ask the systems administrator to get you the required version.  Many distributions ship with old versions of Python, so this should be a reasonable request.

However, this may not be straightforward for one reason or another.  One should search online for how to install Python in user-space.  For reference, the commands to do this are shown but it may be different for your machine::

  mkdir ~/gnomon
  cd ~/gnomon
  export GNOMON_DIR=`pwd`
  mkdir local
  wget http://python.org/ftp/python/2.7.2/Python-2.7.2.tgz
  tar xvfz Python-2.7.2.tgz
  cd Python-2.7.2
  ./configure --prefix=$GNOMON_DIR/local --enable-shared CXXFLAGS="-fPIC" CFLAGS="-fPIC"
  make install
  export PATH=$GNOMON_DIR/local/bin:$PATH
  export LD_LIBRARY_PATH=$GNOMON_DIR/local/lib:$LD_LIBRARY_PATH
  cd ..
  wget http://pypi.python.org/packages/2.7/s/setuptools/setuptools-0.6c11-py2.7.egg
  sh setuptools-0.6c11-py2.7.egg
  # now you have easy_install
  easy_install virtualenv
  cd
  virtualenv -p `which python` $HOME/env/gnomon
  cd $HOME/env/gnomon
  export EXTRAS="--with-python-incdir=/home/tunnell/gnomon/local/include/python2.7 --with-python-libdir=/home/tunnell/gnomon/local/lib"


Why is the test coverage of Geant4 interfaces poor?
---------------------------------------------------

Hard to instantiate.  Geant4 isn't modular enough.

How do I get git
----------------

It should be provided by your system adminstrator.  The program is common in particle physics code development and, for
example, is supported by Fermilab.

If your system administrator refuses, then you can always try to use the program `mercurial` with the hg-git extension.
This can be done by running the following within a Python virtualenv environment::

  easy_install mercurial hg-git

Then adding the following to `~/.hgrc`::

  [extensions]
  hgext.bookmarks =
  convert =
  hggit =