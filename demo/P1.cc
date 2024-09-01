#include <atomic>
#include <thread>
#include <cassert>

std::atomic<int> X;
constexpr int k = 10;

void set() {
    for (int i = 1; i <= k; i++) {
        X.store(i);
    }
}

void check() {
    assert(X.load() != k);
}

int main() {
    X.store(0);
    std::thread t1(set);
    std::thread t2(check);

    t1.join();
    t2.join();
}