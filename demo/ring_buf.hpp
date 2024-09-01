/**************************************************************
 * @file ring_buf.hpp
 * @brief A ring buffer implementation written in standard
 * c++11 suitable for both low-end microcontrollers all the way
 * to HPC machines. Lock-free for single consumer single
 * producer scenarios.
 **************************************************************/

 /**************************************************************
  * Copyright (c) 2023 Djordje Nedic
  *
  * Permission is hereby granted, free of charge, to any person
  * obtaining a copy of this software and associated
  * documentation files (the "Software"), to deal in the Software
  * without restriction, including without limitation the rights
  * to use, copy, modify, merge, publish, distribute, sublicense,
  * and/or sell copies of the Software, and to permit persons to
  * whom the Software is furnished to do so, subject to the
  * following conditions:
  *
  * The above copyright notice and this permission notice shall
  * be included in all copies or substantial portions of the
  * Software.
  *
  * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
  * KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
  * WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
  * PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
  * COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
  * OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
  *
  * This file is part of lockfree
  *
  * Author:          Djordje Nedic <nedic.djordje2@gmail.com>
  * Version:         v2.0.8
  **************************************************************/

  /************************** INCLUDE ***************************/
#ifndef LOCKFREE_RING_BUF_HPP
#define LOCKFREE_RING_BUF_HPP

#include <array>
#include <atomic>
#include <cstddef>
#include <type_traits>

#include <cstring>

#if __cplusplus >= 202002L || (defined(_MSVC_LANG) && _MSVC_LANG >= 202002L)
#include <span>
#endif

namespace lockfree {
    namespace spsc {
        /*************************** TYPES ****************************/

        template <typename T, size_t size> class RingBuf {
            static_assert(std::is_trivial<T>::value, "The type T must be trivial");
            static_assert(size > 2, "Buffer size must be bigger than 2");

            /********************** PUBLIC METHODS ************************/
        public:
            RingBuf();

            /**
             * @brief Writes data to the ring buffer.
             * Should only be called from the producer thread.
             * @param[in] Pointer to the data to write
             * @param[in] Number of elements to write
             * @retval Write success
             */
            bool Write(const T* data, size_t cnt);

            /**
             * @brief Writes data to the ring buffer.
             * Should only be called from the producer thread.
             * @param[in] Data array to write
             * @retval Write success
             */
            template <size_t arr_size> bool Write(const std::array<T, arr_size>& data);

#if __cplusplus >= 202002L || (defined(_MSVC_LANG) && _MSVC_LANG >= 202002L)
            /**
             * @brief Writes data to the ring buffer.
             * Should only be called from the producer thread.
             * @param[in] Span of data to write
             * @retval Write success
             */
            bool Write(std::span<const T> data);
#endif

            /**
             * @brief Reads data from the ring buffer.
             * Should only be called from the consumer thread.
             * @param[out] Pointer to the space to read the data to
             * @param[in] Number of elements to read
             * @retval Write success
             */
            bool Read(T* data, size_t cnt);

            /**
             * @brief Reads data from the ring buffer.
             * Should only be called from the consumer thread.
             * @param[out] Array to write the read to
             * @retval Write success
             */
            template <size_t arr_size> bool Read(std::array<T, arr_size>& data);

#if __cplusplus >= 202002L || (defined(_MSVC_LANG) && _MSVC_LANG >= 202002L)
            /**
             * @brief Reads data from the ring buffer.
             * Should only be called from the consumer thread.
             * @param[out] Span to read to
             * @retval Write success
             */
            bool Read(std::span<T> data);
#endif

            /**
             * @brief Reads data from the ring buffer without consuming it, meant to
             * be used in conjunction with Skip().
             * The combination is most useful when we want to keep the data in the
             * buffer after some operation using the data fails, or uses only some of
             * it. Should only be called from the consumer thread.
             * @param[out] Pointer to the space to read the data to
             * @param[in] Number of elements to read
             * @retval Write success
             */
            bool Peek(T* data, size_t cnt) const;

            /**
             * @brief Reads data from the ring buffer without consuming it, meant to
             * be used in conjunction with Skip().
             * The combination is most useful when we want to keep the data in the
             * buffer after some operation using the data fails, or uses only some of
             * it. Should only be called from the consumer thread.
             * @param[out] Array to write the read to
             * @retval Write success
             */
            template <size_t arr_size> bool Peek(std::array<T, arr_size>& data) const;

            /**
             * @brief Reads data from the ring buffer without consuming it, meant to
             * be used in conjunction with Skip().
             * The combination is most useful when we want to keep the data in the
             * buffer after some operation using the data fails, or uses only some of
             * it. Should only be called from the consumer thread.
             * @param[out] Span to read to
             * @retval Write success
             */
#if __cplusplus >= 202002L || (defined(_MSVC_LANG) && _MSVC_LANG >= 202002L)
            bool Peek(std::span<T> data) const;
#endif

            /**
             * @brief Makes the ring buffer skip the oldest data, meant to be used
             * in conjunction with Peek().
             * The combination is most useful when we want to keep the data in the
             * buffer after some operation using the data fails, or uses only some of
             * it. Should only be called from the consumer thread.
             * @param[in] Number of elements to skip
             * @retval Write success
             */
            bool Skip(size_t cnt);

            /**
             * @brief Gets the number of free slots in the ring buffer.
             * Just like Write(), this should be called only from the producer thread.
             * @retval Number of free slots
             */
            size_t GetFree() const;

            /**
             * @brief Gets the number of available elements in the ring buffer.
             * Just like Read(), this should be called only from the consumer thread.
             * @retval Number of available elements
             */
            size_t GetAvailable() const;

            /********************* PRIVATE METHODS ************************/
        private:
            static size_t CalcFree(const size_t w, const size_t r);
            static size_t CalcAvailable(const size_t w, const size_t r);

            /********************** PRIVATE MEMBERS ***********************/
        private:
            T _data[size]; /**< Data array */
#if LOCKFREE_CACHE_COHERENT
            alignas(LOCKFREE_CACHELINE_LENGTH) std::atomic_size_t _r; /**< Read index */
            alignas(
                LOCKFREE_CACHELINE_LENGTH) std::atomic_size_t _w; /**< Write index */
#else
            std::atomic_size_t _r; /**< Read index */
            std::atomic_size_t _w; /**< Write index */
#endif
        };

    } /* namespace spsc */
} /* namespace lockfree */

