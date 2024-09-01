#!/bin/bash


rm  C11FuzzerTmp*
set -e
make

ENVIRONMENT='-x100 -v3'
CDSLIB="/home/vagrant/c11tester"
cd $CDSLIB
make
cd -
export LIBRARY_PATH=${CDSLIB} 
make clean
make
export LD_LIBRARY_PATH=${CDSLIB}
export C11TESTER=$ENVIRONMENT

EXE=obj/demo
# EXE=obj/demo3
# EXE=obj/long-race
# EXE=obj/ring_buf




$EXE




