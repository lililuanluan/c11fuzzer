#!/bin/bash
set -e

CUR=/home/vagrant/c11tester/benchmarks

CDSLIB="/home/vagrant/c11tester"
cd $CDSLIB
make 
cd -

# races:
TEST=barrier
# TEST=chase-lev-deque
# TEST=mpmc-queue
# TEST=linuxrwlocks 
# TEST=mcs-lock
# TEST=ms-queue # omitted
# TEST=dekker-change

# assertions: 
# TEST=rwlock-test
# TEST=seqlock-test

export LIBRARY_PATH=${CDSLIB}
cd /home/vagrant/c11tester-benchmarks/cdschecker_modified_benchmarks/${TEST}
# cd /home/vagrant/c11tester-benchmarks/tsan11-missingbug/tsan11
echo "ohhh"
pwd
make
set +e
rm C11FuzzerTmp*
rm rf*.json
rm  ${CUR}/${TEST}.txt
set -e
ls
# make clean
# make
export LD_LIBRARY_PATH=${CDSLIB} 
ENVIRONMENT='-x1 -v3'
export C11TESTER=$ENVIRONMENT

source ${CUR}/seeds2.sh
# ./${TEST}
for i in `seq 1 1 10`; do
    export REPLAY_TMPFILE_OUT="/home/vagrant/c11tester/benchmarks/tmp"
    export REPLAY_TMPFILE_IN="/home/vagrant/c11tester/benchmarks/tmp1"
    # export REPLAY_TMPFILE_IN="/home/vagrant/c11tester/benchmarks/tmpfiles/8in"
    # ./${TEST} | grep "Aborted. Execution: " >>${CUR}/${TEST}.txt
    # sleep .5
    export RF="16837695655910571667 5277646471145575703"
    export SEED=${Seeds[i]}
    # echo $SEED
    # ./${TEST} | grep "HASH \|Aborted. " >> ${CUR}/${TEST}.txt
    ./${TEST}
done
cd ${CUR}
python3 cal2.py ${TEST}.txt

# 

# # 优先读写
# 0
# 30
# 113
# 140
# 178
# Total different hashes: 216 21.60%
# Total successful executions: 924 92.40%
# Total failed executions: 76 7.60%
# Total different failures: 5 0.50%

# # 优先线程
# 9
# 11
# 12
# 14
# 41
# Total different hashes: 232 23.20%
# Total successful executions: 903 90.30%
# Total failed executions: 97 9.70%
# Total different failures: 5 0.50%
# Total: 1000

# # 随机
# 4
# 5
# 29
# 113
# 143
# Total different hashes: 234 23.40%
# Total successful executions: 916 91.60%
# Total failed executions: 84 8.40%
# Total different failures: 5 0.50%
# Total: 1000

# # c11tester随机算法
# 7
# 11
# 14
# 20
# 44
# Total different hashes: 373 3.73%
# Total successful executions: 7849 78.49%
# Total failed executions: 2151 21.51%
# Total different failures: 5 0.05%
# Total: 10000

