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


tmp_out = "/home/vagrant/c11tester/benchmarks/tmp"
tmp_in  = "/home/vagrant/c11tester/benchmarks/tmp1"
CUR = "/home/vagrant/c11tester/benchmarks"
CDSLIB = "/home/vagrant/c11tester"


# tmp file protocol
TYPE = 0
SELECTED_IDX = 1
NUM_CHOICE = 2
READ = 3
WRITES = 4
interesting_traces = []

            
mutated_seeds = []
def random_mutate_trace(lines):
    # non_one_indexes = [i for i, line in enumerate(lines) if line.strip().split()[NUM_CHOICE] != '1' and line.strip().split()[TYPE] == 'w']
    non_one_indexes = [i for i, line in enumerate(lines) if line.strip().split()[NUM_CHOICE] != '1' and line.strip().split()[TYPE] == 't']
    # if random.random() % 2 == 1:
    #     non_one_indexes = [i for i, line in enumerate(lines) if line.strip().split()[NUM_CHOICE] != '1' and line.strip().split()[TYPE] == 't']
    # else:
    #     non_one_indexes = [i for i, line in enumerate(lines) if line.strip().split()[NUM_CHOICE] != '1' and line.strip().split()[TYPE] == 'w']
    
    # non_one_indexes = [i for i, line in enumerate(lines) if line.strip().split()[NUM_CHOICE] != '1']
    
    if non_one_indexes:
        selected_line = random.choice(non_one_indexes)
        # print(f"selected line: {lines[selected_line]}line number: {selected_line + 1}")
        # input()
        parts = lines[selected_line].split()
        idx = int(parts[SELECTED_IDX])
        num_choice = int(parts[NUM_CHOICE])
        type = parts[TYPE]
        if num_choice == 0:
            print(f"line selected {lines[selected_line]}")
            print("lines:")
            for l in lines:
                print(l, end='')
            # print(f"parts[1] == idx == {idx}")
            # print(f"")
            # input(f"num choice == {numchoice}")
        
        
        parts[SELECTED_IDX] = str((1 + idx) % num_choice)
        lines[selected_line] = ' '.join(parts) + '\n'
        # print(f"changed to {lines[selected_index]}")
        # print("mutated rand")
        # input()
        # input(f"selected_index + 2 = {selected_index+2}")
        lines += f"b {selected_line + 2}\n"
        if lines not in mutated_seeds:
            mutated_seeds.append(mutated_seeds)
            interesting_traces.append((lines, type))
            

def process_trace(tmp_out_content):    
    random_mutate_trace(tmp_out_content)


