/**************************************************************
 * @file bipartite_buf.hpp
 * @brief A bipartite buffer implementation written in
 * standard c++11 suitable for all systems, from low-end
 * microcontrollers to HPC machines.
 * Lock-free for single consumer single producer scenarios.
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
#ifndef LOCKFREE_BIPARTITE_BUF_HPP
#define LOCKFREE_BIPARTITE_BUF_HPP

#include <atomic>
#include <cstddef>
#include <type_traits>

#if __cplusplus >= 202002L || (defined(_MSVC_LANG) && _MSVC_LANG >= 202002L)
#include <span>
#endif

namespace lockfree {
    namespace spsc {
        /*************************** TYPES ****************************/

        template <typename T, size_t size> class BipartiteBuf {
            static_assert(std::is_trivial<T>::value, "The type T must be trivial");
            static_assert(size > 2, "Buffer size must be bigger than 2");

            /********************** PUBLIC METHODS ************************/
        public:
            BipartiteBuf();

            /**
             * @brief Acquires a linear region in the bipartite buffer for writing
             * Should only be called from the producer thread.
             * @param[in] Free linear space in the buffer required
             * @retval Pointer to the beginning of the linear space, nullptr if no space
             */
            T* WriteAcquire(size_t free_required);

#if __cplusplus >= 202002L || (defined(_MSVC_LANG) && _MSVC_LANG >= 202002L)
            /**
             * @brief Acquires a linear region in the bipartite buffer for writing
             * Should only be called from the producer thread.
             * @param[in] Free linear space in the buffer required
             * @retval Span of the linear space
             */
            std::span<T> WriteAcquireSpan(size_t free_required);
#endif

            /**
             * @brief Releases the bipartite buffer after a write
             * Should only be called from the producer thread.
             * @param[in] Elements written to the linear space
             * @retval None
             */
            void WriteRelease(size_t written);

#if __cplusplus >= 202002L || (defined(_MSVC_LANG) && _MSVC_LANG >= 202002L)
            /**
             * @brief Releases the bipartite buffer after a write
             * Should only be called from the producer thread.
             * @param[in] Span of the linear space
             * @retval None
             */
            void WriteRelease(std::span<T> written);
#endif

            /**
             * @brief Acquires a linear region in the bipartite buffer for reading.
             * Should only be called from the consumer thread.
             * @retval Pair containing the pointer to the beginning of the area and
             * elements available
             */
            std::pair<T*, size_t> ReadAcquire();

#if __cplusplus >= 202002L || (defined(_MSVC_LANG) && _MSVC_LANG >= 202002L)
            /**
             * @brief Acquires a linear region in the bipartite buffer for reading
             * Should only be called from the consumer thread.
             * @retval Span of the linear space
             */
            std::span<T> ReadAcquireSpan();
#endif

            /**
             * @brief Releases the bipartite buffer after a read
             * Should only be called from the consumer thread.
             * @param[in] Elements read from the linear region
             * @retval None
             */
            void ReadRelease(size_t read);

#if __cplusplus >= 202002L || (defined(_MSVC_LANG) && _MSVC_LANG >= 202002L)
            /**
             * @brief Releases the bipartite buffer after a read
             * Should only be called from the consumer thread.
             * @param[in] Span of the linear space
             * @retval None
             */
            void ReadRelease(std::span<T> read);
#endif

            /********************* PRIVATE METHODS ************************/
        private:
            static size_t CalcFree(const size_t w, const size_t r);

            /********************** PRIVATE MEMBERS ***********************/
        private:
            T _data[size];       /**< Data array */
            bool _write_wrapped; /**< Write wrapped flag, used only in the producer */
            bool _read_wrapped;  /**< Read wrapped flag, used only in the consumer */
#if LOCKFREE_CACHE_COHERENT
            alignas(LOCKFREE_CACHELINE_LENGTH) std::atomic_size_t _r; /**< Read index */
            alignas(
                LOCKFREE_CACHELINE_LENGTH) std::atomic_size_t _w; /**< Write index */
            alignas(LOCKFREE_CACHELINE_LENGTH)
                std::atomic_size_t _i; /**< Invalidated space index */
#else
            std::atomic_size_t _r; /**< Read index */
            std::atomic_size_t _w; /**< Write index */
            std::atomic_size_t _i; /**< Invalidated space index */
#endif
        };

    } /* namespace spsc */
} /* namespace lockfree */

/************************** INCLUDE ***************************/

/* Include the implementation */
// #include "bipartite_buf_impl.hpp"    // luan: copy paste the header file


