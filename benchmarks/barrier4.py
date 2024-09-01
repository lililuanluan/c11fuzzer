import os
import subprocess
import shutil
import random
from copy import copy
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

test_with_dir = [("barrier", CDS + "barrier"), ("chase-lev-deque", CDS + "chase-lev-deque"), ("mpmc-queue", CDS + "mpmc-queue"), ("linuxrwlocks", CDS + "linuxrwlocks"), ("mcs-lock", CDS + "mcs-lock"), ("dekker-change", CDS + "dekker-change"), ["rwlock-test",TSAN], ["seqlock-test",TSAN]]

tmp_out = "/home/vagrant/c11tester/benchmarks/tmp"
tmp_in  = "/home/vagrant/c11tester/benchmarks/tmp1"

# tmp file protocol
TYPE = 0
SELECTED_IDX = 1
NUM_CHOICE = 2
READ = 3
WRITES = 4

interesting_traces = []

def mutate_if_interesting(tmp_out_content, pair):
    read = pair[0]
    write = pair[1]
    cnt = 0
    for rev_i, line in enumerate(reversed(tmp_out_content)):
        i = len(tmp_out_content) - rev_i - 1
        parts = copy(line).split()
        if parts == '':
            continue
    
        
        idx = int(parts[SELECTED_IDX])
        num_choice = int(parts[NUM_CHOICE])
        if parts[TYPE] == 'w' and num_choice > 1 and parts[READ] == read and parts[WRITES + idx] != write:
            # print(f"found a mutation point, {line}")
            # input()
            for j in range(0, int(parts[NUM_CHOICE]), 1):
                if(parts[WRITES + j]) == write:
                    # print(tmp_out_content)
                    
                    lines_cpy = copy(tmp_out_content)
                    # input(lines_cpy)
                    # parts[SELECTED_IDX] = str((1 + idx) % num_choice) # 
                    parts[SELECTED_IDX] = str(j)
                    
                    lines_cpy[i] = ' '.join(parts) + '\n'
                    lines_cpy.append(f"b {i + 2}") 
                    mutated = ''.join(lines_cpy)
                    interesting_traces.append(mutated)
                    # print(f"mutated: {mutated}", end = ' ')
                    cnt += 1
                    if cnt >= 2:
                        return True
                    # input()
                    # break
    return False                # return
            
def random_mutate_trace(lines):
    non_one_indexes = [i for i, line in enumerate(lines) if line.strip().split()[NUM_CHOICE] != '1' and line.strip().split()[TYPE] == 't']
    # non_one_indexes = [i for i, line in enumerate(lines) if line.strip().split()[NUM_CHOICE] != '1']
    
    if non_one_indexes:
        selected_line = random.choice(non_one_indexes)
        # print(f"selected line: {lines[selected_index]}line number: {selected_index + 1}")
        # input()
        parts = lines[selected_line].split()
        idx = int(parts[SELECTED_IDX])
        num_choice = int(parts[NUM_CHOICE])
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
        interesting_traces.append(lines)
            
            

def process_trace(tmp_out_content):
    rf_pairs = number_pairs.get_sorted_pairs()
    
    mutated_rf = False
    for pair in rf_pairs:
        mutated_rf = mutate_if_interesting(tmp_out_content, pair)
        pass
    
    if(mutated_rf == False):    
        random_mutate_trace(tmp_out_content)

def bench(TEST, TEST_DIR, is_random = False):
    number_pairs.clear()
    interesting_traces.clear()
    hashes = set()
    
    os.chdir(TEST_DIR)    
    os.system("rm -f C11FuzzerTmp* rf*.json")
    if is_random:
        HASH_FILE = os.path.join(CUR, TEST + ".txt")
    else:
        HASH_FILE = os.path.join(CUR, TEST + "_hashes2.txt")
    os.system(f"rm {HASH_FILE}")
    tmp_out_content = None
    num_execution = 9999-1   # max 9999
    for i in range(1, num_execution + 1):
        if i % 1 == 0:
            # print(f"i = {i}")
            pass
            
        # input(f"interesting_traces size {len(interesting_traces)}")
        if is_random == False and len(interesting_traces) > 0:
            tmp_in_content = interesting_traces.pop()
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
        
        output = run_command(["./" + TEST])
        with open(tmp_out, 'r') as f:
            tmp_out_content = f.readlines()
        if output:
            new_hash = False
            for line in output.split("\n"):
                if "HASH" in line:
                    # get execution hash
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
                    record_last_rf(tmp_out_content)
                    if new_hash == True:
                        process_trace(tmp_out_content)
                    # print_recorded_rfs()
                    
                    

    print_statistics(HASH_FILE)
    print_recorded_rfs()
    

                    


def run():
    os.chdir(CDSLIB)
    run_command(["make"])
    os.environ["LIBRARY_PATH"] = CDSLIB
    os.environ["LD_LIBRARY_PATH"] = CDSLIB
    os.environ["C11TESTER"] = "-x1 -v3"
    
    os.environ["REPLAY_TMPFILE_OUT"] = tmp_out
    # random.seed(time.time())
    # while len(seeds) < 1000:
    #     try_all()
    # print(seeds)
    # try_all()
    for i in range(7, len(test_with_dir)):
        random.seed(114514)
        TEST, TEST_DIR = test_with_dir[i]
        # print(TEST, TEST_DIR)
        # input()
        bench(TEST, TEST_DIR, True)
        # bench(TEST, TEST_DIR, False)
    












    


    
    # print_recorded_rfs()



if __name__ == "__main__":
    
    run()