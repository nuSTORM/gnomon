Installation
============

Software Prerequisites
----------------------

Gnomon and its dependencies depends on several software packages:

* Python 2.7.X
* Boost::Python
* CMake >= 2.8 (for Geant4 fetching data)
* Matplotlib
* xerces C++ 3.1.1 (for GDML)
* GEANT4.9.5
* g4py
* ROOT 5.32

For development, we also recommend:

* nose (to run unit tests)
* coverage (to measure the source coverage of the tests)
* pylint (to check for common problems in Python code)
* sphinx 1.1 dev or later (to generate the documentation with mathjax support)

We will explain how to install all of these packages in the following section.

Step-by-Step Installation
---------------------------------------

Although Gnomon can run on any Linux distribution or Mac OS X, we recommend the
use of Ubuntu 11.10 or Mac OS X for Gnomon testing and development.  For these
instructions, we will assume you are starting with a fresh Ubuntu 11.10 or fresh
Mac OS X 10.7.3 installation.  Notes about using Scientific Linux can be found
in the :doc:`faq`.

Steps 1 will require root privileges, but the remaining steps will be done in
your home directory without administrator intervention.


Step 1: Prerequisites
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This step is where the installation instructions diverge depending on which
operating system you are using.  Please find your package manager and
distribution below.  If you do not see your distribution, then please notify
the developers if you are successful in installing gnomon on your unsupported
distribution and any changes to the instructions you had to make.

``apt-get`` packages from Ubuntu package manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Many packages are required to setup your build environment to compile
GEANT4 and ROOT.  Fortunately, they can be installed with one very
long ``apt-get`` line.  Although this line may wrap in your browser,
it should be executed as one line::

  sudo apt-get install build-essential xorg-dev python-dev \
       python-virtualenv python-numpy python-pygame libglu1-mesa-dev \
       glutg3-dev cmake uuid-dev liblapack-dev mercurial \
       libboost-all-dev libatlas-base-dev

To be able to generate the documentation, we also need these tools::

  sudo apt-get install texlive dvipng


``port`` packages from MacPorts package manager OS X
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Macports is one possible package manager for OS X and the one that will be
assumed for these instructions.  Instructions are provided at the Macports
website http://guide.macports.org/.  It is assumed that the versions of your
software are::

* Mac OS X >=10.7.3
* Xcode >=4.3.1
* MacPorts >=2.0.4 (requires Xcode)

If you do not have MacPorts, then you must ensure Xcode is installed before you
are able to install MacPorts.  Xcode is available through the AppStore but it is
also required to go into the Xcode preferences, select the Downloads tab, and
ensure that the "Command Line Tools" component is installed.  This is all
outlined in the MacPorts installation guide which is referenced above.

Next we must run the following commands::

     sudo port install wget
     sudo port install cmake
     sudo port install boost +python27
     sudo port select --set python python27
     sudo easy_install sphinx
     sudo port install mercurial
     sudo port install py27-tkinter
     sudo easy_install virtualenv
     export EXTRAS="--with-python-incdir=$VIRTUAL_ENV/include/python2.7 --with-python-libdir=$VIRTUAL_ENV/lib"

``yum`` packages from the Redhat based distributions (SL5)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Unsupported**.  Command dump::

  yum install mercurial

See :doc:`faq` about how to change the Python version in userspace.

Step 2: virtualenv
^^^^^^^^^^^^^^^^^^

The excellent `virtualenv <http://www.virtualenv.org/>`_ tool
allows you to create an isolated Python environment, independent from
your system environment. We will keep all of the python modules for
Gnomon (with a few exceptions) and libraries compiled from source
inside of a virtualenv in your ``$HOME`` directory::

  virtualenv -p `which python` $HOME/env/gnomon
  cd $HOME/env/gnomon

You'll want to find the Python shared library associated with the installation referneced above with ``which python`` and make a symbolic link in $HOME/env/gnomon/lib.  This can be done on a Mac by doing, for example, ``ln -s /opt/local/lib/libpython2.7.dylib $VIRTUAL_ENV/lib`` if the shared library lives in ``/opt/``.  Or in the Scientific Linux case above: ``ln -s ~/gnomon/local/lib/libpython2.7.so.1.0 $VIRTUAL_ENV/lib``

Next, append the following lines to the end of ``$HOME/env/gnomon/bin/activate`` to allow codes to see locally installed libraries::

  # For Macs: Change LD_LIBRARY_PATH -> DYLD_LIBRARY_PATH
  export LD_LIBRARY_PATH=$VIRTUAL_ENV/lib:$LD_LIBRARY_PATH
  export PYTHONPATH=$VIRTUAL_ENV/lib:$PYTHONPATH
  
  # For Macs, uncomment this line:
  #export EXTRAS="--with-python-incdir=$VIRTUAL_ENV/include/python2.7 --with-python-libdir=$VIRTUAL_ENV/lib"

Finally, we can enable the virtual environment::

  source $HOME/env/gnomon/bin/activate

This will put the appropriate version of python in the path and also
set the ``$VIRTUAL_ENV`` environment variable we will use in the
remainder of the directions.

And create a directory where all the source codes will go::

  mkdir $VIRTUAL_ENV/src/

where the instructions below will tell you where the files can be located.  At the time of writing, one should just be able to run the following commands to fetch some of the various files::

   wget ftp://root.cern.ch/root/root_v5.32.00.source.tar.gz
   wget http://mirror.ox.ac.uk/sites/rsync.apache.org/xerces/c/3/sources/xerces-c-3.1.1.tar.gz
   wget http://geant4.cern.ch/support/source/geant4.9.5.tar.gz

