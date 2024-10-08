#include <string.h>
#include <stdlib.h>

#include "threads-model.h"
#include "schedule.h"
#include "common.h"
#include "model.h"
#include "execution.h"
#include "fuzzer.h"

/**
 * Format an "enabled_type_t" for printing
 * @param e The type to format
 * @param str The output character array
 */
void enabled_type_to_string(enabled_type_t e, char* str)
{
	const char* res;
	switch (e) {
	case THREAD_DISABLED:
		res = "disabled";
		break;
	case THREAD_ENABLED:
		res = "enabled";
		break;
	case THREAD_SLEEP_SET:
		res = "sleep";
		break;
	default:
		ASSERT(0);
		res = NULL;
		break;
	}
	strcpy(str, res);
}

/** Constructor */
Scheduler::Scheduler() :
	execution(NULL),
	enabled(NULL),
	enabled_len(0),
	curr_thread_index(0),
	current(NULL)
{
}

/**
 * @brief Register the ModelExecution engine
 * @param execution The ModelExecution which is controlling execution
 */
void Scheduler::register_engine(ModelExecution* execution)
{
	this->execution = execution;
}

void Scheduler::set_enabled(Thread* t, enabled_type_t enabled_status) {
	int threadid = id_to_int(t->get_id());
	if (threadid >= enabled_len) {
		enabled_type_t* new_enabled = (enabled_type_t*)snapshot_malloc(sizeof(enabled_type_t) * (threadid + 1));
		real_memset(&new_enabled[enabled_len], 0, (threadid + 1 - enabled_len) * sizeof(enabled_type_t));
		if (enabled != NULL) {
			real_memcpy(new_enabled, enabled, enabled_len * sizeof(enabled_type_t));
			snapshot_free(enabled);
		}
		enabled = new_enabled;
		enabled_len = threadid + 1;
	}
	enabled[threadid] = enabled_status;
}

/**
 * @brief Check if a Thread is currently enabled
 *
 * Check if a Thread is currently enabled. "Enabled" includes both
 * THREAD_ENABLED and THREAD_SLEEP_SET.
 * @param t The Thread to check
 * @return True if the Thread is currently enabled
 */
bool Scheduler::is_enabled(const Thread* t) const
{
	return is_enabled(t->get_id());
}

/**
 * @brief Check if a Thread is currently enabled
 *
 * Check if a Thread is currently enabled. "Enabled" includes both
 * THREAD_ENABLED and THREAD_SLEEP_SET.
 * @param tid The ID of the Thread to check
 * @return True if the Thread is currently enabled
 */
bool Scheduler::is_enabled(thread_id_t tid) const
{
	int i = id_to_int(tid);
	return (i >= enabled_len) ? false : (enabled[i] != THREAD_DISABLED);
}

/**
 * @brief Check if a Thread is currently in the sleep set
 * @param t The Thread to check
 */
bool Scheduler::is_sleep_set(const Thread* t) const
{
	return is_sleep_set(t->get_id());
}

bool Scheduler::is_sleep_set(thread_id_t tid) const
{
	int id = id_to_int(tid);
	ASSERT(id < enabled_len);
	return enabled[id] == THREAD_SLEEP_SET;
}

/**
 * @brief Check if execution is stuck with no enabled threads and some sleeping
 * thread
 * @return True if no threads are enabled and some thread is in the sleep set;
 * false otherwise
 */
bool Scheduler::all_threads_sleeping() const
{
	bool sleeping = false;
	for (int i = 0; i < enabled_len; i++)
		if (enabled[i] == THREAD_ENABLED)
			return false;
		else if (enabled[i] == THREAD_SLEEP_SET)
			sleeping = true;
	return sleeping;
}

enabled_type_t Scheduler::get_enabled(const Thread* t) const
{
	int id = id_to_int(t->get_id());
	ASSERT(id < enabled_len);
	return enabled[id];
}

/**
 * Add a Thread to the sleep set.
 * @param t The Thread to add
 * A Thread is in THREAD_SLEEP_SET if it is sleeping or blocked by a wait
 * operation that should fail spuriously (decide by fuzzer).
 */
void Scheduler::add_sleep(Thread* t)
{
	DEBUG("thread %d\n", id_to_int(t->get_id()));
	set_enabled(t, THREAD_SLEEP_SET);
}