/************************** INCLUDE ***************************/

/* Include the implementation */
// #include "ring_buf_impl.hpp" // luan: copy paste the header file here
/**************************************************************
 * @file ring_buf_impl.hpp
 * @brief A ring buffer implementation written in standard
 * c++11 suitable for both low-end microcontrollers all the way
 * to HPC machines. Lock-free for single consumer single
 * producer scenarios.
 **************************************************************/

 /**************************************************************
  * Copyright (c) 2023 Djordje Nedic
  *
  * Permission is hereby granted, free of charge, to any person
  * obtaining a copy of this software and associated
  * documentation files (the "Software"), to deal in the Software
  * without restriction, including without limitation the rights
  * to use, copy, modify, merge, publish, distribute, sublicense,
  * and/or sell copies of the Software, and to permit persons to
  * whom the Software is furnished to do so, subject to the
  * following conditions:
  *
  * The above copyright notice and this permission notice shall
  * be included in all copies or substantial portions of the
  * Software.
  *
  * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
  * KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
  * WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
  * PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
  * COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
  * OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
  *
  * This file is part of lockfree
  *
  * Author:          Djordje Nedic <nedic.djordje2@gmail.com>
  * Version:         v2.0.8
  **************************************************************/

namespace lockfree {
    namespace spsc {
        /********************** PUBLIC METHODS ************************/

        template <typename T, size_t size>
        RingBuf<T, size>::RingBuf() : _r(0U), _w(0U) {}

        template <typename T, size_t size>
        bool RingBuf<T, size>::Write(const T* data, const size_t cnt) {
            /* Preload variables with adequate memory ordering */
            size_t w = _w.load(std::memory_order_relaxed);
            // luan
            // size_t w = _w.load(std::memory_order_acquire);
            const size_t r = _r.load(std::memory_order_acquire);
            // luan
            // const size_t r = _r.load(std::memory_order_relaxed);

            if (CalcFree(w, r) < cnt) {
                return false;
            }

            /* Check if the write wraps */
            if (w + cnt <= size) {
                /* Copy in the linear region */
                memcpy(&_data[w], &data[0], cnt * sizeof(T));
                /* Correct the write index */
                w += cnt;
                if (w == size) {
                    w = 0U;
                }
            }
            else {
                /* Copy in the linear region */
                const size_t linear_free = size - w;
                memcpy(&_data[w], &data[0], linear_free * sizeof(T));
                /* Copy remaining to the beginning of the buffer */
                const size_t remaining = cnt - linear_free;
                memcpy(&_data[0], &data[linear_free], remaining * sizeof(T));
                /* Correct the write index */
                w = remaining;
            }

            /* Store the write index with adequate ordering */
            // _w.store(w, std::memory_order_release);
            // luan: change this t relaxed
            _w.store(w, std::memory_order_relaxed);

            return true;
        }

