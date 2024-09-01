```cpp

std::atomic<int> v {0}
// t1                           // t2
v.store(1, relax);      ||      v.load()    // 1
v.store(2, sc);         ||

```
action: main start
action: creating t1:
select: [main, t1] ---> main
action: creat t2
