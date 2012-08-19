cd $VIRTUAL_ENV/src
hg clone https://bitbucket.org/gnomon/g4py
cd g4py

export G4FLAGS="--with-g4-incdir=$VIRTUAL_ENV/include/Geant4 --with-g4-libdir=$VIRTUAL_ENV/lib"
export XERCESFLAGS="--with-xercesc-incdir=$VIRTUAL_ENV/include --with-xercesc-libdir=$VIRTUAL_ENV/lib"
export BOOSTFLAGS="--with-boost-libdir=/usr/lib"

# Mac OS X users need to uncomment this line below:
#export BOOSTFLAGS="--with-boost-incdir=/opt/local/include --with-boost-libdir=/opt/local/lib"

# select system name from linux, linux64, macosx as appropriate
./configure linux64 ${G4FLAGS} ${XERCESFLAGS} ${BOOSTFLAGS} --prefix=$VIRTUAL_ENV ${EXTRAS} --with-python-incdir=$VIRTUAL_ENV/include/python2.7 --with-python-libdir=$VIRTUAL_ENV/lib
make
make install

source $HOME/env/gnomon/bin/activate