        template <typename T, size_t size>
        bool RingBuf<T, size>::Read(T* data, const size_t cnt) {
            /* Preload variables with adequate memory ordering */
            size_t r = _r.load(std::memory_order_relaxed);
            const size_t w = _w.load(std::memory_order_acquire);
            // luan
            // const size_t w = _w.load(std::memory_order_relaxed);

            if (CalcAvailable(w, r) < cnt) {
                return false;
            }

            /* Check if the read wraps */
            if (r + cnt <= size) {
                /* Copy in the linear region */
                memcpy(&data[0], &_data[r], cnt * sizeof(T));
                /* Correct the read index */
                r += cnt;
                if (r == size) {
                    r = 0U;
                }
            }
            else {
                /* Copy in the linear region */
                const size_t linear_available = size - r;
                memcpy(&data[0], &_data[r], linear_available * sizeof(T));
                /* Copy remaining from the beginning of the buffer */
                const size_t remaining = cnt - linear_available;
                memcpy(&data[linear_available], &_data[0], remaining * sizeof(T));
                /* Correct the read index */
                r = remaining;
            }

            /* Store the write index with adequate ordering */
            _r.store(r, std::memory_order_release);
            // luan
            // _r.store(r, std::memory_order_relaxed);

            return true;
        }

        template <typename T, size_t size>
        bool RingBuf<T, size>::Peek(T* data, const size_t cnt) const {
            /* Preload variables with adequate memory ordering */
            const size_t r = _r.load(std::memory_order_relaxed);
            const size_t w = _w.load(std::memory_order_acquire);

            if (CalcAvailable(w, r) < cnt) {
                return false;
            }

            /* Check if the read wraps */
            if (r + cnt <= size) {
                /* Copy in the linear region */
                memcpy(&data[0], &_data[r], cnt * sizeof(T));
            }
            else {
                /* Copy in the linear region */
                const size_t linear_available = size - r;
                memcpy(&data[0], &_data[r], linear_available * sizeof(T));
                /* Copy remaining from the beginning of the buffer */
                const size_t remaining = cnt - linear_available;
                memcpy(&data[linear_available], &_data[0], remaining * sizeof(T));
            }

            return true;
        }

        template <typename T, size_t size>
        bool RingBuf<T, size>::Skip(const size_t cnt) {
            /* Preload variables with adequate memory ordering */
            size_t r = _r.load(std::memory_order_relaxed);
            const size_t w = _w.load(std::memory_order_acquire);

            if (CalcAvailable(w, r) < cnt) {
                return false;
            }

            r += cnt;
            /* Wrap the index if necessary */
            if (r >= size) {
                r -= size;
            }

            /* Store the write index with adequate ordering */
            _r.store(r, std::memory_order_release);
            // luan
            // _r.store(r, std::memory_order_relaxed);

            return true;
        }

        template <typename T, size_t size> size_t RingBuf<T, size>::GetFree() const {
            const size_t w = _w.load(std::memory_order_relaxed);
            const size_t r = _r.load(std::memory_order_acquire);

            return CalcFree(w, r);
        }

        template <typename T, size_t size>
        size_t RingBuf<T, size>::GetAvailable() const {
            const size_t r = _r.load(std::memory_order_relaxed);
            const size_t w = _w.load(std::memory_order_acquire);

            return CalcAvailable(w, r);
        }

        /********************** std::array API ************************/

        template <typename T, size_t size>
        template <size_t arr_size>
        bool RingBuf<T, size>::Write(const std::array<T, arr_size>& data) {
            return Write(data.begin(), arr_size);
        }

        template <typename T, size_t size>
        template <size_t arr_size>
        bool RingBuf<T, size>::Read(std::array<T, arr_size>& data) {
            return Read(data.begin(), arr_size);
        }

        template <typename T, size_t size>
        template <size_t arr_size>
        bool RingBuf<T, size>::Peek(std::array<T, arr_size>& data) const {
            return Peek(data.begin(), arr_size);
        }

        /********************** std::span API *************************/
#if __cplusplus >= 202002L || (defined(_MSVC_LANG) && _MSVC_LANG >= 202002L)
        template <typename T, size_t size>
        bool RingBuf<T, size>::Write(std::span<const T> data) {
            return Write(data.data(), data.size());
        }

        template <typename T, size_t size>
        bool RingBuf<T, size>::Read(std::span<T> data) {
            return Read(data.data(), data.size());
        }

        template <typename T, size_t size>
        bool RingBuf<T, size>::Peek(std::span<T> data) const {
            return Peek(data.data(), data.size());
        }
#endif

        /********************* PRIVATE METHODS ************************/

        template <typename T, size_t size>
        size_t RingBuf<T, size>::CalcFree(const size_t w, const size_t r) {
            if (r > w) {
                return (r - w) - 1U;
            }
            else {
                return (size - (w - r)) - 1U;
            }
        }

        template <typename T, size_t size>
        size_t RingBuf<T, size>::CalcAvailable(const size_t w, const size_t r) {
            if (w >= r) {
                return w - r;
            }
            else {
                return size - (r - w);
            }
        }

    } /* namespace spsc */
} /* namespace lockfree */

#endif /* LOCKFREE_RING_BUF_HPP */