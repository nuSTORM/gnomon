export GEANT_PREFIX=`geant4-config --prefix`
export PYTHON_PREFIX=${HOME}/.cache/0install.net/implementations/sha1new=4acc3af86d4a7c72a006c4de96b99e1baec66525

export XD=/Users/tunnell/.cache/0install.net/implementations/sha1new=7b74a95224b4470762beb7f4de4a3a14a021e47d

./configure macosx --with-g4-libdir=${GEANT_PREFIX}/lib --with-clhep-incdir=`clhep-config --prefix`/include --with-clhep-libdir=`clhep-config --prefix`/lib/ --with-boost-incdir=/opt/local/include --with-boost-libdir=/opt/local/lib --with-g4-incdir=${GEANT_PREFIX}/include/Geant4 --with-xercesc-incdir=${XD}/include --with-xercesc-libdir=${XD}/lib --with-python-incdir=${PYTHON_PREFIX}/include/python3.2m --with-python-libdir=${PYTHON_PREFIX}/lib/python3.2 --with-python3