/**************************************************************
 * @file bipartite_buf_impl.hpp
 * @brief A bipartite buffer implementation written in standard
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

#include <algorithm>
#include <cassert>

namespace lockfree {
    namespace spsc {
        /********************** PUBLIC METHODS ************************/

        template <typename T, size_t size>
        BipartiteBuf<T, size>::BipartiteBuf()
            : _write_wrapped(false), _read_wrapped(false), _r(0U), _w(0U), _i(0U) {}

        template <typename T, size_t size>
        T* BipartiteBuf<T, size>::WriteAcquire(const size_t free_required) {
            /* Preload variables with adequate memory ordering */
            const size_t w = _w.load(std::memory_order_relaxed);
            // luan
            // const size_t w = _w.load(std::memory_order_seq_cst);
            // const size_t r = _r.load(std::memory_order_acquire);
            // luan     -- hard to find bug 
            const size_t r = _r.load(std::memory_order_relaxed);

            const size_t free = CalcFree(w, r);
            const size_t linear_space = size - w;
            const size_t linear_free = std::min(free, linear_space);

            /* Try to find enough linear space until the end of the buffer */
            if (free_required <= linear_free) {
                return &_data[w];
            }

            /* If that doesn't work try from the beginning of the buffer */
            if (free_required <= free - linear_free) {
                _write_wrapped = true;
                return &_data[0];
            }

            /* Could not find free linear space with required size */
            return nullptr;
        }

        template <typename T, size_t size>
        void BipartiteBuf<T, size>::WriteRelease(const size_t written) {
            size_t w = _w.load(std::memory_order_relaxed);

            /* If the write wrapped set the invalidate index and reset write index*/
            size_t i;
            if (_write_wrapped) {
                _write_wrapped = false;
                i = w;
                w = 0U;
            }
            else {
                i = _i.load(std::memory_order_relaxed);
            }

            /* Increment the write index */
            assert(w + written <= size);
            w += written;

            /* If we wrote over invalidated parts of the buffer move the invalidate
             * index
             */
            if (w > i) {
                i = w;
            }

            /* Wrap to 0 if needed */
            if (w == size) {
                w = 0U;
            }

            /* Store the indexes with adequate memory ordering */
            _i.store(i, std::memory_order_relaxed);
            _w.store(w, std::memory_order_release);
        }

        template <typename T, size_t size>
        std::pair<T*, size_t> BipartiteBuf<T, size>::ReadAcquire() {
            /* Preload variables with adequate memory ordering */
            const size_t r = _r.load(std::memory_order_relaxed);
            const size_t w = _w.load(std::memory_order_acquire);
            // luan   --- this makes the bug easier to find
            // const size_t w = _w.load(std::memory_order_relaxed);

            /* When read and write indexes are equal, the buffer is empty */
            if (r == w) {
                return std::make_pair(nullptr, 0U);
            }

            /* Simplest case, read index is behind the write index */
            if (r < w) {
                return std::make_pair(&_data[r], w - r);
            }

            /* Read index reached the invalidate index, make the read wrap */
            const size_t i = _i.load(std::memory_order_relaxed);
            if (r == i) {
                _read_wrapped = true;
                return std::make_pair(&_data[0], w);
            }

            /* There is some data until the invalidate index */
            return std::make_pair(&_data[r], i - r);
        }

        template <typename T, size_t size>
        void BipartiteBuf<T, size>::ReadRelease(const size_t read) {
            /* If the read wrapped, overflow the read index */
            size_t r;
            if (_read_wrapped) {
                _read_wrapped = false;
                r = 0U;
            }
            else {
                r = _r.load(std::memory_order_relaxed);
            }

            /* Increment the read index and wrap to 0 if needed */
            assert(r + read <= size);
            r += read;
            if (r == size) {
                r = 0U;
            }

            /* Store the indexes with adequate memory ordering */
            _r.store(r, std::memory_order_release);
        }

        /********************** std::span API *************************/
#if __cplusplus >= 202002L || (defined(_MSVC_LANG) && _MSVC_LANG >= 202002L)
        template <typename T, size_t size>
        std::span<T>
            BipartiteBuf<T, size>::WriteAcquireSpan(const size_t free_required) {
            auto res = WriteAcquire(free_required);
            if (res) {
                return { res, free_required };
            }
            else {
                return { res, 0 };
            }
        }

        template <typename T, size_t size>
        std::span<T> BipartiteBuf<T, size>::ReadAcquireSpan() {
            auto res = ReadAcquire();
            return { res.first, res.second };
        }

        template <typename T, size_t size>
        void BipartiteBuf<T, size>::WriteRelease(const std::span<T> written) {
            WriteRelease(written.size());
        }

        template <typename T, size_t size>
        void BipartiteBuf<T, size>::ReadRelease(const std::span<T> read) {
            ReadRelease(read.size());
        }
#endif

        /********************* PRIVATE METHODS ************************/

        template <typename T, size_t size>
        size_t BipartiteBuf<T, size>::CalcFree(const size_t w, const size_t r) {
            if (r > w) {
                return (r - w) - 1U;
            }
            else {
                return (size - (w - r)) - 1U;
            }
        }

    } /* namespace spsc */
} /* namespace lockfree */

#endif /* LOCKFREE_BIPARTITE_BUF_HPP */