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
CDSLIB = "/home/vagrant/c11tester"

TSAN = "/home/vagrant/c11tester-benchmarks/tsan11-missingbug/tsan11"
CDS = "/home/vagrant/c11tester-benchmarks/cdschecker_modified_benchmarks/"

test_with_dir = [("barrier", CDS + "barrier"), ("chase-lev-deque", CDS + "chase-lev-deque"), ("mpmc-queue", CDS + "mpmc-queue"), ("linuxrwlocks", CDS + "linuxrwlocks"), ("mcs-lock", CDS + "mcs-lock"), ("dekker-change", CDS + "dekker-change"), ["rwlock-test",TSAN], ["seqlock-test",TSAN], ["long-race", "/home/vagrant/c11tester/demo/obj/"]]

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
    return False
    read = pair[0]
    write = pair[1]
    cnt = 0
    ret = False
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
                    ret = True
                    lines_cpy = copy(tmp_out_content)
                    # input(lines_cpy)
                    # parts[SELECTED_IDX] = str((1 + idx) % num_choice) # 
                    parts[SELECTED_IDX] = str(j)
                    
                    lines_cpy[i] = ' '.join(parts) + '\n'
                    lines_cpy.append(f"b {i + 2}") 
                    mutated = ''.join(lines_cpy)
                    interesting_traces.append((mutated, 'rf'))
                    # print(f"rf mutated: {mutated}", end = ' ')
                    cnt += 1
                    ret = True
                    if cnt >= 2:
                        return True
                        return ret
                    # input()
                    # break
    return False                # always mutate randomly
    return ret                  # only do random mutation when no rf mutations awailable
    return False                # mutate when not enough rf mutations performed
            
mutated_seeds = []
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
        if lines not in mutated_seeds:
            mutated_seeds.append(mutated_seeds)
            interesting_traces.append((lines, 'rnd'))
            
            

def process_trace(tmp_out_content):
    rf_pairs = number_pairs.get_sorted_pairs()
    
    mutated_rf = False
    for pair in rf_pairs:
        mutated_rf = mutate_if_interesting(tmp_out_content, pair)
        pass
    
    if(mutated_rf == False):    
        random_mutate_trace(tmp_out_content)
        
mut_data = ""

def bench(TEST, TEST_DIR, is_random = False):
    
    number_pairs.clear()
    interesting_traces.clear()
    mutated_seeds.clear()
    hashes = set()
    
    os.chdir(TEST_DIR)    
    os.system("rm -f C11FuzzerTmp* rf*.json")
    if is_random:
        HASH_FILE = os.path.join(CUR, TEST + ".txt")
    else:
        HASH_FILE = os.path.join(CUR, TEST + "_hashes2.txt")
    os.system(f"rm {HASH_FILE}")
    print(HASH_FILE)
    tmp_out_content = None
    num_execution = 10000 - 3
    
    rf_mut_cnt = 0
    rnd_mut_cnt = 0
    rf_mut_bug = []
    rnd_mut_bug = []
    for i in range(1, num_execution + 1):
        if i % 1 == 0:
            # print(f"i = {i}")
            pass
            
        rf_or_rnd = None
        tmp_in_content = None
        # input(f"interesting_traces size {len(interesting_traces)}")
        if is_random == False and len(interesting_traces) > 0:
            tmp_in_content, rf_or_rnd = interesting_traces.pop()
            if rf_or_rnd == 'rf':
                rf_mut_cnt += 1
            if rf_or_rnd == 'rnd':
                rnd_mut_cnt += 1
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
                        if tmp_in_content != None:
                            interesting_traces.append((tmp_in_content, rf_or_rnd))
                    # print_recorded_rfs()
                    if rf_or_rnd == 'rf':
                        rf_mut_bug.append(hash_value)
                    if rf_or_rnd == 'rnd':
                        rnd_mut_bug.append(hash_value)
                    
                    

    print_statistics(HASH_FILE)
    # print_recorded_rfs()
    if is_random == False:
        # print(f"rf mutated: {rf_mut_cnt}")
        # print(f"rf mutated bug: {len(rf_mut_bug)}")
        # print(f"rf mutated uniq bug: {len(Counter(rf_mut_bug))}")
        # print(f"rnd mutated: {rnd_mut_cnt}")
        # print(f"rnd mutated bug: {len(rnd_mut_bug)}")
        # print(f"rnd mutated uniq bug: {len(Counter(rnd_mut_bug))}")
        # print(f"{"rf mutated"}, {"rf mutated bug"}, {"rf mutated uniq bug"}, {"rnd mutated"}, {"rnd mutated bug"}, {"rnd mutated uniq bug"}")
        mut_data = f"{rf_mut_cnt} {len(rf_mut_bug)} {len(Counter(rf_mut_bug))} {rnd_mut_cnt} {len(rnd_mut_bug)} {len(Counter(rnd_mut_bug))}"
        # print(mut_data)
        with open(CUR + "/mut_data.txt", 'a') as file:
        # f.writeline(f"{"rf mutated"}, {"rf mutated bug"}, {"rf mutated uniq bug"}, {"rnd mutated"}, {"rnd mutated bug"}, {"rnd mutated uniq bug"}")
            # input(mut_data)
            file.write(mut_data + "\n")

                    


def run():
    with open("mut_data.txt", "w") as file:
        # f.writeline(f"{"rf mutated"}, {"rf mutated bug"}, {"rf mutated uniq bug"}, {"rnd mutated"}, {"rnd mutated bug"}, {"rnd mutated uniq bug"}")
        file.write("{}, {}, {}, {}, {}, {}\n".format("rf mutated", "rf mutated bug", "rf mutated uniq bug", "rnd mutated", "rnd mutated bug", "rnd mutated uniq bug"))
        
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
    TEST, TEST_DIR = test_with_dir[-1]
    print(TEST, TEST_DIR)
    
    bench(TEST, TEST_DIR, is_random=True)
    bench(TEST, TEST_DIR, is_random=False)
    
    # for i in range(0, len(test_with_dir)):
    #     random.seed(114514)
    #     TEST, TEST_DIR = test_with_dir[i]
    #     # print(TEST, TEST_DIR)
    #     # input()
    #     bench(TEST, TEST_DIR, True)
    #     bench(TEST, TEST_DIR, False)
    #     pass
    
    # os.chdir(CUR)
    # print_table(".txt", is_c11tester=True)
    # print()
    # print()
    # print_table("_hashes2.txt", is_c11tester=False)
    
    # tests = ["barrier", "chase-lev-deque", "mpmc-queue", "linuxrwlocks", "mcs-lock", "dekker-change", "rwlock-test", "seqlock-test"]
    
    # with open("mut_data.txt", "r") as f:
    #     lines = f.read().strip().split('\n')
    #     print(lines)
        
    #     headers = lines[0].split(',')
    #     headers = [header.strip() for header in headers]
    #     data = []
    #     for line in lines[1:]:
    #         # 将每行数据按空格拆分并转为整数
    #         row = row = [float(num) * 100 / 1000 for num in line.split()]
    #         data.append(row )

        
    #     print_table_with_data(tests, headers, data)











    


    
    # print_recorded_rfs()



if __name__ == "__main__":
    random.seed(114514)
    run()