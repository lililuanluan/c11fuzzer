
#include <errno.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <pthread.h>
#include <atomic>
#include <cassert>

static std::atomic<size_t> sum{ 0 };
static std::atomic<size_t> dif{ 0 };


#define ORDER std::memory_order_relaxed
// #define ORDER std::memory_order_seq_cst 


static void* sub_worker(void* arg) {
    if (sum.load(ORDER) == 1) {
        dif.fetch_sub(1, ORDER);
        if (sum.load(ORDER) == 2) {
            dif.fetch_sub(1, ORDER);
            if (sum.load(ORDER) == 3) {
                dif.fetch_sub(1, ORDER);
                if (sum.load(ORDER) == 4) {
                    dif.fetch_sub(1, ORDER);
                }
            }
        }
    }
    return NULL;
}

static void* add_worker(void* arg)
{
    sum++;

    if (dif.load(ORDER) == -1) {
        sum.fetch_add(1, ORDER);
        if (dif.load(ORDER) == -2) {
            sum.fetch_add(1, ORDER);
            if (dif.load(ORDER) == -3) {
                sum.fetch_add(1, ORDER);
                if (dif.load(ORDER) == -4) {
                    fprintf(stderr, "Bug found\n");
                    abort();
                }
            }
        }
    }

    return NULL;
}

// requires: add -> sub -> add -> sub -> add -> sub ...

int main(int argc, char** argv)
{
    int n = 2;

    pthread_t adder;
    pthread_t suber;
    pthread_create(&adder, NULL, add_worker, NULL);
    pthread_create(&suber, NULL, sub_worker, NULL);
    pthread_join(adder, NULL);
    pthread_join(suber, NULL);

    printf("sum = %zu\n", sum.load()); // 4198890
    return 0;
}

