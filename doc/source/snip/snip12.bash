cd $VIRTUAL_ENV/src
svn co --non-interactive --trust-server-cert https://genie.hepforge.org/svn/trunk genie
cd genie

echo export GENIE=\$VIRTUAL_ENV/src/genie >> $VIRTUAL_ENV/bin/activate
echo export PYTHIA6=\$VIRTUAL_ENV/src/pythia6/v6_424/lib >> $VIRTUAL_ENV/bin/activate
echo export LHAPDF=\${GENIE}/v5_8_8/stage >> $VIRTUAL_ENV/bin/activate
echo export PATH=\$PATH:\${LHAPDF}/bin >> $VIRTUAL_ENV/bin/activate
echo export PYTHONPATH=\$PYTHONPATH:\${LHAPDF}/lib/python2.6/site-packages/ >> $VIRTUAL_ENV/bin/activate
echo export LHAPATH=\`lhapdf-config --pdfsets-path\` >> $VIRTUAL_ENV/bin/activate
echo export LLP=LD_LIBRARY_PATH >> $VIRTUAL_ENV/bin/activate
echo eval \${LLP}=\${!LLP}:\${LHAPDF}/lib:\${GENIE}/lib:\${PYTHIA6}:/opt/local/lib >> $VIRTUAL_ENV/bin/activate

source $VIRTUAL_ENV/bin/activate

./src/scripts/build/ext/build_lhapdf.sh 5.8.8 --refetch

source $VIRTUAL_ENV/bin/activate

./configure --with-lhapdf-lib=$LHAPDF/lib --with-lhapdf-inc=$LHAPDF/include --prefix=$VIRTUAL_ENV

make install
