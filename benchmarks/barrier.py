import os
import subprocess
import shutil
import random

import time
from mutate import *
from cal2 import *
from seeds import *
from command import *
from rf import *

CUR = "/home/vagrant/c11tester/benchmarks"
CDSLIB = "/home/vagrant/c11tester"

TSAN = "/home/vagrant/c11tester-benchmarks/tsan11-missingbug/tsan11"
CDS = "/home/vagrant/c11tester-benchmarks/cdschecker_modified_benchmarks/"

# data races
# TEST, TEST_DIR = ["barrier", CDS + "barrier"]
# TEST, TEST_DIR = ["chase-lev-deque", CDS + "chase-lev-deque"]
# TEST, TEST_DIR = ["mpmc-queue", CDS + "mpmc-queue"]
# TEST, TEST_DIR = ["linuxrwlocks", CDS + "linuxrwlocks"]
TEST, TEST_DIR = ["mcs-lock", CDS + "mcs-lock"]
# TEST, TEST_DIR = ["dekker-change", CDS + "dekker-change"]

# assertions
# TEST, TEST_DIR = ["rwlock-test",TSAN]
# TEST, TEST_DIR = ["seqlock-test",TSAN]



HASH_FILE = os.path.join(CUR, TEST + "_hashes.txt")
# TMP_DIR = "/home/vagrant/c11tester/benchmarks/tmpfiles"

# def run_command(command):
#     # print(f"Running command: {command}")
#     try:
#         output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
#         print(output)
#         return output
#     except subprocess.CalledProcessError as e:
#         print(f"Error running command: {command}")
#         print(e.output)
#         return None







def compile():    
    os.chdir(CDSLIB)
    run_command(["make"])

    # Change to the test directory
    # os.chdir()
    os.chdir(TEST_DIR)

    # Clean up files
    os.system("rm -f C11FuzzerTmp* rf*.json")

def set_env():
    # Set environment variables for test execution
    os.environ["LIBRARY_PATH"] = CDSLIB
    os.environ["LD_LIBRARY_PATH"] = CDSLIB
    os.environ["C11TESTER"] = "-x1 -v3"


hashes = set()

rf_mutated_has_bug = 0

def main():
    # run_command(f"rm {HASH_FILE}")
    compile()
    set_env()
    
    # saved_files = []
    last_tmp_file = ""
    last_hash_value = None
    last_selected_index = None
    lines = None
    last_fail = False
    for i in range(1, 1000 + 1):
        print("i = ", i)
        os.environ["SEED"] = "{}".format(Seeds[i])
        tmp_out = "/home/vagrant/c11tester/benchmarks/tmp"
        tmp_in  = "/home/vagrant/c11tester/benchmarks/tmp1"
        os.environ["REPLAY_TMPFILE_OUT"] = tmp_out
        os.environ["RF"] = get_rf_env()
        
        if i != 1:
            # os.environ["REPLAY_TMPFILE_IN"] = tmp_in
            # # selected_file = random.choice(saved_files)
            # selected_file = tmp_out
            # last_selected_index = mutate(selected_file, tmp_in, last_selected_index)
            
            lines = rf_mutate(lines)
                # input("lines == None")
                
            with open(tmp_in, 'w') as f:
                f.writelines(lines)
            # if last_fail == True:
            os.environ["REPLAY_TMPFILE_IN"] = tmp_in
            
            # shutil.copyfile(tmp_in, os.path.join(TMP_DIR, str(i)+"in"))
            # print(lines)
            # input()
            
            
        output = run_command(["./" + TEST])
        is_interesting = True
        with open(tmp_out, 'r') as f:
            lines = f.readlines()
        if output:
            # input("has output")
            
            for line in output.split("\n"):
                if "HASH" in line:
                    # get execution hash
                    hash_value = line.split("HASH ")[1]
                    
                    if hash_value not in hashes:
                        hashes.add(hash_value)
                        is_interesting = True
                    with open(HASH_FILE, "a") as f:
                        f.write(line  + "\n") # + "  ----" + str(i)
                    if(hash_value == last_hash_value):
                        # input("repeated hash")
                        pass
                    last_hash_value = hash_value
                elif "Aborted." in line:
                    print("Aborted.")
                    last_fail = True
                    with open(HASH_FILE, "a") as f:
                        f.write(line + "\n")
                    record_last_rf(lines)
                    # print_recorded_rfs()
                    # input()
        else:
            input("no output")
        if is_interesting:
            # new_tmp_file = os.path.join(TMP_DIR, str(i)+"trace")
            new_tmp_file = tmp_out + "prev"
            shutil.copyfile(tmp_out, new_tmp_file)
            # saved_files.append(new_tmp_file)
            # mutate(new_tmp_file)
            # print(f"New hash found! Saved tmp content to: {new_tmp_file}")
            # input()

            # print("current tmp out is: ", new_tmp_file)
            last_tmp_file = tmp_out
        # input("Press Enter to continue...")
    
    os.chdir(CUR)
    

def statistics():
    filename = HASH_FILE
    hash_set, success_count, failure_count, unique_failures, total_count = process_file(filename)

    print("Total different hashes: {} {:.2f}%".format(len(hash_set), 100 * len(hash_set) / total_count))
    # print("Total successful executions: {} {:.2f}%".format(success_count, 100 * success_count / total_count))
    # for hash_val in hash_set:
    #     print(hash_val)
    print("Total failed executions: {} {:.2f}%".format(failure_count, 100 * failure_count / total_count))
    print("Total different failures: {} {:.2f}%".format(len(unique_failures), 100 * len(unique_failures) / total_count))
    print("Total:", total_count)
    
    # print_recorded_rfs()



if __name__ == "__main__":
    random.seed(114514)
    main()
    statistics()
    print_recorded_rfs()
    
    # 2809369706
    # 770712606