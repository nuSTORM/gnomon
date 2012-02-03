#export GEANT_PREFIX=`geant4-config --prefix`
export GEANT_PREFIX=/Users/tunnell/work/Geant4-9.5.0-Darwin

export XD=/Users/tunnell/.cache/0install.net/implementations/sha1new=3467d45bed1905bf61e6f7fa6ec72d3dbcd47b02/include

./configure macosx --with-g4-libdir=${GEANT_PREFIX}/lib --with-clhep-incdir=`clhep-config --prefix`/include --with-clhep-libdir=`clhep-config --prefix`/lib/ --with-boost-incdir=/opt/local/include --with-boost-libdir=/opt/local/lib --with-g4-incdir=${GEANT_PREFIX}/include/Geant4 --with-xercesc-incdir=${XD} --with-xercesc-libdir=${XD}/../lib