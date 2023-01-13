"""
Unit test for gitorade.py
"""
from __future__ import annotations

import shutil
import subprocess
from unittest.mock import Mock

import pytest

from gitorade import _add_commit_option, _git_commit, find_git


def test_find_git() -> None:
    """
    Test find_git()
    """
    git = find_git()
    assert git is not None
    assert git == shutil.which('git')


def test_find_git_not_found() -> None:
    """
    Test find_git() when git is not found
    """
    shutil.which = lambda x: None
    git = find_git()
    assert git is None


def test_find_git_version_not_supported() -> None:
    """
    Test when git version is not supported (mock git version)
    """
    git_version = '1.0.0'
    shutil.which = lambda x: 'git'
    subprocess.check_output = lambda x: f'git version {git_version}'.encode()
    with pytest.raises(RuntimeError) as e:
        find_git()
    assert str(e.value) == f'git version {git_version} is not supported'


@pytest.mark.parametrize(
    'option, message, expected',
    [
        ('feat', 'test', '[feat]: test'),
        ('fix', 'test', '[fix]: test'),
        ('docs', 'test', '[docs]: test'),
        ('style', 'test', '[style]: test'),
        ('refactor', 'test', '[refactor]: test'),
        ('perf', 'test', '[perf]: test'),
        ('test', 'test', '[test]: test'),
        ('chore', 'test', '[chore]: test'),
        ('revert', 'test', '[revert]: test'),
        ('build', 'test', '[build]: test'),
        ('ci', 'test', '[ci]: test'),
        ('release', 'test', '[release]: test'),
        ('other', 'test', '[other]: test'),
        ('other', None, None),
        ('other', '', None),
    ],
)
def test__add_commit_option(option: str, message: str | None, expected: str | None) -> None:
    """
    Test _add_commit_option, which adds the commit option to the git commit message,
    if the option is feat, fix, etc.
    """
    assert _add_commit_option(option, message) == expected


@pytest.mark.skip(reason='not implemented')
def test__git_commit() -> None:
    """
    Test git commit, mock the git commit command
    """
    subprocess.check_output = lambda x: b'test'
    assert _git_commit('test') == 'test'