/**
 * Remove a Thread from the sleep set.
 * @param t The Thread to remove
 */
void Scheduler::remove_sleep(Thread* t)
{
	DEBUG("thread %d\n", id_to_int(t->get_id()));
	set_enabled(t, THREAD_ENABLED);
}

/**
 * Add a Thread to the scheduler's ready list.
 * @param t The Thread to add
 */
void Scheduler::add_thread(Thread* t)
{
#ifdef REPLAY
	// model_print("add thread %d\n", id_to_int(t->get_id()));
	// GETCHAR
#endif
	DEBUG("thread %d\n", id_to_int(t->get_id()));
	ASSERT(!t->is_model_thread());
	set_enabled(t, THREAD_ENABLED);
}

/**
 * Remove a given Thread from the scheduler.
 * @param t The Thread to remove
 */
void Scheduler::remove_thread(Thread* t)
{
	if (current == t)
		current = NULL;
	set_enabled(t, THREAD_DISABLED);
}

/**
 * Prevent a Thread from being scheduled. The sleeping Thread should be
 * re-awoken via Scheduler::wake.
 * @param thread The Thread that should sleep
 */
void Scheduler::sleep(Thread* t)
{
	set_enabled(t, THREAD_DISABLED);
	t->set_state(THREAD_BLOCKED);
}

/**
 * Wake a Thread up that was previously waiting (see Scheduler::wait)
 * @param t The Thread to wake up
 */
void Scheduler::wake(Thread* t)
{
	ASSERT(!t->is_model_thread());
	set_enabled(t, THREAD_ENABLED);
	t->set_state(THREAD_READY);
}

/**
 * @brief Select a Thread to run via round-robin
 *
 *
 * @return The next Thread to run
 */
Thread* Scheduler::select_next_thread()
{
#ifdef REPLAY
	// model_print("scheduler select next thread\n");
	// GETCHAR
#endif
	int avail_threads = 0;
	int sleep_threads = 0;
	int thread_list[enabled_len], sleep_list[enabled_len];
	Thread* thread;

	for (int i = 0; i < enabled_len; i++) {
		if (enabled[i] == THREAD_ENABLED)
			thread_list[avail_threads++] = i;
		else if (enabled[i] == THREAD_SLEEP_SET)
			sleep_list[sleep_threads++] = i;
	}

	if (avail_threads == 0 && !execution->getFuzzer()->has_paused_threads()) {
		if (sleep_threads != 0) {
			// No threads available, but some threads sleeping. Wake up one of them
			thread = execution->getFuzzer()->selectThread(sleep_list, sleep_threads);
			remove_sleep(thread);
			thread->set_wakeup_state(true);
		}
		else {
#ifndef REPLAY
			model_print("selected null\n");
#endif
			return NULL;	// No threads available and no threads sleeping.
		}
	}
	else {
#ifdef REPLAY
		// model_print("scheduler calls fuzzer to select\n");
		// GETCHAR
#endif
		// Some threads are available
		thread = execution->getFuzzer()->selectThread(thread_list, avail_threads);
	}
#ifdef REPLAY
	// model_print("scheduler selected next thread %d\n", id_to_int(thread->get_id()));
	// GETCHAR
#endif
	//curr_thread_index = id_to_int(thread->get_id());
	return thread;
}

void Scheduler::set_scheduler_thread(thread_id_t tid) {
	curr_thread_index = id_to_int(tid);
}

/**
 * @brief Set the current "running" Thread
 * @param t Thread to run
 */
void Scheduler::set_current_thread(Thread* t)
{
	ASSERT(!t || !t->is_model_thread());

	current = t;
	if (DBG_ENABLED())
		print();
}

/**
 * @return The currently-running Thread
 */
Thread* Scheduler::get_current_thread() const
{
	ASSERT(!current || !current->is_model_thread());
	return current;
}

/**
 * Print debugging information about the current state of the scheduler. Only
 * prints something if debugging is enabled.
 */
void Scheduler::print() const
{
	int curr_id = current ? id_to_int(current->get_id()) : -1;

	model_print("Scheduler: ");
	for (int i = 0; i < enabled_len; i++) {
		char str[20];
		enabled_type_to_string(enabled[i], str);
		model_print("[%i: %s%s]", i, i == curr_id ? "current, " : "", str);
	}
	model_print("\n");
}


