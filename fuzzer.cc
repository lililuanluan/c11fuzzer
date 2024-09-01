#include "fuzzer.h"
#include <stdlib.h>
#include <fstream>
#include <cassert>
#include "threads-model.h"
#include "model.h"
#include "action.h"


#ifdef REPLAY
#include "replay.h"




static void print_rf_set(ModelAction* read, SnapVector<ModelAction*>* rf_set) {

	model_print("[%d selectWrite from %d]: \n", read->get_seq_number(), rf_set->size());
	for (uint i = 0; i < rf_set->size(); i++) {
		model_print(GREEN("\t[%u]")": %#llx, value: %u\n", i, (*rf_set)[i]->get_position_hash(), (*rf_set)[i]->get_write_value());
	}
	model_print("\n");
}

void print_threadlist(int* threadlist, int numthreads) {
	model_print("fuzzer selecting from %d threads\n", numthreads);
	for (int i = 0; i < numthreads; i++) {
		model_print(GREEN("\t[%d]")": thread %d\n", i, threadlist[i]);
	}
	// getchar();
}

#endif	// REPLAY


#ifdef REPLAY

// random selecting functions
static
int selectThreadRand(int* threadlist, int numthreads) {
	int random_index = random() % numthreads;
	return random_index;
	// int thread = threadlist[random_index];
	// thread_id_t curr_tid = int_to_id(thread);
	// #ifdef REPLAY
	// 	model_print("fuzzer select thread %d\n", thread);
	// 	tmpf << "t  " << threadlist[random_index] << std::endl;
	// #endif
	// return model->get_thread(curr_tid);
}
static
int selectWriteRand(ModelAction* read, SnapVector<ModelAction*>* rf_set) {
	int random_index = random() % rf_set->size();
	return random_index;
}


static void log_select_thread(int idx, int* threadlist, int numthreads) {
	if (idx >= numthreads) {
		model_print("idx = %d, thrd size = %d, \n", idx, numthreads);
		getchar();
	}
	tmpf << "t " << idx << " " << numthreads;
	// tmpf << " " << model->get_current_thread_id();
	for (int i = 0; i < numthreads; i++) {
		tmpf << " " << threadlist[i];
	}
	tmpf << std::endl;
	// tmpf << '\n';
}
static void log_select_write(ModelAction* read, int idx, SnapVector<ModelAction*>* rf_set) {
	if (idx >= (int)rf_set->size()) {
		model_print("idx = %d, rf size = %d\n", idx, rf_set->size());
		getchar();
	}
	tmpf << "w " << idx << " " << rf_set->size();
	tmpf << " " << read->get_position_hash() << " ";
	for (int i = 0; i < rf_set->size(); i++) {
		tmpf << " " << rf_set->at(i)->get_position_hash();
	}
	tmpf << std::endl;
	// tmpf << '\n';
}

// ------------ fuzzer select thread ------------------
Thread* Fuzzer::selectThread(int* threadlist, int numthreads) {

	// model_print("fuzzer selectThread\n");
	// print_threadlist(threadlist, numthreads);
#ifdef INTERACT
	int idx;
	scanf("%d", &idx);
	tmpf << "t  " << threadlist[idx] << std::endl;
	return model->get_thread(threadlist[idx]);
#else
	if (replayer.is_random_execute()) {
		// model_print(GREEN("is random execution\n"));
		// getchar();
		auto idx = selectThreadRand(threadlist, numthreads);

		log_select_thread(idx, threadlist, numthreads);
		// tmpf << "t  " << t->get_id() << " " << numthreads << std::endl;
		// model_print("selected idx = %d\n", idx);
		return model->get_thread(threadlist[idx]);
	}

	replayer.step();


	switch (replayer.get_state())
	{
	case Replayer::State::replaying: {
		auto idx = replayer.get_thread();
		log_select_thread(idx, threadlist, numthreads);
		return model->get_thread(threadlist[idx]);
		// model_print("target tid: %d\n", tid);
		// for (int i = 0; i < numthreads; i++) {
		// 	thread_id_t curr_tid = int_to_id(threadlist[i]);
		// 	if (tid == curr_tid) {
		// 		// model_print("selected i-th thread: %d\n", i);
		// 		model_print(GREEN("got target thread!\n"));
		// 		// tmpf << "t  " << threadlist[i] << " " << numthreads << std::endl;
		// 		log_select_thread(threadlist[i], threadlist, numthreads);
		// 		// getchar();
		// 		return model->get_thread(curr_tid);
		// 	}
		// }
		// model_print(RED("didn't get target thread\n"));
		// getchar();
		break;
	}

	case Replayer::State::at_brk_point:
		// {
		// 	model_print(GREEN("at break point\n"));
		// 	assert(numthreads != 1);
		// 	auto tid = replayer.get_thread();
		// 	Thread* t = nullptr;
		// 	while (1) {
		// 		t = selectThreadRand(threadlist, numthreads);
		// 		if (t->get_id() != tid) break;
		// 	}
		// 	tmpf << "t  " << t->get_id() << " " << numthreads << std::endl;
		// 	return t;
		// }

										  // getchar();

	case Replayer::State::after_brk_point:
		auto idx = selectThreadRand(threadlist, numthreads);
		// tmpf << "t  " << t->get_id() << " " << numthreads << std::endl;
		log_select_thread(idx, threadlist, numthreads);
		return model->get_thread(threadlist[idx]);


	}



#endif
}




