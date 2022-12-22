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
