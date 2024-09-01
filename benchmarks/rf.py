from collections import defaultdict

class NumberPairs:
    def __init__(self):
        self.freq_map = defaultdict(int)
        self.sorted_pairs = []
        
    def clear(self):
        self.freq_map.clear()
        self.sorted_pairs.clear()

    def record_pair(self, pair):
        # 更新频次字典
        self.freq_map[pair] += 1

        # 根据频次对数对排序
        self.sorted_pairs = sorted(self.freq_map.keys(), key=lambda x: self.freq_map[x], reverse=True)

    def get_sorted_pairs(self):
        return self.sorted_pairs

    def get_sorted_pairs_with_frequency(self):
        return [(pair, self.freq_map[pair]) for pair in self.sorted_pairs]
    
    def get_pairs_with_first_element(self, value):
        pairs = [(pair, freq) for pair, freq in self.freq_map.items() if pair[0] == value]
        return sorted(pairs, key=lambda x: x[1], reverse=True)

number_pairs = NumberPairs()

def get_last_rf(lines):
    read = None
    write = None
    for line in lines:
        parts = line.strip().split()
        if parts[0] == 'w':
            read = parts[3]
            if(4 + int(parts[1]) >= len(parts)):
                print(f"out of index: line: {line}")
                for l in lines:
                    print(l, end = '')
                input()
            write = parts[4 + int(parts[1])]
    return read, write
    
def record_last_rf(lines):
    r, w = get_last_rf(lines)
    number_pairs.record_pair((r, w))
    
def print_recorded_rfs():
    sorted_pairs_with_frequency = number_pairs.get_sorted_pairs_with_frequency()
    print("Sorted Pairs with Frequency:")
    for pair, frequency in sorted_pairs_with_frequency:
        print(pair, "-", frequency)
        
def get_rf_env():
    
    rf = number_pairs.get_sorted_pairs()
    env = ''
    for pair in rf:
        # print(f"pair = {pair}")
        if(pair[0]!=None and pair[1]!=None):
            env += pair[0]
            env += ' '
            env += pair[1]
            env += ' '
    return env
    
def test_rf_env():
    # number_pairs.record_pair(('5277646471145575703', '15815996774348270660'))
    # number_pairs.record_pair(('5277646471145575703', '15815996774348270660'))
    # number_pairs.record_pair(('5277646471145575703', '15815996774348270660'))
    # number_pairs.record_pair(('16837695655910571667', '15815996774348270660'))
    print_recorded_rfs()
    env = get_rf_env()
    print(env)
    
def test_rf():
    with open("tmp", "r") as f:
        lines = f.readlines()
        r, w = get_last_rf(lines)
        print(f"read: {r}, write: {w}")
    
   
        record_last_rf(lines)
        print_recorded_rfs()

def test():
    number_pairs.record_pair((3, 4))
    number_pairs.record_pair((1, 2))
    number_pairs.record_pair((3, 4))
    number_pairs.record_pair((1, 2))
    number_pairs.record_pair((3, 4))
    number_pairs.record_pair((3, 2))
    
    sorted_pairs = number_pairs.get_sorted_pairs()
    print("Sorted Pairs:")
    for pair in sorted_pairs:
        print(pair)
    
    
    sorted_pairs_with_frequency = number_pairs.get_sorted_pairs_with_frequency()
    print("Sorted Pairs with Frequency:")
    for pair, frequency in sorted_pairs_with_frequency:
        print(pair, "-", frequency)
        
    value = 3
    pairs_with_value = number_pairs.get_pairs_with_first_element(value)
    print(f"\nPairs with first element equal to {value} sorted by frequency:")
    for pair, frequency in pairs_with_value:
        print(pair, "-", frequency)

if __name__ == "__main__":
    # test()
    # test_rf()
    test_rf_env()