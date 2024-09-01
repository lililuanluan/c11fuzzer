#include <algorithm>
#include <math.h>
#include <thread>
#include "prio_queue.hpp"

lockfree::spsc::PriorityQueue<uint64_t, 10, 4> queue;
std::vector<uint64_t> written;
std::vector<uint64_t> read;
#define TEST_MT_TRANSFER_CNT 100
void consumer() {
    uint64_t value = 0;
        uint64_t cnt = 0;
        do {
            bool pop_success = queue.Pop(value);
            if (pop_success) {
                read.push_back(value);
                cnt++;
            }
        } while (cnt < TEST_MT_TRANSFER_CNT);
}

void producer() {
     uint64_t cnt = 0;
        uint64_t value = 0;
        uint8_t prio = 0;
        do {
            value = cnt << 2 + prio;
            bool push_success = queue.Push(value, prio);
            if (push_success) {
                written.push_back(value);
                prio = (prio + 1) % 4; // this could be also randomly generated
                cnt++;
            }
        } while (cnt < TEST_MT_TRANSFER_CNT + 1);
}

int main() {
    std::thread t1(producer);
    std::thread t2(consumer);
    t1.join();
    t2.join();
    assert(std::equal(std::begin(written), std::end(written), std::begin(read)));
}