// -------------- fuzzer select write ---------------
int Fuzzer::selectWrite(ModelAction* read, SnapVector<ModelAction*>* rf_set) {

	// model_print("fuzzer selectWrite\n");
	// getchar();
	// print_rf_set(read, rf_set);
	// model_print("select index: ");
#ifdef INTERACT
	int indx;
	scanf("%d", &indx);
	tmpf << "w  " << std::hex << rf_set->at(indx)->get_position_hash() << "\n" << std::dec;;
	return indx;
#else
	static int flag = 0;
	// ---- prioritize rf in rf_map
#ifdef PRIORITIZE_RF_MAP
	for (auto&& rf : replayer.rf_map) {
		if (read->get_position_hash() == rf.first) {
			for (int i = 0; i < rf_set->size(); i++) {
				if (rf_set->at(i)->get_position_hash() == rf.second) {
					model_print("can select an rf in rf_map: %llu, %llu\n", rf.first, rf.second);
					// getchar();
					if (rand() % 2 > 0) {
						replayer.set_random_execute();
						log_select_write(read, i, rf_set);
						// getchar();
						flag++;
						return i;
					}

				}
			}
		}
	}
#endif



	if (replayer.is_random_execute()) {
		// model_print(GREEN("is random execution\n"));
		// getchar();
		auto idx = selectWriteRand(read, rf_set);
		// auto hash = rf_set->at(idx)->get_position_hash();
		// tmpf << "w  " << idx << " " << rf_set->size() << std::endl;
		log_select_write(read, idx, rf_set);

		return idx;
	}

	replayer.step();

	switch (replayer.get_state())
	{
	case Replayer::State::replaying: {
		auto w = replayer.get_write();
		log_select_write(read, w, rf_set);
		// tmpf << "w  " << w << " " << rf_set->size() << std::endl;
		// for (int i = 0; i < rf_set->size(); i++) {
		// 	auto hash = rf_set->at(i)->get_position_hash();
		// 	if (hash == w) {
		// 		// model_print("selected [%d]: %llu\n", i, hash);
		// 		model_print(GREEN("got target write!\n"));
		// 		getchar();
		// 		tmpf << "w  " << std::hex << hash << std::dec << " " << rf_set->size() << std::endl;
		// 		return i;
		// 	}

		// }
		return w;
		model_print(RED("didn't get target write\n"));
		// getchar();
		break;
	}

	case Replayer::State::at_brk_point:
		// {
		// 	model_print(GREEN("at break point\n"));
		// 	assert(rf_set->size() != 1);
		// 	auto w = replayer.get_write();
		// 	int idx;
		// 	while (true) {
		// 		idx = selectWriteRand(read, rf_set);
		// 		if (idx != w) { break; }
		// 	}
		// 	log_select_write(read, idx, rf_set);
		// 	// tmpf << "w  " << idx << " " << rf_set->size() << std::endl;
		// 	return idx;
		// 	// getchar();
		// }


	case Replayer::State::after_brk_point:
#ifdef PRIORITIZE_RF_MAP
		// ---- prioritize rf in rf_map
		for (auto&& rf : replayer.rf_map) {
			if (read->get_position_hash() == rf.first) {
				for (int i = 0; i < rf_set->size(); i++) {
					if (rf_set->at(i)->get_position_hash() == rf.second) {
						model_print("can select an rf in rf_map: %llu, %llu\n", rf.first, rf.second);
						// getchar();
						if (rand() % 5 > 0) {
							// replayer.set_random_execute();
							log_select_write(read, i, rf_set);
							flag++;
							return i;
						}

					}
				}
			}
		}
#endif
		// ---------------


		auto idx = selectWriteRand(read, rf_set);
		// tmpf << "w  " << idx << " " << rf_set->size() << std::endl;
		log_select_write(read, idx, rf_set);
		return idx;


	}


#endif	// INTERACT

}


#else 

