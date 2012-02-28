How to regenerate these documents
=================================


``ln -s /Users/tunnell/env/gnomon/src/gnomon.bitbucket.org html``

``PYTHONPATH=$PYTHONPATH:/Users/tunnell/env/gnomon/src/gnomon make html``

``cd build/html; hg add *; hg commit; hg push``