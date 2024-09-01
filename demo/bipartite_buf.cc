#include <atomic>
#include <thread>
#include <vector>
#include <cassert>
#include "bipartite_buf-bak.hpp"

lockfree::spsc::BipartiteBuf<unsigned int, 1024U> bb;
std::vector<unsigned int> written;
std::vector<unsigned int> read;

const size_t data_size = 59; // Intentionally a prime number

#define TEST_MT_TRANSFER_CNT 256

void consumer() {
    size_t read_count = 0;
    do {
        std::pair<unsigned int*, size_t> read_region = bb.ReadAcquire();
        if (read_region.second) {
            read.insert(read.end(), &read_region.first[0],
                &read_region.first[read_region.second]);
            bb.ReadRelease(read_region.second);
            read_count += read_region.second;
        }
    } while (read_count < TEST_MT_TRANSFER_CNT);
}


void producer() {
    unsigned int data[data_size] = { 0 };
    for (unsigned int i = 0; i < data_size; i++) {
        data[i] = rand();
    }

    size_t write_count = 0;
    do {
        unsigned int* write_region = bb.WriteAcquire(data_size);
        if (write_region != nullptr) {
            std::copy(&data[0], &data[data_size], write_region);
            bb.WriteRelease(data_size);
            written.insert(written.end(), &data[0], &data[data_size]);
            write_count += data_size;
        }
    } while (write_count < TEST_MT_TRANSFER_CNT);
}

int main() {
    std::thread t1(producer);
    std::thread t2(consumer);
    t1.join();
    t2.join();
    assert(std::equal(std::begin(written), std::end(written), std::begin(read)));
}