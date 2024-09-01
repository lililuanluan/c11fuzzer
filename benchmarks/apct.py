import os
import subprocess
import shutil
import random
from copy import copy
from collections import Counter
import time
from mutate import *
from cal2 import *
from seeds import *
from command import *
from rf import *
from table import *

CUR = "/home/vagrant/c11tester/benchmarks"
CDSLIB = "/home/vagrant/pctwmtest"

TSAN = "/home/vagrant/c11tester-benchmarks/tsan11-missingbug/tsan11"
CDS = "/home/vagrant/c11tester-benchmarks/cdschecker_modified_benchmarks/"

# test_with_dir = [("barrier", CDS + "barrier"), ("chase-lev-deque", CDS + "chase-lev-deque"), ("mpmc-queue", CDS + "mpmc-queue"), ("linuxrwlocks", CDS + "linuxrwlocks"), ("mcs-lock", CDS + "mcs-lock"), ("dekker-change", CDS + "dekker-change"), ["rwlock-test",TSAN], ["seqlock-test",TSAN]]
test_with_dir = [("linuxrwlocks", CDS + "linuxrwlocks")]

# ENVIRONMENT='-h -x1 -p'$VERSION' -d'$DEPTH' -k'$COMMUNICATIONEVENTS' -y'$HISTORY''
test_with_env = {
    "barrier": "-x1 -p1 -d1 -k10 -y2",  # ok
    "chase-lev-deque": "-x1 -p1 -d2 -k56 -y1",  # ok
    "mpmc-queue":    "-x1 -p1 -d2 -k17 -y2",    # no abort
    "linuxrwlocks": "-x1 -p1 -d5 -k100 -y10",     # all hash same
    "mcs-lock": "-x1 -p1 -d1 -k16 -y1",         # no abort
    "dekker-change": "-x1 -p1 -d1 -k14 -y1",    # deadlocks...
    "rwlock-test":  "-x1 -p1 -d3 -k74 -y3",     # no abort
    "seqlock-test": "-x1 -p1 -d4 -k18 -y1"      # ok
}


# pctwm version
def bench(TEST, TEST_DIR):
    
    os.environ["C11TESTER"] = test_with_env[TEST] + " -v3"
    print(f"set environ: ", os.environ["C11TESTER"])
    # input()
    
    hashes = set()
        
    os.chdir(TEST_DIR)    
    
    HASH_FILE = os.path.join(CUR , TEST + "_pct.txt")
    os.system(f"rm {HASH_FILE}")
    
    print("HASH_FILE = ", HASH_FILE)
    # input()
    
    num_execution = 10000
    
    # timing
    run_TEST_time = 0
    
    for i in range(1, num_execution + 1):
        os.system("rm -f C11FuzzerTmp*")
        batch_size = num_execution / 10
        if i % batch_size == 1:
            print("pct: " + f"{i} / {num_execution}")
            pass
          

                
        os.environ["SEED"] = f"{Seeds[i]}"
        
        start_time = time.time()
        output = run_command(["./" + TEST])
        end_time = time.time()
        run_TEST_time = run_TEST_time + end_time - start_time
        

        if output:
            new_hash = False
            got_hash = False
            for line in output.split("\n"):
                if "HASH" in line:
                    # get execution hash
                    got_hash = True
                    hash_value = line.split("HASH ")[1]                    
                    if hash_value not in hashes:
                        hashes.add(hash_value)
                        new_hash = True
                        
                    with open(HASH_FILE, "a") as f:
                        f.write(line  + "\n") # + "  ----" + str(i)                    
                  
                elif "Aborted." in line:
                    # print("Aborted.")
                    with open(HASH_FILE, "a") as f:
                        f.write(line + "\n")                    
                    
                  
            if got_hash == False:
                print("no hash got !!!! output:")
                print(output)
                       
        else:
            print("no output from command")            

    print_statistics(HASH_FILE)
    print(f"pure TEST elapsed: {(run_TEST_time/ 60):.6f} minutes") 
    # print_recorded_rfs()
   

                    


def run():
    

    os.chdir(CDSLIB)
    run_command(["make"])
    os.environ["LIBRARY_PATH"] = CDSLIB
    os.environ["LD_LIBRARY_PATH"] = CDSLIB
    os.environ["C11TESTER"] = "-x1 -v3"
    
   
    
    for i in range(0, len(test_with_dir)):
        random.seed(114514)
        TEST, TEST_DIR = test_with_dir[i]
        print(TEST, TEST_DIR)
        # input()
        bench(TEST, TEST_DIR)
        pass
    
    
    os.chdir(CUR)
    
   
    
    
if __name__ == "__main__":
    random.seed(114514)
    run()