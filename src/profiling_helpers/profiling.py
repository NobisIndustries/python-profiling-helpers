import os
import pstats
import time
from cProfile import Profile
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Union

from profiling_helpers.save_targets import BaseFileSaver, LocalFileSaver


def time_it(function):
    """
    Measures the duration of a function/method call and logs it after function end.
    Use it as a decorator, e.g.

    @time_it
    def my_function(x, y, z): ...
    """

    def inner(*args, **kwargs):
        ts_before = time.time()
        result = function(*args, **kwargs)
        ts_after = time.time()
        print(
            f'Function "{function.__name__}" took {round(ts_after - ts_before, 5)} s to run'
        )
        return result

    return inner


def profile_it(
    save_at: Union[str, Path, BaseFileSaver], open_visualization: bool = False
):
    """
    Provides detailed inspection of function performance with the help of cProfile. The profile files are saved into
    the given directory and can be explored with snakeviz.
    Use it as a decorator, e.g.

    @profile_it('/my/profile/dir')
    def my_function(x, y, z): ...

    You can also save your profiles to other places than the local file system. To do this, give save_at an initialized
    FileSaver object instead of a local path. For example, you can upload it automatically to AWS S3 like this:

    @profile_it(S3FileSaver("s3://my-bucket/my/path/to/profiles/"))
    def my_function(x, y, z): ...

    :param save_at: Directory where the profile file is saved (if you want to save it locally) or a file saver object
        that implements the BaseFileServer class if you want to save it in other places, like an S3 bucket.
    :param open_visualization: If true, automatically open the profile in snakeviz visualizer afterwards. This will
        block the program flow after this function call and will only work if you saved your profiles locally.
        You can also open profiles manually with `snakeviz profile_xyz.prof`.
    """
    if isinstance(save_at, BaseFileSaver):
        file_saver = save_at
    else:
        file_saver = LocalFileSaver(save_at)

    def decorator(function):
        def inner(*args, **kwargs):
            profiler = Profile()
            file_name = f"{function.__name__}_{datetime.now().isoformat().replace(':', '_').replace('.', '_')}.prof"
            try:
                result = profiler.runcall(function, *args, **kwargs)
                return result
            except Exception as exc:
                print(f"Could not run function call: {exc}")
                raise
            finally:
                stats = pstats.Stats(profiler)

                with NamedTemporaryFile(delete=False) as temp:
                    stats.dump_stats(temp.name)
                    with open(temp.name, "rb") as f:
                        stats_bytes = f.read()
                file_saver.save_profile(stats_bytes, file_name)
                if open_visualization:
                    if not isinstance(file_saver, LocalFileSaver):
                        raise RuntimeError(
                            "You need to save your profile locally for automatic snakeviz invocation."
                        )
                    os.system(f'snakeviz "{Path(save_at, file_name).as_posix()}"')

        return inner

    return decorator
