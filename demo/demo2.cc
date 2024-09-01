#include "librace.h"
#include <atomic>
#include <thread>

#define RLX std::memory_order_relaxed
#define REL std::memory_order_release
#define ACQ std::memory_order_acquire
#define SC  std::memory_order_seq_cst

uint8_t data = {};
std::atomic<int> flag = { 1 };

// thread 2
void t2() {
    auto _ = flag.load(ACQ);
    store_8(&data, 0);          // cds_store8    
    flag.store(1, REL);
}

// thread 3
void t3() {
    if (flag.load(ACQ))
        store_8(&data, 1);
}

// thread 1
int main() {
    std::thread t_2(t2);

    std::thread t_3(t3);

    t_2.join();
    t_3.join();
}