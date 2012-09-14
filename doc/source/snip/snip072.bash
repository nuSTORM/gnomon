cd $VIRTUAL_ENV
tar xvf root_v5.34.00.source.tar.gz
mv root $VIRTUAL_ENV/src/root-5.34.00
cd $VIRTUAL_ENV/src/root-5.34.00
./configure ${EXTRAS} --with-pythia6-libdir=../pythia6/v6_424/lib --enable-gdml
make
