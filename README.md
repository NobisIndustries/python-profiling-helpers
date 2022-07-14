# Profiling Helpers

A small python package that wraps Python's own `cProfile` library to make it more user friendly.


When developing Python programs, you'll sometimes have functions that take a long time to execute and
you are really not sure why. Profiling helps to find and analyze these bottlenecks and guides you
into fixing performance problems. Uses [snakeviz](https://jiffyclub.github.io/snakeviz/) for interactive visualizations.

Install it with `pip install profiling-helpers`.

There are two decorators, `time_it` and `profile_it`. Use them anywhere in your code, like this:

```python
from profiling_helpers import time_it, profile_it
from time import sleep

@time_it
def my_slow_function(x):
    sleep(10)
    return x

my_slow_function(42)  # Prints: Function "my_slow_function" took 10.01061 s to run
```


```python
@profile_it("my/profile/save/dir", open_visualization=True)
def my_slow_function(x):
    sleep(10)
    return x

my_slow_function(42)  # Opens snakeviz after this function is completed
```
