tar xvf root_v5.32.00.source.tar.gz
mv root $VIRTUAL_ENV/src/root-5.32.00
cd $VIRTUAL_ENV/src/root-5.32.00
./configure ${EXTRAS}
make
