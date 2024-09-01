#include <atomic>
#include <thread>
#include <cassert>
#include <iostream>
// #include <stdio.h>


#define RLX std::memory_order_relaxed
#define REL std::memory_order_release
#define ACQ std::memory_order_acquire
#define SC  std::memory_order_seq_cst

std::atomic<int> var = {};


// thread 2
void t2() {
    // auto _1 = var.load(SC);
    // auto _2 = var.load(ACQ);
    var.store(1, REL);
    // printf("t2: %d\n", var.load(ACQ));
    var.store(2, REL);
}

// thread 3
void t3() {
    // var.store(1, REL);
    // var.store(2, SC);
    // var = 0;
    // var.store(1, SC);
    // var.store(2, REL);
    // var.store(3, REL);
    // var.store(2, REL);

    auto r1 = var.load(ACQ);

    auto r2 = var.load(ACQ);
    // printf("t3: %d\n", var.load(ACQ));
    // assert(r2 != 2);
    assert(!(r1 == 2 && r2 == 1));
}

// thread 1
int main() {
    std::thread t_2(t2);
    std::thread t_3(t3);

    t_2.join();
    t_3.join();
}


