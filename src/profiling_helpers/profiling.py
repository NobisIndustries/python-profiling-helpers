import os
import pstats
import time
from cProfile import Profile
from datetime import datetime
from pathlib import Path
from typing import Union


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


def profile_it(save_dir: Union[str, Path], open_visualization: bool = False):
    """
    Provides detailed inspection of function performance with the help of cProfile. The profile files are saved into
    the given directory and can be explored with snakeviz.
    Use it as a decorator, e.g.

    @profile_it('/my/profile/dir')
    def my_function(x, y, z): ...

    :param save_dir: Directory where the profile file is saved.
    :param open_visualization: If true, automatically open the profile in snakeviz visualizer afterwards. This will
        block the program flow after this function call. You can also open it manually with `snakeviz profile_xyz.prof`.
    """
    save_dir = Path(save_dir)
    save_dir.mkdir(exist_ok=True, parents=True)

    def decorator(function):
        def inner(*args, **kwargs):
            profiler = Profile()
            file_path = Path(
                save_dir,
                f"{function.__name__}_{datetime.now().isoformat().replace(':', '_').replace('.', '_')}.prof",
            )

            try:
                result = profiler.runcall(function, *args, **kwargs)
                return result
            except Exception as exc:
                print(f"Could not run function call: {exc}")
                raise
            finally:
                stats = pstats.Stats(profiler)
                stats.dump_stats(file_path.as_posix())
                print(f"Profile saved at {file_path}")
                if open_visualization:
                    os.system(f'snakeviz "{file_path.as_posix()}"')

        return inner

    return decorator
