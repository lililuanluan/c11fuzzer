#include <atomic>
#include <thread>
#include <cassert>
#include <stdio.h>

std::atomic<size_t> sum;
std::atomic<size_t> dif;
int input = 100;

void sub_worker() {
    for (int i = 0; i < input; i++) {
        dif = dif.load() - 1;   // --
        sum = sum.load() - 1;
    }
}

void add_worker() {
    for (int i = 0; i < input; i++) {
        dif = dif.load() + 1;   // --
        sum = sum.load() + 1;
    }
}

int main() {
    sum = 0;
    dif = 0;
    std::thread t1(sub_worker);
    std::thread t2(add_worker);

    t1.join();
    t2.join();
    assert(dif.load() <= 4);
    return 0;
}