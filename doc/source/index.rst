Gnomon: NuSTORM Detector Simulation
===================================

This softare is intended for people within the NuSTORM collaboration in order to simulate the response of magentized
iron sampling calorimter within nuSTORM.


The nuSTORM experiment
----------------------

nuSTORM is an entry-level muon storage ring intended to produce flavor pure beams of muon neutrinos and electron
antineutrinos (or electron neutrinos and muon antineutrinos when mu-minus are stored). When paired with a magnetized
detector at short baseline (1 to 2 km), nuSTORM is intended to make a definitive measurement on the presence or absence
of an LSND/MiniBooNE type sterile neutrino. Near detectors in the nuSTORM beam could be used to make very clean, high
statistics measurements of both electron and muon neutrino cross sections.

The Letter Of Intent (LOI) that was submit to Fermilab is available here:

  http://arxiv.org/abs/1206.0294

Development
-----------

Gnomon is under heavy development.  Tagged releases will happen soon,
but in the meantime we encourage people to obtain the code directly
from the git repository hosted at github:

  https://github.com/nuSTORM/gnomon

Various services are used to aid in development.  For example, readthedocs.org hosts our documentation:

  http://gnomon.readthedocs.org/

It is currently planned that all the project management will be done within the github project's issue tracker.

There are plans for using Jenkins for continous integration but we use nothing at the moment.  There are tests that can
be run with `nose`.

There is currently no mailing list so please email the authors directly.

User Documentation
------------------


.. toctree::
   :maxdepth: 2

   install
   createproc
   gnomon.processors
   faq
   cheat

Developer Documentation
-----------------------

.. toctree::
   :maxdepth: 2

   gnomon
   genie


Support and Author list
-----------------------

For support, please contact the authors until there is a mailing list.  For general queries, contact Christopher
Tunnell.

Gnomon was developed by the following people (alphabetically):

.. include:: ../../AUTHORS

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