Lastly::

  easy_install couchdb
  easy_install nose # for running tests


Step 3: ROOT
^^^^^^^^^^^^

Gnomon uses the ROOT I/O system to record event information to disk
for access later.  In addition, we expect many Gnomon users will
want to use ROOT to analyze the output of Gnomon.

Begin by downloading the ROOT 5.32 tarball from `the ROOT download
page <http://root.cern.ch/drupal/content/production-version-532>`_.
As of this writing, the latest version is 5.32.00.  Then, from the
download directory, execute the following commands::

  tar xvf root_v5.32.00.source.tar.gz
  mv root $VIRTUAL_ENV/src/root-5.32.00
  cd $VIRTUAL_ENV/src/root-5.32.00
  ./configure ${EXTRAS}
  make

.. tip:: When running the command ``make`` above, one can multithread the build by doing ``make -jN`` for an N-core machine.  For example, in a four core laptop, one could do ``make -j4``.  This is true for all the ``make`` commands on this page.

We also need to append a ``source`` line to ``$VIRTUAL_ENV/bin/activate``::

  source $VIRTUAL_ENV/src/root-5.32.00/bin/thisroot.sh

to ensure that ROOT is setup when the environment is setup.

Step 4: xerces c++
^^^^^^^^^^^^^^^^^^

Gnomon uses xerces to help Geant4 with parsing XML that is
used in our GDML geometry representation.  Proceed to the `xerces
C++ download page <http://xerces.apache.org/xerces-c/download.cgi>`_
and get version 3.1.1.

Proceed to your download directory then run the following commands::

  tar xvf xerces-c-3.1.1.tar.gz
  mv xerces-c-3.1.1 $VIRTUAL_ENV/src/
  cd $VIRTUAL_ENV/src/xerces-c-3.1.1
  ./configure --prefix=$VIRTUAL_ENV
  make install


.. warning:: **Mac users:** xerces gets confused about the architecture.  It may be necessary to append ``CFLAGS="-arch x86_64" CXXFLAGS="-arch x86_64"`` to the configure command.  This is only relevant if the output of `./configure` does not agree with the output of `uname -m`.


Step 5: GEANT4
^^^^^^^^^^^^^^

Gnomon uses GEANT4 to model particle interactions with matter. These
instructions describe how to compile GEANT4 using the new CMake-based
build system.  As of GEANT4.9.5, CLHEP is shipped within GEANT4 along
with various data files which means it is no longer necessary to download
these on one's own.
  
Now go to the `GEANT4 Download Page <http://geant4.cern.ch/support/download.shtml>`_ and download the source code.

Next go to your download directory and run the following commands::

  tar xvf geant4.9.5.tar.gz
  mv geant4.9.5 $VIRTUAL_ENV/src/
  cd $VIRTUAL_ENV/src/
  mkdir geant4.9.5-build
  cd geant4.9.5-build
  cmake -DCMAKE_INSTALL_PREFIX=$VIRTUAL_ENV -DGEANT4_INSTALL_DATA=True -DGEANT4_USE_OPENGL_X11:BOOL=ON -DGEANT4_USE_GDML:BOOL=ON ../geant4.9.5
  make install


Step 6: g4py
^^^^^^^^^^^^

To access GEANT4 from Python, Gnomon uses the g4py wrappers.  We have
had to fix a few bugs and add wrapper a few additional classes for
Gnomon, so for now you will need to use our fork of g4py::

  cd $VIRTUAL_ENV/src
  hg clone https://bitbucket.org/gnomon/g4py
  cd g4py

  export G4FLAGS="--with-g4-incdir=$VIRTUAL_ENV/include/Geant4 --with-g4-libdir=$VIRTUAL_ENV/lib"
  export XERCESFLAGS="--with-xercesc-incdir=$VIRTUAL_ENV/include --with-xercesc-libdir=$VIRTUAL_ENV/lib"
  export BOOSTFLAGS="--with-boost-libdir=/usr/lib"

  # Mac OS X users need to uncomment this line below:
  #export BOOSTFLAGS="--with-boost-incdir=/opt/local/include --with-boost-libdir=/opt/local/lib"

  # select system name from linux, linux64, macosx as appropriate
  ./configure linux64 ${G4FLAGS} ${XERCESFLAGS} ${BOOSTFLAGS} --prefix=$VIRTUAL_ENV ${EXTRAS}
  make
  make install

.. caution:: If one is not careful and the python headers g4py finds, python libraries g4py finds, and python executable used to import g4py are not of the same version, then very obscure fatal errors will arise.  This is the purpose of the ``${EXTRAS}`` flag.

Now you can enable the Gnomon environment whenever you want by typing
``source $HOME/env/gnomon/bin/activate``, or by placing that line in the
``.bashrc`` login script.

Step 7: gnomon
^^^^^^^^^^^^^^

Now you are ready to get gnomon.  One can currently work only from the developer's version.  To get the code, run::

  cd $VIRTUAL_ENV/src
  hg clone https://bitbucket.org/gnomon/gnomon
  cd gnomon

There is no installation for the actual gnomon code since it's written in an interpreted language (i.e. python).  In order to tell Python where to look for gnomon, you must append ``$VIRTUAL_ENV/bin/activate`` with the following::

  export PYTHONPATH=$VIRTUAL_ENV/src/gnomon/gnomon:$PYTHONPATH

Then you are ready to move to the tutorial.