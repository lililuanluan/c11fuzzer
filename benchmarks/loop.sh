#!/bin/bash
rm rf*.json
rm C11FuzzerTmp*
set -e


ENVIRONMENT='-x1000000 -v3' # bug depth 2
CDSLIB="/home/vagrant/c11tester"


cd $CDSLIB
make
cd -
export LIBRARY_PATH=${CDSLIB} # link time (compile)

make clean
make
export LD_LIBRARY_PATH=${CDSLIB}

EXE=obj/loop

export C11TESTER=$ENVIRONMENT

time $EXE  #> $tmpfile