def bench(TEST, TEST_DIR, is_random = False):
    
    number_pairs.clear()
    interesting_traces.clear()
    mutated_seeds.clear()
    hashes = set()
    
    os.chdir(TEST_DIR)    
    
    if is_random:
        HASH_FILE = os.path.join(CUR, TEST + ".txt")
    else:
        HASH_FILE = os.path.join(CUR, TEST + "_hashes2.txt")
    os.system(f"rm {HASH_FILE}")
    
    # input(HASH_FILE)
    tmp_out_content = None
    # num_execution = 100-2
    num_execution_explored = 0
    num_execution = 10
     
    
    rf_mut_cnt = 0
    thrd_mut_cnt = 0
    rf_mut_uniq = 0
    thrd_mut_uniq = 0
    
    # timing
    run_TEST_time = 0
    # 
    # bench(TEST, TEST_DIR, False)
    # 
    # elapsed_time = end_time - start_time
    i = 0
    while num_execution_explored < num_execution:
        i = i + 1
        os.system("rm -f C11FuzzerTmp*")
        # input(f"i = {i}")
        # batch_size = num_execution / 10
        # if i % batch_size == 1:
        #     print(["random", "fuzz"][is_random] + f": {i} / {num_execution}")
        #     pass
            
            
        rf_or_thrd = None
        tmp_in_content = None
        # input(f"interesting_traces size {len(interesting_traces)}")
        if is_random == False and len(interesting_traces) > 0:
            tmp_in_content, rf_or_thrd = interesting_traces.pop()
            # input(f"rf_or_thrd: {rf_or_thrd}")
            if rf_or_thrd == 'w':
                rf_mut_cnt += 1
            if rf_or_thrd == 't':
                thrd_mut_cnt += 1
            # input(tmp_in_content)
            with open(tmp_in, 'w') as f:
                f.writelines(tmp_in_content)
            os.environ["REPLAY_TMPFILE_IN"] = tmp_in
            # print("rf mutated")
            # input("written to tmp_in")
        else:
            # print("rand")
            if "REPLAY_TMPFILE_IN" in os.environ:
                os.environ.pop("REPLAY_TMPFILE_IN")
            pass
        
        os.environ["SEED"] = f"{Seeds[i]}"
        
        start_time = time.perf_counter()
        output = run_command(["./" + TEST])
        # output = run_command(["./" + TEST, " --verbose -t 3"]) # silo
        end_time = time.perf_counter()
        
        
        with open(tmp_out, 'r') as f:
            tmp_out_content = f.readlines()
        if output:
            new_hash = False
            got_hash = False
            ReplayerTimer = None
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
                    
                    if new_hash == True:
                        # input("new hash")
                        if rf_or_thrd != None:
                            if rf_or_thrd == 'w':
                                rf_mut_uniq += 1
                            if rf_or_thrd == 't':
                                thrd_mut_uniq += 1
                        if is_random == False:
                            process_trace(tmp_out_content)
                        if tmp_in_content != None:
                            interesting_traces.append((tmp_in_content, rf_or_thrd))
                    
                    
                elif "Aborted." in line:
                    # print("Aborted.")
                    with open(HASH_FILE, "a") as f:
                        f.write(line + "\n")
                elif "ReplayerTimer" in line:
                    ReplayerTimer = line
                    # input()
                    
                    # print_recorded_rfs()
                    # if rf_or_thrd == 'rf':
                    #     rf_mut_bug.append(hash_value)
                    # if rf_or_thrd == 'rnd':
                    #     rnd_mut_bug.append(hash_value)
            if got_hash == False:
                print("no hash got !!!! output:")
                print(output)
                pass
            else:
                run_TEST_time = run_TEST_time + end_time - start_time
                num_execution_explored = num_execution_explored + 1
                print(ReplayerTimer)
                       
        else:
            print("no output from command")            

    
    print_statistics(HASH_FILE)
    return run_TEST_time
    # print(f"pure TEST elapsed: {(run_TEST_time/ 60):.6f} minutes") 


                    
    
def iris():
    TEST, TEST_DIR = ["test_lfringbuffer", "/home/vagrant/c11tester-benchmarks/iris/"]
    os.chdir(CDSLIB)
    run_command(["make"])
    os.environ["LIBRARY_PATH"] = CDSLIB
    os.environ["LD_LIBRARY_PATH"] = CDSLIB
    os.environ["C11TESTER"] = "-x1 -v3"
    
    os.environ["REPLAY_TMPFILE_OUT"] = tmp_out
    
    
    start_time = time.perf_counter()
    run_TEST_time = bench(TEST, TEST_DIR, True)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"pure TEST elapsed: {(run_TEST_time/ 60):.6f} minutes") 
    print(f"bench (random) executed in: {(elapsed_time/ 60):.6f} minutes")
    
    print("----------------------------")
    
    
    start_time = time.perf_counter()
    run_TEST_time = bench(TEST, TEST_DIR, False)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"pure TEST elapsed: {(run_TEST_time/ 60):.6f} minutes") 
    print(f"bench (fuzz) executed in: {(elapsed_time/ 60):.6f} minutes")


def mabain():
    # comment the abort in report data race
    TEST, TEST_DIR = ["mb_multi_thread_insert_test", "/home/vagrant/c11tester-benchmarks/mabain/examples/"]
    os.chdir(CDSLIB)
    run_command(["make"])
    os.environ["LIBRARY_PATH"] = CDSLIB
    os.environ["LD_LIBRARY_PATH"] = CDSLIB+":/home/vagrant/c11tester-benchmarks/mabain/src/"
    os.environ["C11TESTER"] = "-x1 -v3"
    
    os.environ["REPLAY_TMPFILE_OUT"] = tmp_out
    
    
    start_time = time.perf_counter()
    run_TEST_time = bench(TEST, TEST_DIR, True)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"pure TEST elapsed: {(run_TEST_time/ 60):.6f} minutes") 
    print(f"bench (random) executed in: {(elapsed_time/ 60):.6f} minutes")
    
    print("----------------------------")
    
    
    start_time = time.perf_counter()
    run_TEST_time = bench(TEST, TEST_DIR, False)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"pure TEST elapsed: {(run_TEST_time/ 60):.6f} minutes") 
    print(f"bench (fuzz) executed in: {(elapsed_time/ 60):.6f} minutes")


if __name__ == "__main__":
    random.seed(114514)
    # iris()
    mabain()