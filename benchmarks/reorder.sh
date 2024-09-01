#!/bin/bash
rm rf*.json
rm C11FuzzerTmp*
set -e
# CDSLIB="/home/vagrant/pctversion" ; ENVIRONMENT='-x1000 -v1 -b11 -e5 -h --verbose=3' # remove -h
CDSLIB="/home/vagrant/c11tester"; ENVIRONMENT='-x1000 -v3'
# CDSLIB="/home/vagrant/pctversion"
type="reorder_10"
# ENVIRONMENT='-x1000 -v3 -p0 -k100 ' # 100k


# type="longrace-pct"
# ENVIRONMENT='-x10000 -v3 -p1 -d9 -k100'

tmpfile="${type}.txt"
resultfile="${type}.result"


cd $CDSLIB
make
cd -
export LIBRARY_PATH=${CDSLIB} # link time (compile)

make clean
make
export LD_LIBRARY_PATH=${CDSLIB}

EXE=obj/reorder_10

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


# time $EXE # > $tmpfile
TEST=${type}
for i in `seq 1 1 100`; do

./obj/${TEST} | grep "Aborted. Execution: " >> ${TEST}.txt
done
python calculate.py ${TEST}.txt