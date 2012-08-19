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
use of Ubuntu Server 12.04 LTS or Mac OS X for Gnomon testing and development.  For these
instructions, we will assume you are starting with a fresh Ubuntu 12.04 or fresh
Mac OS X 10.7.3 installation.  Notes about using Scientific Linux can be found
in the :doc:`faq`.

Steps 1 will require root privileges, but the remaining steps will be done in
your home directory without administrator intervention.


Step 1: Prerequisites
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The installation instructions diverge depending on which
operating system you are using.  Please find your package manager and
distribution below.  If you do not see your distribution, then please notify
the developers if you are successful in installing gnomon on your unsupported
distribution and any changes to the instructions you had to make.

``apt-get`` packages from Ubuntu package manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Many packages are required to setup your build environment to compile
GEANT4 and ROOT.  Fortunately, they can be installed with one very
long ``apt-get`` line.  Although this line may wrap in your browser,
it should be executed as one line:

  .. literalinclude:: snip/snip00.bash
    :language: bash
    :linenos:

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
inside of a virtualenv in your ``$HOME`` directory:

.. literalinclude:: snip/snip01.bash
  :language: bash
  :linenos:

Where the last line setup the environment.


You'll want to find the Python shared library associated with the installation referneced above with ``which python`` and make a symbolic link in ``$HOME/env/gnomon/lib`` by running:

.. literalinclude:: snip/snip02.bash
  :language: bash
  :linenos:

Next, append the following lines to the end of ``$HOME/env/gnomon/bin/activate`` to allow codes to see locally installed libraries:

.. literalinclude:: snip/snip03.bash
  :language: bash
  :linenos:

This will put the appropriate version of python in the path and also
set the ``$VIRTUAL_ENV`` environment variable we will use in the
remainder of the directions.

And create a directory where all the source codes will go:

.. literalinclude:: snip/snip04.bash
  :language: bash
  :linenos:

where the instructions below will tell you where the files can be located.  At the time of writing, one should just be able to run the following commands to fetch some of the various files:

.. literalinclude:: snip/snip05.bash
  :language: bash
  :linenos:

Lastly:

.. literalinclude:: snip/snip06.bash
  :language: bash
  :linenos:


Step almost 3: Pythia6
^^^^^^^^^^^^^^^^^^^^^^


.. literalinclude:: snip/snip071.bash


Step 3: ROOT
^^^^^^^^^^^^

Gnomon uses the ROOT I/O system to record event information to disk
for access later.  In addition, we expect many Gnomon users will
want to use ROOT to analyze the output of Gnomon.

Begin by downloading the ROOT 5.32 tarball from `the ROOT download
page <http://root.cern.ch/drupal/content/production-version-532>`_.
As of this writing, the latest version is 5.32.00.  Then, from the
download directory, execute the following commands:

.. literalinclude:: snip/snip072.bash

.. tip:: When running the command ``make`` above, one can multithread the build by doing ``make -jN`` for an N-core machine.  For example, in a four core laptop, one could do ``make -j4``.  This is true for all the ``make`` commands on this page.

We also need to append a ``source`` line to ``$VIRTUAL_ENV/bin/activate`` and setup ROOT:

.. literalinclude:: snip/snip08.bash


Step 4: xerces c++
^^^^^^^^^^^^^^^^^^

Gnomon uses xerces to help Geant4 with parsing XML that is
used in our GDML geometry representation.  Proceed to the `xerces
C++ download page <http://xerces.apache.org/xerces-c/download.cgi>`_
and get version 3.1.1.

Proceed to your download directory then run the following commands:

.. literalinclude:: snip/snip09.bash

.. warning:: **Mac users:** xerces gets confused about the architecture.  It may be necessary to append ``CFLAGS="-arch x86_64" CXXFLAGS="-arch x86_64"`` to the configure command.  This is only relevant if the output of `./configure` does not agree with the output of `uname -m`.


Step 5: GEANT4
^^^^^^^^^^^^^^

Gnomon uses GEANT4 to model particle interactions with matter. These
instructions describe how to compile GEANT4 using the new CMake-based
build system.  As of GEANT4.9.5, CLHEP is shipped within GEANT4 along
with various data files which means it is no longer necessary to download
these on one's own.

Now go to the `GEANT4 Download Page <http://geant4.cern.ch/support/download.shtml>`_ and download the source code.

Next go to your download directory, run the following commands, and append to the ``activate`` script:

.. literalinclude:: snip/snip10.bash


Step 6: g4py
^^^^^^^^^^^^

To access GEANT4 from Python, Gnomon uses the g4py wrappers.  We have
had to fix a few bugs and add wrapper a few additional classes for
Gnomon, so for now you will need to use our fork of g4py:


.. literalinclude:: snip/snip11.bash

.. caution:: If one is not careful and the python headers g4py finds, python libraries g4py finds, and python executable used to import g4py are not of the same version, then very obscure fatal errors will arise.  This is the purpose of the ``${EXTRAS}`` flag.

Now you can enable the Gnomon environment whenever you want by typing
``source $HOME/env/gnomon/bin/activate``, or by placing that line in the
``.bashrc`` login script equivalent.


Genie
^^^^^^^^^^^^^^

Please install Genie per the directions on their `website <http://www.genie-mc.org/>`_.  At the time writing, only version 2.7.1 has been tested with gnomon.  However, there is no svn tag for this release so you might want to try the trunk.  The gnomon software will only expect a file in the GST file format so it should be independent of Genie version.

Install Genie:

.. literalinclude:: snip/snip12.bash



Step 7: gnomon
^^^^^^^^^^^^^^

Now you are ready to get gnomon.  One can currently work only from the developer's version.  To get the code, run::

.. literalinclude:: snip/snip13.bash

There is no installation for the actual gnomon code since it's written in an interpreted language (i.e. python).  In order to tell Python where to look for gnomon, you must append ``$VIRTUAL_ENV/bin/activate`` with the following::

.. literalinclude:: snip/snip14.bash

Then you are ready to move to the tutorial (or examples in the gnomon-analysis branch).
