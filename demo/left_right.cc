#include <random>
#include <thread>
#include <vector>

#include "left_right.hpp"

constexpr int MaxIterations = 20;
xenium::left_right<int> lr{ 0 };


void worker(int i, int max_it) {

    int last_value = 0;
    for (int j = 0; j < 3; j++) {
        lr.update([](int& v) { ++v; });
        lr.read([&last_value](const int& v) {
            // EXPECT_GE(v, last_value);
            assert(v >= last_value);
            last_value = v; });
    }

    // for (int j = 0; j < MaxIterations; ++j) {
    //     int last_value = 0;
    //     if (j % 3 == 0) {
    //         lr.update([](int& v) { ++v; });
    //     }
    //     else {
    //         lr.read([&last_value](const int& v) {
    //             // EXPECT_GE(v, last_value);
    //             assert(v >= last_value);
    //             last_value = v;
    //             });
    //     }
    // }

}



int main() {
    std::vector<std::thread> threads;
    for (int i = 0; i < 2; ++i) {
        threads.push_back(std::thread(worker, i, MaxIterations));
    }
    for (auto& thread : threads) {
        thread.join();
    }

}