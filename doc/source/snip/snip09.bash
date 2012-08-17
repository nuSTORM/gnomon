tar xvf xerces-c-3.1.1.tar.gz
mv xerces-c-3.1.1 $VIRTUAL_ENV/src/
cd $VIRTUAL_ENV/src/xerces-c-3.1.1
./configure --prefix=$VIRTUAL_ENV
make install
