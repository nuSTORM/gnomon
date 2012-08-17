tar xvf geant4.9.5.tar.gz
mv geant4.9.5 $VIRTUAL_ENV/src/
cd $VIRTUAL_ENV/src/
mkdir geant4.9.5-build
cd geant4.9.5-build
cmake -DCMAKE_INSTALL_PREFIX=$VIRTUAL_ENV -DGEANT4_INSTALL_DATA=True -DGEANT4_USE_OPENGL_X11:BOOL=ON -DGEANT4_USE_GDML:BOOL=ON ../geant4.9.5
make install

source $VIRTUAL_ENV/src/geant4.9.5-build/geant4make.sh
echo source \$VIRTUAL_ENV/src/geant4.9.5-build/geant4make.sh >> $VIRTUAL_ENV/bin/activate