Thread* Fuzzer::selectThread(int* threadlist, int numthreads) {
	int random_index = random() % numthreads;
	int thread = threadlist[random_index];
	thread_id_t curr_tid = int_to_id(thread);
	// #ifdef REPLAY
	// 	model_print("fuzzer select thread %d\n", thread);
	// 	tmpf << "t  " << threadlist[random_index] << std::endl;
	// #endif
	return model->get_thread(curr_tid);
}
int Fuzzer::selectWrite(ModelAction* read, SnapVector<ModelAction*>* rf_set) {
	// model_print("rf set has: %d\n", rf_set->size());
	// for(uint i=0; i<rf_set->size();i++) {
	// 	if(rf_set->at(i)->get_mo() == std::memory_order_relaxed ) {
	// 		model_print("has relaxed, %d\n", i);
	// 		// getchar();
	// 		return i;
	// 	}
	// }
	int random_index = random() % rf_set->size();
	return random_index;
}


#endif	// REPLAY

// Thread* Fuzzer::selectThread(int* threadlist, int numthreads) {
// #ifdef REPLAY
// 	model_print("fuzzer selectThread\n");
// 	print_threadlist(threadlist, numthreads);
// #ifdef INTERACT
// 	int idx;
// 	scanf("%d", &idx);
// 	tmpf << "t  " << threadlist[idx] << std::endl;
// 	return model->get_thread(threadlist[idx]);
// #else
// 	if (!replayer.random_execute && !replayer.is_break()) {
// 		auto tid = replayer.get_thread();
// 		model_print("target tid: %d\n", tid);
// 		for (int i = 0; i < numthreads; i++) {
// 			thread_id_t curr_tid = int_to_id(threadlist[i]);
// 			if (tid == curr_tid) {
// 				model_print("selected i-th thread: %d\n", i);
// 				return model->get_thread(curr_tid);
// 			}
// 		}
// 		abort();
// 	}

// #endif

// #endif
// 	int random_index = random() % numthreads;
// 	int thread = threadlist[random_index];
// 	thread_id_t curr_tid = int_to_id(thread);
// #ifdef REPLAY
// 	model_print("fuzzer select thread %d\n", thread);
// 	tmpf << "t  " << threadlist[random_index] << std::endl;
// #endif
// 	return model->get_thread(curr_tid);
// }




Thread* Fuzzer::selectNotify(simple_action_list_t* waiters) {
#ifdef REPLAY
	model_print("select notify\n");
	GETCHAR
#endif
		int numwaiters = waiters->size();
	int random_index = random() % numwaiters;
	sllnode<ModelAction*>* it = waiters->begin();
	while (random_index--)
		it = it->getNext();
	Thread* thread = model->get_thread(it->getVal());
	waiters->erase(it);
	return thread;
}

bool Fuzzer::shouldSleep(const ModelAction* sleep) {
	return true;
}

bool Fuzzer::shouldWake(const ModelAction* sleep) {
	struct timespec currtime;
	clock_gettime(CLOCK_MONOTONIC, &currtime);
	uint64_t lcurrtime = currtime.tv_sec * 1000000000 + currtime.tv_nsec;

	return ((sleep->get_time() + sleep->get_value()) < lcurrtime);
}

/* Decide whether wait should spuriously fail or not */
bool Fuzzer::waitShouldFail(ModelAction* wait)
{
#ifdef REPLAY
	model_print("wait should fail\n");
	GETCHAR
#endif
		if ((random() & 1) == 0) {
			struct timespec currtime;
			clock_gettime(CLOCK_MONOTONIC, &currtime);
			uint64_t lcurrtime = currtime.tv_sec * 1000000000 + currtime.tv_nsec;

			// The time after which wait fail spuriously, in nanoseconds
			uint64_t time = random() % 1000000;
			wait->set_time(time + lcurrtime);
			return true;
		}

	return false;
}

bool Fuzzer::waitShouldWakeUp(const ModelAction* wait)
{
	struct timespec currtime;
	clock_gettime(CLOCK_MONOTONIC, &currtime);
	uint64_t lcurrtime = currtime.tv_sec * 1000000000 + currtime.tv_nsec;

	return (wait->get_time() < lcurrtime);
}

bool Fuzzer::randomizeWaitTime(ModelAction* timed_wait)
{
#ifdef REPLAY
	// model_print("random wait time\n");
	// GETCHAR
#endif
		uint64_t abstime = timed_wait->get_time();
	struct timespec currtime;
	clock_gettime(CLOCK_MONOTONIC, &currtime);
	uint64_t lcurrtime = currtime.tv_sec * 1000000000 + currtime.tv_nsec;
	if (abstime <= lcurrtime)
		return false;

	// Shorten wait time
	if ((random() & 1) == 0) {
		uint64_t tmp = abstime - lcurrtime;
		uint64_t time_to_expire = random() % tmp + lcurrtime;
		timed_wait->set_time(time_to_expire);
	}

	return true;
}
