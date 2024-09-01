#!/bin/bash
# ms-queue 
TESTS="barrier chase-lev-deque mpmc-queue linuxrwlocks mcs-lock dekker-change rwlock-test seqlock-test reorder_10"

for t in ${TESTS}
do
    echo $t:
    python calculate.py $t.txt
done