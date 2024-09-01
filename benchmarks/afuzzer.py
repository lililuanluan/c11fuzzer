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

test_with_dir = [("barrier", CDS + "barrier"), ("chase-lev-deque", CDS + "chase-lev-deque"), ("mpmc-queue", CDS + "mpmc-queue"), ("linuxrwlocks", CDS + "linuxrwlocks"), ("mcs-lock", CDS + "mcs-lock"), ("dekker-change", CDS + "dekker-change"), ["rwlock-test",TSAN], ["seqlock-test",TSAN]]
# , ["long-race", "/home/vagrant/c11tester/demo/obj/"]
tmp_out = "/home/vagrant/c11tester/benchmarks/tmp"
tmp_in  = "/home/vagrant/c11tester/benchmarks/tmp1"

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
        
mut_data = ""

def bench(TEST, TEST_DIR, is_random = False):
    # random.seed(114514)
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
    num_execution = 5000
    
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
            print(["random", "fuzz"][is_random] + f": {i} / {num_execution}")
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
                        process_trace(tmp_out_content)
                        if tmp_in_content != None:
                            interesting_traces.append((tmp_in_content, rf_or_thrd))
                    
                    
                elif "Aborted." in line:    # uncomment abort() in datarace.cc
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

                    


def run():
    
    with open(os.path.join(CUR, "mut_data.txt"), "w") as file:
        file.write("{}, {}, {}, {}\n".format("rf mutated", "rf mutated uniq", "thrd mutated", "thrd mutated uniq"))
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
    # TEST, TEST_DIR = test_with_dir[-1]
    # print(TEST, TEST_DIR)
    
    # bench(TEST, TEST_DIR, is_random=True)
    # bench(TEST, TEST_DIR, is_random=False)
    
    for i in range(0, len(test_with_dir)):
        random.seed(114514)
        TEST, TEST_DIR = test_with_dir[i]
        # print(TEST, TEST_DIR)
        # input()
        bench(TEST, TEST_DIR, True)
        bench(TEST, TEST_DIR, False)
        pass
    
    
    os.chdir(CUR)
    print_table(".txt", is_c11tester=True)
    print()
    print()
    print_table("_hashes2.txt", is_c11tester=False)
    
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

# rf mutation works better
def ring_buf():
    TEST, TEST_DIR = ["ring_buf", "/home/vagrant/c11tester/demo/obj/"]
    os.chdir("/home/vagrant/c11tester/demo/")
    run_command("ls")
    run_command("make")
    # input()
    os.chdir(CDSLIB)
    run_command(["make"])
    os.environ["LIBRARY_PATH"] = CDSLIB
    os.environ["LD_LIBRARY_PATH"] = CDSLIB
    os.environ["C11TESTER"] = "-x1 -v3"
    
    os.environ["REPLAY_TMPFILE_OUT"] = tmp_out
    bench(TEST, TEST_DIR, True)
    bench(TEST, TEST_DIR, False)
    
# lower TEST_MT_TRANSFER_CNT should make difference
# thrd mut
# 
def bipartite_buf():
    TEST, TEST_DIR = ["bipartite_buf", "/home/vagrant/c11tester/demo/obj/"]
    os.chdir("/home/vagrant/c11tester/demo/")
    run_command("ls")
    run_command("make")
    # input()
    os.chdir(CDSLIB)
    run_command(["make"])
    os.environ["LIBRARY_PATH"] = CDSLIB
    os.environ["LD_LIBRARY_PATH"] = CDSLIB
    os.environ["C11TESTER"] = "-x1 -v3"
    
    os.environ["REPLAY_TMPFILE_OUT"] = tmp_out
    bench(TEST, TEST_DIR, True)
    bench(TEST, TEST_DIR, False)
    
def bipartite_buf2():
    TEST, TEST_DIR = ["bipartite_buf_hard", "/home/vagrant/c11tester/demo/obj/"]
    os.chdir("/home/vagrant/c11tester/demo/")
    run_command("ls")
    run_command(["make", TEST])
    # input()
    os.chdir(CDSLIB)
    run_command(["make"])
    os.environ["LIBRARY_PATH"] = CDSLIB
    os.environ["LD_LIBRARY_PATH"] = CDSLIB
    os.environ["C11TESTER"] = "-x1 -v3"
    
    os.environ["REPLAY_TMPFILE_OUT"] = tmp_out
    bench(TEST, TEST_DIR, True)
    bench(TEST, TEST_DIR, False)

# rf or mix works better
def left_right():
    TEST, TEST_DIR = ["left_right", "/home/vagrant/c11tester/demo/obj/"]
    os.chdir("/home/vagrant/c11tester/demo/")
    run_command("ls")
    run_command("make")
    # input()
    os.chdir(CDSLIB)
    run_command(["make"])
    os.environ["LIBRARY_PATH"] = CDSLIB
    os.environ["LD_LIBRARY_PATH"] = CDSLIB
    os.environ["C11TESTER"] = "-x1 -v3"
    
    os.environ["REPLAY_TMPFILE_OUT"] = tmp_out
    bench(TEST, TEST_DIR, True)
    bench(TEST, TEST_DIR, False)
    
# not used
def prio_queue():
    TEST, TEST_DIR = ["prio_queue", "/home/vagrant/c11tester/demo/obj/"]
    os.chdir("/home/vagrant/c11tester/demo/")
    run_command("ls")
    run_command("make")
    # input()
    os.chdir(CDSLIB)
    run_command(["make"])
    os.environ["LIBRARY_PATH"] = CDSLIB
    os.environ["LD_LIBRARY_PATH"] = CDSLIB
    os.environ["C11TESTER"] = "-x1 -v3"
    
    os.environ["REPLAY_TMPFILE_OUT"] = tmp_out
    bench(TEST, TEST_DIR, True)
    bench(TEST, TEST_DIR, False)
    
def iris():
    TEST, TEST_DIR = ["test_lfringbuffer", "/home/vagrant/c11tester-benchmarks/iris/"]
    os.chdir(CDSLIB)
    run_command(["make"])
    os.environ["LIBRARY_PATH"] = CDSLIB
    os.environ["LD_LIBRARY_PATH"] = CDSLIB
    os.environ["C11TESTER"] = "-x1 -v3"
    
    os.environ["REPLAY_TMPFILE_OUT"] = tmp_out
    
    
    start_time = time.time()
    bench(TEST, TEST_DIR, True)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"bench (random) executed in: {(elapsed_time/ 60):.6f} minutes")
    
    print("----------------------------")
    
    
    start_time = time.time()
    bench(TEST, TEST_DIR, False)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"bench (fuzz) executed in: {(elapsed_time/ 60):.6f} minutes")

def dekker():
    TEST, TEST_DIR = ["dekker-change", CDS + "dekker-change"]
    os.chdir(CDSLIB)
    run_command(["make"])
    os.environ["LIBRARY_PATH"] = CDSLIB
    os.environ["LD_LIBRARY_PATH"] = CDSLIB
    os.environ["C11TESTER"] = "-x1 -v3"
    
    os.environ["REPLAY_TMPFILE_OUT"] = tmp_out
    bench(TEST, TEST_DIR, True)
    bench(TEST, TEST_DIR, False)  
    
    
if __name__ == "__main__":
    random.seed(114514)
    # run()
    # long_race()
    # ring_buf()
    # bipartite_buf()
    # bipartite_buf2()
    # left_right()
    # prio_queue()
    # iris()
    # dekker()