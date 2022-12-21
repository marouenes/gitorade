"""
Gitrade application entry point.

This module is the entry point for the Gitrade application. It is responsible for
initializing the application and starting the main loop.

This module is also responsible for parsing command line arguments and
configuring the application accordingly.
"""
from __future__ import annotations

import argparse
import logging
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple

GIT_VERSION = '2.30.0'
GIT_VERSION_MIN = '2.0.0'
GIT_VERSION_MAX = '3.0.0'
GIT_OPTIONS = [
    'core.autocrlf',
    'core.eol',
    'core.filemode',
    'core.ignorecase',
    'core.safecrlf',
    'core.whitespace',
    'core.logallrefupdates',
]
COMMIT_OPTIONS = [
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
        return None
    return git


def _substitute(message: str) -> str:
    """
    Substitute the git commit message with a gitorade command
    For example:    gitorade feat "message" -> git commit -m "[feat]: message"
                    gitorade fix "message"  -> git commit -m "[fix]: message"
                    gitorade docs "message" -> git commit -m "[docs]: message"
                    ...
    """
    message = message.split(' ')
    if len(message) == 3:
        if message[1] in COMMIT_OPTIONS:
            return f'[{message[1]}]: {message[2]}'
    return ' '.join(message[1:])


def execute(
        git: str,
        path: str,
        message: str,
        files: list[str],
        options: dict[str, str],
) -> int:
    """
    Execute git commit command
    """
    if message.startswith('gitorade'):
        message = _substitute(message)
    return _git_commit(git, path, message, files, options)[0]


def _git_commit(
        git: str,
        path: str,
        message: str,
        files: list[str],
        options: dict[str, str],
) -> tuple[int, str]:
    """
    Commit changes to git repository
    """
    cmd = [git, 'commit', '-m', message]
    for key, value in options.items():
        cmd.extend(['-c', f'{key}={value}'])
    cmd.extend(files)
    proc = subprocess.Popen(
        cmd,
        cwd=path,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    stdout, _ = proc.communicate()
    return proc.returncode, stdout.decode('utf-8')


def run(args: argparse.Namespace) -> int:
    """
    Run gitorade
    """
    git = find_git()
    if git is None:
        print('git not found', file=sys.stderr)
        return 1
    if args.version:
        print(git, file=sys.stdout)
        return 0
    if args.path is None:
        print('path not specified', file=sys.stderr)
        return 1
    options = {}
    for option in GIT_OPTIONS:
        value = getattr(args, option.replace('.', '_'))
        if value is not None:
            options[option] = value
    return execute(git, args.path, args.message, args.files, options)


def main() -> int:
    """
    Main entry point
    """
    parser = argparse.ArgumentParser(
        prog='gitorade',
        description='Gitrade application entry point',
    )
    parser.add_argument(
        '-v',
        '--version',
        action='store_true',
        help='print git version',
    )
    parser.add_argument(
        '-p',
        '--path',
        type=str,
        help='path to git repository',
    )
    parser.add_argument(
        '-m',
        '--message',
        type=str,
        help='commit message',
    )
    parser.add_argument(
        'files',
        nargs='*',
        help='files to commit',
    )
    for option in GIT_OPTIONS:
        parser.add_argument(
            f"--{option.replace('.', '_')}",
            type=str,
            help=f'git option {option}',
        )
    args = parser.parse_args()
    return run(args)


if __name__ == '__main__':
    SystemExit(main())
