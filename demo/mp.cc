#include <atomic>
#include <thread>
#include <cassert>
#include <iostream>
#include <bitset>
#include <vector>

#define RLX std::memory_order_relaxed
#define REL std::memory_order_release
#define ACQ std::memory_order_acquire
#define SC  std::memory_order_seq_cst

std::atomic<int> flag = {};

void t1(int tid) {
    if (flag.load(RLX) == tid) {
        flag.store(tid + 1, REL);
    }
}

void test() {
    std::vector<std::thread> v;
    for (int i = 0; i < 5; i++) {
        v.push_back(std::thread(t1, i));
    }
    for (auto&& t : v) {
        t.join();
    }
    if (flag.load() == 4) abort();
}




int main() {

    test();

}