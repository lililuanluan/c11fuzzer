
#include <errno.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <pthread.h>
#include <atomic>
#include <cassert>

static std::atomic<size_t> sum;
static std::atomic<size_t> dif;


#define ORDER std::memory_order_relaxed
// #define ORDER std::memory_order_seq_cst 









#line 20
static void* sub_worker(void* arg) {
    if (sum.load(ORDER) == 1) { // 12509095658903305407
        dif.fetch_sub(1, ORDER); // 5604351433223617936
        if (sum.load(ORDER) == 2) { // 9145372461014558573
            dif.fetch_sub(1, ORDER);    // 9795771407245830963
        }
    }

    return NULL;
}





#line 37
static void* add_worker(void* arg)
{
    sum.fetch_add(1, ORDER); // 13908578951258756704

    if (dif.load(ORDER) == -1) {    // 1743720903142651214
        sum.fetch_add(1, ORDER);    // 7753569527864603567
        if (dif.load(ORDER) == -2) {    // 12925955884095687375
            fprintf(stderr, "Bug found\n");
            abort();
        }
    }

    return NULL;
}

// requires: add -> sub -> add -> sub -> add -> sub ...

int main(int argc, char** argv)
{
    int n = 2;
#line 65
    sum.store(0);   // 14935894086998972344
    dif.store(0);   // 14889444969647379617

    pthread_t adder;
    pthread_t suber;
    pthread_create(&adder, NULL, add_worker, NULL);
    pthread_create(&suber, NULL, sub_worker, NULL);
    pthread_join(adder, NULL);
    pthread_join(suber, NULL);

    printf("sum = %zu\n", sum.load()); // 4198890
    return 0;
}

