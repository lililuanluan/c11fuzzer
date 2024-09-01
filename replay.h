#ifndef REPLAY_H
#define REPLAY_H
#include "config.h"
#ifdef REPLAY

#include <vector>
#include <deque>
#include <vector>
#include <iostream>
#include <cinttypes>
#include <fstream>
#include <sstream>
#include <cstring>
#include <chrono>
#include "modeltypes.h"
#include "common.h"

#include <string_view>

class Timer {
public:
    Timer() {
        m_StartTimepoint = std::chrono::high_resolution_clock::now(); 
    }
    Timer(const char* func_name) {
        m_Name = func_name;
        m_StartTimepoint = std::chrono::high_resolution_clock::now();
    }

    std::pair<double, double> Stop() {
        auto endTimepoint = std::chrono::high_resolution_clock::now();
        auto start = std::chrono::time_point_cast<std::chrono::microseconds>(m_StartTimepoint).time_since_epoch().count(); 
        auto end = std::chrono::time_point_cast<std::chrono::microseconds>(endTimepoint).time_since_epoch().count();

        double us = end - start;
        double ms = us * 0.001; 
        model_print("Timer: <%s> %.2f us (%.2f ms)\n", m_Name.c_str(), us, ms);
        return { us, ms };
    }
    ~Timer() {
        Stop();
    }
private:
    std::chrono::time_point<std::chrono::high_resolution_clock> m_StartTimepoint;
    std::string m_Name{};
};

namespace {
    const char* tmpf_in = getenv("REPLAY_TMPFILE_IN");
    const char* tmpf_out = getenv("REPLAY_TMPFILE_OUT");
}

#ifdef WRITE_ACT_SELECT
inline bool write_flag = false;
#endif

// #define REPLAY_TMPFILE_OUT "/home/vagrant/c11tester/benchmarks/tmp"
// #define REPLAY_TMPFILE_IN "/home/vagrant/c11tester/benchmarks/tmp1"

inline std::ofstream tmpf; // output

struct Replayer {



    std::deque<int> tidx;
    std::deque<int> widx;
    std::vector<std::pair<uint64_t, uint64_t> > rf_map;

    void init_rf_map() {
        const char* p = getenv("RF");

        if (p == nullptr) {
            model_print("no RF env\n");
            // getchar();
            return;
        }
        model_print("RF: %s\n", p);
        // getchar();

        char buf[4096];
        std::strcpy(buf, p);
        model_print("RF:%s\n", buf);
        // getchar();
        char* r, * w;
        char* rest = buf;
        while (r = strtok_r(rest, " ", &rest), w = strtok_r(rest, " ", &rest)) {
            model_print("r = %s\n", r);
            model_print("w = %s\n", w);
            uint64_t r_ = std::stoull(r);
            uint64_t w_ = std::stoull(w);
            model_print("toull: %llu, %llu\n", r_, w_);
            // rf_map.insert(std::make_pair(std::strtoull()))
            rf_map.push_back(std::make_pair(r_, w_));
            // getchar();
        }
        // while (ss >> r >> w, ss.good()) {
        //     // model_print("got pair {%llu, %llu}\n", r, w);
        //     getchar();
        // }
    }
    bool random_execute = true;

    void set_random_execute(bool v = true) {
        random_execute = v;
    }

    bool is_random_execute() {
        return random_execute;
    }

    enum State {
        replaying = 0,
        at_brk_point = 1,
        after_brk_point = 2,
    };

    void step() {
        static int cnt = 0;
        cnt++;
        // model_print("cnt = %d, break_point = %d\n", cnt, break_point);
        // getchar();
        if (cnt < break_point) {
            state = replaying;
        }
        else if (cnt == break_point) {
            state = at_brk_point;
        }
        else {
            state = after_brk_point;
        }
        const char* s[] = { "replaying", "at_brk_point", "after_brk_point" };
        // model_print("replayer take step: cnt = %d, state: %s\n", cnt, s[state]);
        // getchar();
    }

    State state = replaying;
    State get_state() {
        return state;
    }

    int break_point = 0;

    Replayer() {
        Timer t("ReplayerTimer");
        init();
        init_rf_map();
    }

    void init() {
        if (tmpf_out) {
            tmpf = std::ofstream(tmpf_out);
            model_print("output file: %s\n", tmpf_out);
            // getchar();
        }
        if (!tmpf_in) {
            model_print("no input file\n");
            // getchar();
        }
        else {
            random_execute = false;
            model_print("input file: %s\n", tmpf_in);
            // getchar();
        }
        std::ifstream f(tmpf_in);
        char type;
        int t;
        int w;
        while (f >> type, (type == 't' || type == 'w' || type == 'b') && f.good()) {
            if (type == 't') {
                f >> t;
                // model_print("t id: %d\n", t);
                // getchar();
                tidx.push_back(t);
            }
            if (type == 'w') {
                f >> w;
                // model_print("w: %d\n", w);
                // getchar();
                widx.push_back(w);
            }
            if (type == 'b') {  // divergence point
                f >> break_point;
                // model_print("break point: %d\n", break_point);
                // getchar();
            }

            int num_choice;
            if (type == 't' || type == 'w') {
                f >> num_choice;
                // model_print("num choices: %d\n", num_choice);
                // getchar();
            }
            if (type == 'w') {
                uint64_t rh;
                f >> rh;
                // model_print("got read hash: %llu\n", rh);
                uint64_t wh;
                while (num_choice--) {
                    f >> wh;
                    // model_print("got write hash: %llu\n", wh);
                    // getchar();
                }
            }
            if (type == 't') {
                int tid;
                while (num_choice--) {
                    f >> tid;
                }
            }

        }
        // getchar();

    }

    int get_thread() {
        auto t = tidx.front();
        tidx.pop_front();
        return t;
    }

    // bool is_break() {
    //     static int cnt = 0;
    //     cnt++;
    //     return cnt >= break_point;
    // }


    int get_write() {
        auto w = widx.front();
        widx.pop_front();
        return w;
    }

};


inline Replayer replayer{};











#endif
#endif