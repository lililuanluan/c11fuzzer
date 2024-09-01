#include <thread>
#include <atomic>
#include <vector>
#include <assert.h>
#include "ring_buf.hpp"
/*
TEST_CASE("spsc::RingBuf - Multithreaded read/write", "[rb_multithread]") {
    std::vector<std::thread> threads;
    lockfree::spsc::RingBuf<uint64_t, 1024U> rb;
    std::vector<uint64_t> written;
    std::vector<uint64_t> read;

    // consumer
    threads.emplace_back([&]() {
        uint64_t data[1] = {0};
        do {
            bool read_success = rb.Read(data, 1);
            if (read_success) {
                read.push_back(data[0]);
            }
        } while (data[0] < TEST_MT_TRANSFER_CNT);
    });
    // producer
    threads.emplace_back([&]() {
        uint64_t cnt = 0;
        do {
            bool write_success = rb.Write(&cnt, 1);
            if (write_success) {
                written.push_back(cnt);
                cnt++;
            }
        } while (cnt < TEST_MT_TRANSFER_CNT + 1);
    });
    for (auto &t : threads) {
        t.join();
    }
    REQUIRE(
        std::equal(std::begin(written), std::end(written), std::begin(read)));
}
*/


#define TEST_MT_TRANSFER_CNT 1024
lockfree::spsc::RingBuf<uint64_t, 1024U> rb;
std::vector<uint64_t> read;
std::vector<uint64_t> written;

void consumer() {
    uint64_t data[1] = { 0 };
    do {
        bool read_success = rb.Read(data, 1);
        if (read_success) {
            read.push_back(data[0]);
        }
    } while (data[0] < TEST_MT_TRANSFER_CNT);
}

void producer() {
    uint64_t cnt = 0;
    do {
        bool write_success = rb.Write(&cnt, 1);
        if (write_success) {
            written.push_back(cnt);
            cnt++;
        }
    } while (cnt < TEST_MT_TRANSFER_CNT + 1);
}

int main() {
    // std::vector<std::thread> threads;




    std::thread t1(producer);
    std::thread t2(consumer);
    t1.join();
    t2.join();
    assert(std::equal(std::begin(written), std::end(written), std::begin(read)));
}