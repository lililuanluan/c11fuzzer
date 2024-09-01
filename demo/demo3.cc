#include "librace.h"
#include <atomic>
#include <thread>
#include <cassert>

#define RLX std::memory_order_relaxed
#define REL std::memory_order_release
#define ACQ std::memory_order_acquire
#define SC  std::memory_order_seq_cst

std::atomic<int> x;
std::atomic<int> y;

int a, b, c, d;

void t1() {
    x.store(1, SC);
}

void t2() {
    a = x.load(RLX);
    b = y.load(RLX);
}

void t3() {
    c = y.load(RLX);
    d = x.load(RLX);
}

void t4() {
    y.store(1, SC);
}

int main() {
    std::thread t_1(t1);
    std::thread t_2(t2);
    std::thread t_3(t3);
    std::thread t_4(t4);

    t_1.join();
    t_2.join();
    t_3.join();
    t_4.join();

    assert(a == 1 and b == 0 and c == 1 and d == 0);
}