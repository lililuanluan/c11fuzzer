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

TSAN = "/home/vagrant/c11tester-benchmarks/tsan11-missingbug/tsan11"
CDS = "/home/vagrant/c11tester-benchmarks/cdschecker_modified_benchmarks/"

test_with_dir = [("barrier", CDS + "barrier"), ("chase-lev-deque", CDS + "chase-lev-deque"), ("mpmc-queue", CDS + "mpmc-queue"), ("linuxrwlocks", CDS + "linuxrwlocks"), ("mcs-lock", CDS + "mcs-lock"), ("dekker-change", CDS + "dekker-change"), ["rwlock-test",TSAN], ["seqlock-test",TSAN]]

TYPE = 0
SELECTED_IDX = 1
NUM_CHOICE = 2
READ = 3
WRITES = 4
interesting_traces = []

            
mutated_seeds = []
def random_mutate_trace(lines):
    # print("random_mutate_trace---\n", lines)
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
        
mut_data = ""

def bench(TEST, TEST_DIR, is_random = False, num_execution = 10000):
    
    random.seed(114514)
    
    number_pairs.clear()
    interesting_traces.clear()
    mutated_seeds.clear()
    hashes = set()
    hash_frequencies = {}
    
    os.chdir(TEST_DIR)    
    
    if is_random:
        HASH_FILE = os.path.join(CUR, TEST + ".txt")
    else:
        HASH_FILE = os.path.join(CUR, TEST + "_hashes2.txt")
    os.system(f"rm {HASH_FILE}")
    
    # input(HASH_FILE)
    tmp_out_content = None
    # num_execution = 100-2
    
    
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
    for i in range(1, num_execution + 1):
        os.system("rm -f C11FuzzerTmp*")
        # input(f"i = {i}")
        batch_size = num_execution / 10
        if i % batch_size == 1:
            print(["fuzz", "random"][is_random] + f": {i} / {num_execution}")
            pass
            
            
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
        
        start_time = time.time()
        output = run_command(["./" + TEST])
        end_time = time.time()
        run_TEST_time = run_TEST_time + end_time - start_time
        
        with open(tmp_out, 'r') as f:
            tmp_out_content = f.readlines()
        if output:
            new_hash = False
            got_hash = False
            for line in output.split("\n"):
                if "HASH" in line:
                    # get execution hash
                    got_hash = True
                    hash_value = line.split("HASH ")[1]  
                    if hash_value in hash_frequencies:
                        hash_frequencies[hash_value] += 1   
                    else:
                        hash_frequencies[hash_value] = 1     
                         
                    # print("hash freq total: ", sum(hash_frequencies.values()))     
                    weight = hash_frequencies[hash_value]/sum(hash_frequencies.values())
                    if hash_value not in hashes:
                        hashes.add(hash_value)
                        new_hash = True
                        
                    with open(HASH_FILE, "a") as f:
                        f.write(line  + "\n") # + "  ----" + str(i)
                    
                    if is_random == False:
                        if rf_or_thrd != None:
                            if rf_or_thrd == 'w':
                                rf_mut_uniq += 1
                            if rf_or_thrd == 't':
                                thrd_mut_uniq += 1
                        if new_hash == True:
                            weight = 0
                        
                        thres = 0.1
                        m = 7
                        # m = 5
                        mut_times = m - int(m*weight/thres)
                        if weight < thres:
                            for i in range(0, mut_times):
                            
                                tmp_out_content2 = tmp_out_content.copy()
                                process_trace(tmp_out_content2)
                           
                            if tmp_in_content != None:
                                interesting_traces.append((tmp_in_content, rf_or_thrd))
                    
                    
                elif "Aborted." in line: #  # uncomment abort() in datarace.cc
                    # print("Aborted.")
                    with open(HASH_FILE, "a") as f:
                        f.write(line + "\n")
                    
                    
                    # print_recorded_rfs()
                    # if rf_or_thrd == 'rf':
                    #     rf_mut_bug.append(hash_value)
                    # if rf_or_thrd == 'rnd':
                    #     rnd_mut_bug.append(hash_value)
            if got_hash == False:
                print("no hash got !!!! output:")
                print(output)
                       
        else:
            print("no output from command")            

    print_statistics(HASH_FILE)
    # print(hash_frequencies)
    print(sorted(hash_frequencies.items(), key=lambda item: item[1], reverse=True))
    print(f"pure TEST elapsed: {(run_TEST_time/ 60):.6f} minutes") 
    # print_recorded_rfs()
    if is_random == False:
        print(f"rf mutated: {rf_mut_cnt}")
        print(f"rf mutated uniq: {rf_mut_uniq}")
        print(f"thrd mutated: {thrd_mut_cnt}")
        print(f"thrd mutated uniq: {thrd_mut_uniq}")
        # print(f"rnd mutated bug: {len(rnd_mut_bug)}")
        # print(f"rnd mutated uniq bug: {len(Counter(rnd_mut_bug))}")
        # print(f"{"rf mutated"}, {"rf mutated bug"}, {"rf mutated uniq bug"}, {"rnd mutated"}, {"rnd mutated bug"}, {"rnd mutated uniq bug"}")
        mut_data = f"{rf_mut_cnt} {rf_mut_uniq} {thrd_mut_cnt} {thrd_mut_uniq}"
        
            
        # print(mut_data)
        with open(CUR + "/mut_data.txt", 'a') as file:
        # f.writeline(f"{"rf mutated"}, {"rf mutated bug"}, {"rf mutated uniq bug"}, {"rnd mutated"}, {"rnd mutated bug"}, {"rnd mutated uniq bug"}")
            # input(mut_data)
            file.write(mut_data + "\n")


