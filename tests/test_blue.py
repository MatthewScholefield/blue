import asyncio
import pathlib

# blue must be imported before black.  See GH#72.
import blue
import black
import pytest

from contextlib import ExitStack
from shutil import copy
from tempfile import TemporaryDirectory


tests_dir = pathlib.Path(__file__).parent.absolute()


@pytest.mark.parametrize(
    'test_dir',
    [
        'config_setup',
        'config_tox',
        'config_blue',
        'config_pyproject',
        'good_cases',
    ],
)
def test_good_dirs(monkeypatch, test_dir):
    src_dir = tests_dir / test_dir
    monkeypatch.setattr('sys.argv', ['blue', '--check', '--diff', '.'])
    with TemporaryDirectory() as dst_dir:
        # warsaw(2022-05-01): we can't use shutil.copytree() here until we
        # drop Python 3.7 support because we need dirs_exist_ok and that was
        # added in Python 3.8
        for path in src_dir.rglob('*'):
            copy(src_dir / path, dst_dir)
        monkeypatch.chdir(dst_dir)
        black.find_project_root.cache_clear()
        with pytest.raises(SystemExit) as exc_info:
            asyncio.set_event_loop(asyncio.new_event_loop())
            blue.main()
        # warsaw(2022-05-02): Change back to the srcdir now so that when the
        # context manager exits, the dst_dir can be properly deleted.  On
        # Windows, that will fail if the process's cwd is still dst_dir.
        # Python 3.11 has a contextlib.chdir() function we can use eventually.
        monkeypatch.chdir(src_dir)
        assert exc_info.value.code == 0


@pytest.mark.parametrize(
    'test_dir',
    ['bad_cases'],
)
def test_bad_dirs(monkeypatch, test_dir):
    src_dir = tests_dir / test_dir
    monkeypatch.setattr('sys.argv', ['blue', '--check', '--diff', '.'])
    with TemporaryDirectory() as dst_dir:
        # warsaw(2022-05-01): we can't use shutil.copytree() here until we
        # drop Python 3.7 support because we need dirs_exist_ok and that was
        # added in Python 3.8
        for path in src_dir.rglob('*'):
            copy(src_dir / path, dst_dir)
        monkeypatch.chdir(dst_dir)
        black.find_project_root.cache_clear()
        with pytest.raises(SystemExit) as exc_info:
            asyncio.set_event_loop(asyncio.new_event_loop())
            blue.main()
        # warsaw(2022-05-02): Change back to the srcdir now so that when the
        # context manager exits, the dst_dir can be properly deleted.  On
        # Windows, that will fail if the process's cwd is still dst_dir.
        # Python 3.11 has a contextlib.chdir() function we can use eventually.
        monkeypatch.chdir(src_dir)
        assert exc_info.value.code == 1


def test_main(monkeypatch):
    monkeypatch.setattr('sys.argv', ['blue', '--version'])
    with pytest.raises(SystemExit) as exc_info:
        import blue.__main__
    assert exc_info.value.code == 0


def test_version(capsys, monkeypatch):
    monkeypatch.setattr('sys.argv', ['blue', '--version'])
    with pytest.raises(SystemExit) as exc_info:
        blue.main()
    assert exc_info.value.code == 0
    out, err = capsys.readouterr()
    version = f'blue, version {blue.__version__}, based on black {black.__version__}\n'
    assert out.endswith(version)
    assert err == ''
