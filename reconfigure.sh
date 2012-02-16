export GEANT_PREFIX=`geant4-config --prefix`
export PYTHON_PREFIX=$VIRTUAL_ENV

export XD=${XLIB}/..

./configure macosx --with-g4-libdir=${GEANT_PREFIX}/lib --with-clhep-incdir=`clhep-config --prefix`/include --with-clhep-libdir=`clhep-config --prefix`/lib/ --with-boost-incdir=/opt/local/include --with-boost-libdir=/opt/local/lib --with-g4-incdir=${GEANT_PREFIX}/include/Geant4 --with-xercesc-incdir=${XD}/include --with-xercesc-libdir=${XD}/lib --with-python-incdir=$VIRTUAL_ENV/include/python2.7/ --with-python-libdir=${PYTHON_PREFIX}/lib