def long_race():
    TEST, TEST_DIR = ["long-race", "/home/vagrant/c11tester/demo/obj/"]
    os.chdir(CDSLIB)
    run_command(["make"])
    os.environ["LIBRARY_PATH"] = CDSLIB
    os.environ["LD_LIBRARY_PATH"] = CDSLIB
    os.environ["C11TESTER"] = "-x1 -v3"
    
    os.environ["REPLAY_TMPFILE_OUT"] = tmp_out
    bench(TEST, TEST_DIR, True)
    bench(TEST, TEST_DIR, False)
                    
def bipartite():
    TEST, TEST_DIR = ["bipartite_buf_hard", "/home/vagrant/c11tester/demo/obj/"]
    os.chdir(CDSLIB)
    run_command(["make"])
    os.environ["LIBRARY_PATH"] = CDSLIB
    os.environ["LD_LIBRARY_PATH"] = CDSLIB
    os.environ["C11TESTER"] = "-x1 -v3"
    
    os.environ["REPLAY_TMPFILE_OUT"] = tmp_out
    os.chdir("/home/vagrant/c11tester/demo/")
    run_command(["make", TEST])
    
    bench(TEST, TEST_DIR, True)
    bench(TEST, TEST_DIR, False)                    
                    

def mp():
    TEST, TEST_DIR = ["mp", "/home/vagrant/c11tester/demo/obj/"]
    os.chdir(CDSLIB)
    run_command(["make"])
    os.environ["LIBRARY_PATH"] = CDSLIB
    os.environ["LD_LIBRARY_PATH"] = CDSLIB
    os.environ["C11TESTER"] = "-x1 -v3"
    
    os.environ["REPLAY_TMPFILE_OUT"] = tmp_out
    os.chdir("/home/vagrant/c11tester/demo/")
    run_command(["make", TEST])
    
    bench(TEST, TEST_DIR, True)
    bench(TEST, TEST_DIR, False)    
    
def reorder():
    TEST, TEST_DIR = ["reorder_10", "/home/vagrant/c11tester/demo/obj/"]
    os.chdir(CDSLIB)
    run_command(["make"])
    os.environ["LIBRARY_PATH"] = CDSLIB
    os.environ["LD_LIBRARY_PATH"] = CDSLIB
    os.environ["C11TESTER"] = "-x1 -v3"
    
    os.environ["REPLAY_TMPFILE_OUT"] = tmp_out
    os.chdir("/home/vagrant/c11tester/demo/")
    run_command(["make", TEST])
    
    bench(TEST, TEST_DIR, True)
    bench(TEST, TEST_DIR, False)   
                    
def P1():
    TEST, TEST_DIR = ["P1", "/home/vagrant/c11tester/demo/obj/"]
    os.chdir(CDSLIB)
    run_command(["make"])
    os.environ["LIBRARY_PATH"] = CDSLIB
    os.environ["LD_LIBRARY_PATH"] = CDSLIB
    os.environ["C11TESTER"] = "-x1 -v3"
    
    os.environ["REPLAY_TMPFILE_OUT"] = tmp_out
    os.chdir("/home/vagrant/c11tester/demo/")
    run_command(["make", TEST])
    
    bench(TEST, TEST_DIR, True, 1000)
    bench(TEST, TEST_DIR, False, 1000)                       
                    
                    
if __name__ == "__main__":
    # long_race()
    mp()
    reorder()
    P1()
    bipartite()
    # run()
    