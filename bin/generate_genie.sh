export DATA_DIR=../data
export GSPLOAD=$DATA_DIR/xsec.xml

gevgen -p -14 -t 1000260560 -n 10000 -e 0.1,2.0 -f $DATA_DIR/flux_file_mu.dat  > /dev/null
gntpc -i gntp.0.ghep.root -o ntuple_nu_mu.root -f gst > /dev/null

gevgen -p 14 -t 1000260560 -n 10000 -e 0.1,2.0 -f $DATA_DIR/flux_file_e.dat  > /dev/null
gntpc -i gntp.0.ghep.root -o ntuple_nu_mu_bar.root -f gst > /dev/null

