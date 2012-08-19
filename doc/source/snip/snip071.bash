cd $VIRTUAL_ENV/src/
mkdir pythia6
cd pythia6
wget http://genie.hepforge.org/svn/trunk/src/scripts/build/ext/build_pythia6.sh
chmod +x build_pythia6.sh
./build_pythia6.sh
