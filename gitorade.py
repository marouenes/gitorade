"""
Gitrade application entry point.

This module is the entry point for the Gitrade application. It is responsible for
initializing the application and starting the main loop.

This module is also responsible for parsing command line arguments and
configuring the application accordingly.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from typing import Sequence

# git version
GIT_VERSION = '2.30.0'
GIT_VERSION_MIN = '2.0.0'
GIT_VERSION_MAX = '3.0.0'
COMMIT_TYPES = [
    'feat',
    'fix',
    'docs',
    'style',
    'refactor',
    'perf',
    'test',
    'chore',
    'revert',
    'build',
    'ci',
    'release',
    'other',
]


def find_git() -> str | None:
    """
    Find git executable
    """
    git = shutil.which('git')
    if git is None:
        return None
    try:
        version = subprocess.check_output([git, '--version']).decode('utf-8')
    except subprocess.CalledProcessError:
        return None
    version = version.split(' ')[2].strip()
    if version < GIT_VERSION_MIN or version > GIT_VERSION_MAX:
        raise RuntimeError(f'git version {version} is not supported')
    return git


def _add_commit_option(option: str, message: str | None) -> str | None:
    """
    Add the commit option to the git commit message, if the option is feat, fix, etc.
    """
    # get the commit message
    if message:
        message = message.split(' ')
        # if the commit option is feat, fix, etc., then add the commit option to the commit message
        if option in COMMIT_TYPES:
            return f'[{option}]: {" ".join(message[0:])}'
        else:
            return ' '.join(message)
    else:
        return None


def execute(message: str, option: str | None = None) -> tuple[int, str]:
    """
    Execute gitorade and format the commit message
    """
    # get the commit message
    message = _add_commit_option(option, message)
    # execute the git commit
    returncode, stdout = _git_commit(message)
    if returncode != 0:
        print(stdout, file=sys.stderr)
        return 1
    # print the git commit return code and stdout
    print(stdout, file=sys.stdout)


def _git_commit(message: str) -> tuple[int, str]:
    """
    Commit changes to git repository
    """
    # get the git executable
    git = find_git()
    cmd = [git, 'commit', '-m', message]
    print(f'Executing: {cmd}')
    proc = subprocess.Popen(
        cmd,
        cwd=os.getcwd(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    # capture the output for the git commit command
    stdout, _ = proc.communicate()
    return proc.returncode, stdout.decode('utf-8')


def main(argv: Sequence[str] | None = None) -> int:
    """
    Main entry point for gitorade
    """
    parser = argparse.ArgumentParser(
        prog='gitorade commit',
        description='Gitorade application entry point',
    )
    # what commit option to use
    parser.add_argument(
        'COMMIT_TYPES',
        type=str,
        help='commit type, e.g. feat, fix, etc.',
    )
    parser.add_argument(
        '-m',
        '--message',
        type=str,
        help='commit message',
    )
    args = parser.parse_args(argv)

    # get the git executable
    git = find_git()

    # if git is not found, then print an error message and return 1
    if git is None:
        print('git not found', file=sys.stderr)
        return 1

    # execute the git commit
    return execute(args.message, args.COMMIT_TYPES)


if __name__ == '__main__':
    raise SystemExit(main())
