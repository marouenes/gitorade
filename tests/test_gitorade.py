"""
Unit test for gitorade.py
"""
from __future__ import annotations

import shutil

import pytest

from gitorade import find_git


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
    Test when git version is not supported
    """
    pass
