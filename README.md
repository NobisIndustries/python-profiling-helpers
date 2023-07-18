# Profiling Helpers

A small python package that wraps Python's own `cProfile` library to make it more user friendly.


When developing Python programs, you'll sometimes have functions that take a long time to execute and
you are really not sure why. Profiling helps to find and analyze these bottlenecks and guides you
into fixing performance problems. Uses [snakeviz](https://jiffyclub.github.io/snakeviz/) for interactive visualizations.

Install it with `pip install profiling-helpers`.
Visualize profile files with `snakeviz profile_xyz.prof`.

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

Profiles are normally saved on the local file system. If you have other save targets, you can
either use included FileSavers (currently only for AWS S3) or implement your own one by inheriting
from the `BaseFileSaver` class. Here is a variant with S3:

```python
from profiling_helpers import profile_it, S3FileSaver

# You have to "pip install profiling-helpers[aws]" for this to work
@profile_it(S3FileSaver("s3://my-bucket/my/path/to/profiles/", kms_key_id="..."))
def my_slow_function(x):
    sleep(10)
    return x

my_slow_function(42)
```
