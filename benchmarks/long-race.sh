#!/bin/bash
rm C11FuzzerTmp*
set -e
clear
# CDSLIB="/home/vagrant/pctversion"
# ENVIRONMENT='-x10 -v1 -e20 -b10  --verbose=3'

CDSLIB="/home/vagrant/c11tester"
ENVIRONMENT='-x1000000 -v3 ' # 100k
# ENVIRONMENT='-h'
# ENVIRONMENT='-x10 -v1 -b11  --verbose=3'
# ENVIRONMENT='-h'

# type="longrace-pct"
# ENVIRONMENT='-x10000 -v3 -p1 -d10 -k100'

tmpfile="${type}.txt"
resultfile="${type}.result"


cd $CDSLIB
make
cd -
export LIBRARY_PATH=${CDSLIB} # link time (compile)

make clean
make
export LD_LIBRARY_PATH=${CDSLIB}

EXE=obj/long-race

export C11TESTER=$ENVIRONMENT

# for i in {1..100}; do
#     echo "iteration: $i"
    
#     $EXE > $tmpfile
#     echo "returned $?"
#     num=$(grep 'Aborted. Execution:' $tmpfile | awk '{print $NF}' )
#     if [ -n "$num" ]; then
        
#         echo "$i    $num" >> $resultfile
        
#     else
#         echo "$i    -1" >> $resultfile
#     fi
#     rm C11FuzzerTmp*
#     rm $tmpfile
# done


time $EXE # > $tmpfile