import sys
import os
from cal2 import *

    
def print_table_with_data(tests, metrics, data):
    table_width = max(len(header) for header in metrics) + 1
    # input(f"table width = {table_width}")   # 16
    
    # 打印左上角空白
    print(" " * table_width, end=" | ")

    # 打印第一行表头
    for header in tests:
        print(f"{header:^{table_width}}", end=" | ")
    print()

    # 打印分隔线
    print("-" * table_width, end="-|-")
    print("-" * ((table_width + 2) * len(tests) + 5 ), end = "-|\n")

    # 打印表格数据
    for i, header in enumerate(metrics):
        # input()
        print(f"{header:<{table_width}}", end=" | ")
        for j, col in enumerate(data):
            
            # d = f"{col[i]:.1f}" #+ " %"
            d = f"{col[i]}"
            print(f"{d:^{table_width}}", end=" | ")
        print()

def print_table(file_postfix, is_c11tester = False):
    tests = ["barrier", "chase-lev-deque", "mpmc-queue", "linuxrwlocks", "mcs-lock", "dekker-change", "rwlock-test", "seqlock-test", "bipartite_buf", "left_right", "ring_buf"]
    metrics = ["uniq executions", "bug rate", "uniq bug rate" ]
    
    data = []
    
    print(">>>>>>  " + ["fuzzer:", "c11tester:"][is_c11tester])
    
    # print("tests: ", end='\t')
    for test in tests:
        hash_set, success_count, failure_count, unique_failures, total_count = process_file(test + file_postfix)
        data.append([ len(hash_set) , failure_count, len(unique_failures)])
        
    print_table_with_data(tests, metrics, data)


def print_table_by_test(file_postfix, test, is_c11tester = False):
    
    
    # data = []
    
    print(">>>>>>  " + ["fuzzer:", "c11tester:"][is_c11tester])
    
    hash_set, success_count, failure_count, unique_failures, total_count = process_file(test + file_postfix)
    # data.append([ len(hash_set) , failure_count, len(unique_failures)])
        
        
    print(f"unique hashes: {len(hash_set)}")

if __name__ == "__main__":
    print_table(".txt", is_c11tester=True)
    print()
    print()
    print_table("_hashes2.txt", is_c11tester=False)
    # tests = ["barrier", "chase-lev-deque", "mpmc-queue", "linuxrwlocks", "mcs-lock", "dekker-change", "rwlock-test", "seqlock-test"]
    # for t in tests:
    #     # os.system("ls")
    #     os.system(f"touch {t}.txt")
    #     os.system(f"touch {t}_hashes2.txt")

