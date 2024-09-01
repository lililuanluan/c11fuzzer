import random
import string
from rf import *


def generate_random_filename(i):
    print(f"{i}")
    generated = str(i) + ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    print(generated)
    return generated

# last_selected_index = None


def mutate(ffrom, fto, last_selected_index):
    # random.seed(time.time())
    with open(ffrom, "r") as f:
        lines = f.readlines()

    # 随机选择一个 choices 不为 1 的行
    option = 3
    # 优先线程
    if option == 1: 
        non_one_indexes = [i for i, line in enumerate(lines) if line.strip().split()[2] != '1' and line.strip().split()[0] == 't'] # and line.strip().split()[0] == 'w'
        if not non_one_indexes:
            non_one_indexes = [i for i, line in enumerate(lines) if line.strip().split()[2] != '1']
    # 优先读写
    elif option == 2: 
        non_one_indexes = [i for i, line in enumerate(lines) if line.strip().split()[2] != '1' and line.strip().split()[0] == 'w'] # and line.strip().split()[0] == 'w'
        if not non_one_indexes:
            non_one_indexes = [i for i, line in enumerate(lines) if line.strip().split()[2] != '1']
    # 随机        
    else:
        non_one_indexes = [i for i, line in enumerate(lines) if line.strip().split()[2] != '1']

    if non_one_indexes:
        # 随机选择一个非1的行
        # selected_index = random.choice(non_one_indexes)
        while True:
            selected_index = random.choice(non_one_indexes)
            if selected_index != last_selected_index:
                break
        # print(f"selected line: {lines[selected_index]}, line number: {selected_index + 1}")
        # input()
        
        # 在第一行中加入 "d 行号"
        break_point = "b {}\n".format(selected_index + 1)

        # 将修改后的内容写入新文件
        with open(fto, "w") as f:
            f.write(break_point)
            f.writelines(lines)
    else:
        print("No lines with choices not equal to 1 found.")
        return None
        # input()
    
    return selected_index

def test():
    with open("tmp", "r") as f:
        lines = random_mutate(f.readlines())
    for line in lines:
        print(line, end='')
    
    
    
    
    pass

def random_mutate(lines):
    non_one_indexes = [i for i, line in enumerate(lines) if line.strip().split()[2] != '1']
    
    if non_one_indexes:
        selected_index = random.choice(non_one_indexes)
        # print(f"selected line: {lines[selected_index]}line number: {selected_index + 1}")
        # input()
        parts = lines[selected_index].split()
        idx = int(parts[1])
        num_choice = int(parts[2])
        if num_choice == 0:
            print(f"line selected {lines[selected_index]}")
            print("lines:")
            for l in lines:
                print(l, end='')
            print(f"parts[1] == idx == {idx}")
            # print(f"")
            input(f"num choice == {numchoice}")
            
        parts[1] = str((1 + idx) % num_choice)
        lines[selected_index] = ' '.join(parts) + '\n'
        # print(f"changed to {lines[selected_index]}")
        print("mutated rand")
        # input()
        # input(f"selected_index + 2 = {selected_index+2}")
        lines += f"b {selected_index + 2}\n"
        # lines += f"b {1000}\n"
    else:
        lines += f"b {1}\n"
    
    return lines

def try_rf_mutate(lines, pair):
    # print_recorded_rfs()
    # input()
    read = pair[0]
    write = pair[1]
    # input(f"mutating for rf {read}, {write}")
    for i in range(-1, -len(lines)-1, -1):
        # print(f"mutate: i = {i}")
        line = lines[i]
        # print(f"iterating line: {line}")
        parts = line.split()
        if parts == '':
            continue
        
        if parts[0] == 'w' and int(parts[2]) > 1 and  parts[3] == read and parts[4 + int(parts[1])] != write:
            # input(f"found a line {line}could be mutated")
            for j in range(0, int(parts[2]), 1):
                # input(f"write choice {parts[4+j]}")
                if parts[4 + j] == write:
                    parts[1] = str(j)
                    # print(f"original lines[i] = {lines[i]}")
                    lines[i] = ' '.join(parts)# + '\n'
                    # print(f"mutated lines[i] = {lines[i]}")
                    print("mutated rf")
                    # for l in lines:
                        # print(l, end='')
                    # input(f"i + 2 = {i+2}")
                    # lines += f"b {i + 2 + len(lines)}\n"
                    return True, lines           

    
    return False, lines


rf_mutated = 0
    
def rf_mutate(lines):
    # print("lines to be mutated")
    # for l in lines:
    #     print(l, end='')
    rf_pairs = number_pairs.get_sorted_pairs()
    mutated = False
    for pair in rf_pairs:
        # print(f"pair: {pair}")
        mutated, lines = try_rf_mutate(lines, pair)
        
        if mutated == True:
            # rf_mutated += 1
            return lines
    # return None
        
        
    # else:
    lines = random_mutate(lines)
    # lines += f"b {1}\n"   
        
    return lines

def test_rf():
    with open("tmp", "r") as f:
        lines = f.readlines()
        record_last_rf(lines)
        print_recorded_rfs()
        
        
        lines = rf_mutate(lines)
        
        print("mutated: ")
        for line in lines:
            print(line, end='')
            
def test_random():
    with open("tmp", "r") as f:
        lines = f.readlines()
        lines = random_mutate(lines)
        print(lines)

if __name__ == "__main__":
    # mutate("tmp", "tmp2")
    # test()
    # test_rf()
    test_random()