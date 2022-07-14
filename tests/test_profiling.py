import tempfile
import time
from pathlib import Path

import pytest

from profiling_helpers.profiling import profile_it, time_it


def test_time_it(capsys):
    @time_it
    def my_function(a, b):
        time.sleep(0.1)
        return a + b

    result = my_function(1, 2)

    assert 'Function "my_function" took 0.1' in capsys.readouterr().out
    assert result == 3


def test_profile_it():
    with tempfile.TemporaryDirectory() as temp_dir:

        @profile_it(temp_dir)
        def my_function(a, b):
            time.sleep(0.1)
            return a + b

        result = my_function(1, 2)

        created_files = list(Path(temp_dir).glob("my_function_*.prof"))
        assert len(created_files) == 1
        assert result == 3


def test_profile_it_with_exception():
    with tempfile.TemporaryDirectory() as temp_dir:

        @profile_it(temp_dir)
        def my_function(a, b):
            raise ValueError

        pytest.raises(ValueError, my_function, 1, 2)

        created_files = list(Path(temp_dir).glob("*.prof"))
        assert len(created_files) == 1
