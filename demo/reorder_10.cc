#include <vector>
#include <thread>
#include <cassert>
#include "cds_threads.h"
#include <iostream>
#include <atomic>
#include "model-assert.h"
#include "librace.h"
#include <mutex>
#include <cstdlib>

constexpr int RND[] = { 108, 198, 75, 122, 169, 164, 131, 61, 65, 186, 143, 135, 65, 76, 99, 60, 98, 95, 49, 9, 19, 31, 66, 140, 112, 57, 14, 143, 30, 41, 142, 90, 38, 17, 11, 158, 132, 93, 170, 197, 79, 112, 131, 143, 140, 182, 154, 37, 76, 154, 197, 46, 136, 62, 138, 47, 71, 103, 141, 100, 143, 83, 141, 132, 51, 103, 89, 182, 196, 11, 178, 26, 122, 61, 168, 13, 42, 74, 1, 69, 179, 150, 66, 115, 11, 3, 113, 33, 58, 54, 133, 152, 136, 25, 84, 138, 128, 124, 119, 123 };

#define TEST_RAND 0

std::atomic<int> a, b;
std::mutex mtx;

void setThread(int i) {
#if TEST_RAND
    a.store(RND[i * 2], std::memory_order_seq_cst);
    b.store(RND[i * 2 + 1] % 100 + 1, std::memory_order_seq_cst);
    // a.store(rand() % 100 + 1, std::memory_order_seq_cst);
    // b.store(rand() % 100 + 1, std::memory_order_seq_cst);
#else
    a.store(1, std::memory_order_seq_cst);
    b.store(-1, std::memory_order_seq_cst);
#endif
}




void checkThread() {
#if TEST_RAND
    // auto a_ = a.load();
    // auto b_ = b.load();
    // if (!((a_ == 0 && b_ == 0) || (a_ != 0 && b_ != 0))) {


    if (!((a.load() == 0 && b.load() == 0) || (a.load() != 0 && b.load() != 0))) {
        // if ((a_ == 0 && b_ != 0) || (a_ != 0 && b_ == 0)) {
        printf("BUG FOUND NO\n");
        MODEL_ASSERT(0); // Bug found
    }
#else
    if (!((a.load() == 0 && b.load() == 0) || (a.load() == 1 && b.load() == -1))) {
        fprintf(stderr, "BUG FOUND NO\n");
        MODEL_ASSERT(0); // Bug found
    }
#endif
}




int main() {
#if TEST_RAND
    // srand(time(NULL));
#endif
    a = 0;
    b = 0;
    const int n = 10;
    std::vector<std::thread> st;
    for (int i = 0; i < n; ++i) {
        st.emplace_back(setThread, i);
    }
    std::thread ct(checkThread);
    ct.join();
    for (int i = 0; i < n; ++i) {
        st[i].join();
    }
    return 0;
}