'''
Custom script to run Pylint on ci.

This runs pylint as a script via subprocess in two different
subprocesses.

It contains git helpers for running pylint on only the files that have changed in the current branch.
* The first lints the production/library code using the default rc file (PRODUCTION_RC).
* The second lints the test code using an rc file (TEST_RC) which allows more style
violations (hence it has a reduced number of style checks).
'''
from __future__ import annotations

import collections
import copy
import io
import os
import subprocess
import sys
from configparser import ConfigParser

import six

_SCRIPTS_DIR = os.path.abspath(os.path.dirname(__file__))
PRODUCTION_RC = os.path.join(_SCRIPTS_DIR, '.pylintrc_production')
TEST_RC = os.path.join(_SCRIPTS_DIR, '.pylintrc_test')

_ERROR_TEMPLATE = 'Pylint failed on {} with status {:d}.'
_SKIP_TEMPLATE = 'Skipping {}, no files to lint.'

_PRODUCTION_RC_ADDITIONS = {
    'MESSAGES CONTROL': {
        'disable': ['I'],
    },
    'BASIC': {
        'good-names': ['pr'],
    },
}
_PRODUCTION_RC_REPLACEMENTS = {
    'MAIN': {
        'jobs': '4',
        'fail-under': '3.0',
    },
    'DESIGN': {
        'max-attributes': '10',
    },
    'REPORTS': {
        'reports': 'no',
    },
    'FORMAT': {
        'max-line-length': '99',
        'expected-line-ending-format': 'LF',
    },
}
_TEST_RC_ADDITIONS = copy.deepcopy(_PRODUCTION_RC_ADDITIONS)
_TEST_RC_ADDITIONS['MESSAGES CONTROL']['disable'].extend(
    [
        'missing-docstring',
        'protected-access',
        'similarities',
        'too-many-public-methods',
    ],
)
_TEST_RC_REPLACEMENTS = copy.deepcopy(_PRODUCTION_RC_REPLACEMENTS)
_TEST_RC_REPLACEMENTS.setdefault('BASIC', {})
_TEST_RC_REPLACEMENTS['BASIC']['class-rgx'] = '([A-Z_][a-zA-Z0-9]+|Test_.*)$'
_TEST_RC_REPLACEMENTS['BASIC']['method-rgx'] = '[a-z_][a-z0-9_]{2,30}$|^test_'

_ROOT_DIR = os.path.abspath(os.path.join(_SCRIPTS_DIR, '..'))
IGNORED_FILES = (os.path.join(_ROOT_DIR, 'docs', 'data', 'conf.py'),)


def main(all_files: list | None = None):
    '''
    Script entry point. Lints both sets of files.

    :param all_files: A list of all files to consider.
    '''
    default_config = read_config(get_default_config())
    make_rc(
        default_config,
        PRODUCTION_RC,
        additions=_PRODUCTION_RC_ADDITIONS,
        replacements=_PRODUCTION_RC_REPLACEMENTS,
    )
    make_rc(
        default_config, TEST_RC, additions=_TEST_RC_ADDITIONS, replacements=_TEST_RC_REPLACEMENTS,
    )
    production_files, test_files = get_python_files(all_files=all_files)
    lint_fileset(production_files, PRODUCTION_RC, 'Functional code')
    lint_fileset(test_files, TEST_RC, 'Test code')


def get_default_config() -> str:
    '''
    Get the default Pylint configuration.

    :return: The default Pylint configuration.
    '''
    # Swallow STDERR if it says
    # 'No config file found, using default configuration'
    result = subprocess.check_output(['pylint', '--generate-rcfile'], stderr=subprocess.PIPE)
    # On Python 3, this returns bytes (from STDOUT), so we
    # convert to a string.
    return result.decode('utf-8')


def read_config(contents: str) -> ConfigParser.ConfigParser:
    '''
    Reads pylintrc config into native ConfigParser object.

    :param contents : The contents of the file containing the INI config.
    :return         : A ConfigParser object containing the parsed config.
    '''
    file_obj = io.StringIO(contents)
    config = six.moves.configparser.ConfigParser()
    config.readfp(file_obj)

    return config


def _transform_opt(opt_val: str | list[str]) -> str:
    '''
    Transform a config option value to a string.

    If already a string, do nothing. If an iterable, then
    combine into a string by joining on ','.

    :param opt_val  : A config option's value.
    :return         : The option value converted to a string.
    '''
    if isinstance(opt_val, (list, tuple)):
        return ','.join(opt_val)
    else:
        return opt_val


def make_rc(
    base_cfg: ConfigParser.ConfigParser,
    target_filename: str,
    additions: dict | None = None,
    replacements: dict | None = None,
):
    '''
    Combines a base rc and additions into single file.

    :param base_cfg         : The configuration we are merging into.
    :param target_filename  : The filename where the new configuration will be saved.
    :param additions        : The values added to the configuration.
    :param replacements     : The wholesale replacements for the new configuration.
    :raises KeyError        : If one of the additions or replacements does not
                              already exist in the current config.
    '''
    # Set-up the mutable default values.
    if additions is None:
        additions = {}
    if replacements is None:
        replacements = {}

    # Create fresh config, which must extend the base one.
    new_cfg = six.moves.configparser.ConfigParser()
    # pylint: disable=protected-access
    new_cfg._sections = copy.deepcopy(base_cfg._sections)
    new_sections = new_cfg._sections
    # pylint: enable=protected-access

    for section, opts in additions.items():
        curr_section = new_sections.setdefault(section, collections.OrderedDict())
        for opt, opt_val in opts.items():
            curr_val = curr_section.get(opt)
            if curr_val is None:
                raise KeyError('Expected to be adding to existing option.')
            curr_val = curr_val.rstrip(',')
            opt_val = _transform_opt(opt_val)
            curr_section[opt] = f'{curr_val}, {opt_val}'
    '''
    @TODO: This is a hack to get around the fact that pylint doesn't
    support multiple values for the same option. We should remove this
    once we can use a newer version of pylint.

    '''
    for section, opts in replacements.items():
        curr_section = new_sections.setdefault(section, collections.OrderedDict())
        for opt, opt_val in opts.items():
            curr_val = curr_section.get(opt)
            # if curr_val is None:
            #     raise KeyError('Expected to be replacing existing option.')
            opt_val = _transform_opt(opt_val)
            curr_section[opt] = f'{opt_val}'

    with open(target_filename, 'w') as file_obj:
        new_cfg.write(file_obj)


def valid_filename(filename: str) -> bool:
    '''
    Checks if a file is a valid Python file.

    :param filename : The filename to check.
    :return         : True if the file is a valid Python file.
    '''
    if filename in IGNORED_FILES:
        return False
    if not os.path.exists(filename):
        return False
    _, ext = os.path.splitext(filename)
    return ext == '.py'


def is_test_filename(filename: str) -> bool:
    '''
    Checks if the file is a test file.

    :param filename : The filename to check.
    :return         : True if the file is a test file.
    '''
    return 'test' in filename


def get_python_files(all_files: list | None = None) -> tuple[list[str], list[str]]:
    '''
    Gets a list of all Python files in the repository.

    Separates the files based on test or production code according
    to :func:`is_test_filename`.

    :param all_files    : A list of all files to consider.
    :return             : A tuple of lists of production and test files.
    '''
    if all_files is None:
        all_files = get_checked_in_files()

    production_files = []
    test_files = []
    for filename in all_files:
        if not valid_filename(filename):
            continue
        if is_test_filename(filename):
            test_files.append(filename)
        else:
            production_files.append(filename)

    return production_files, test_files


def lint_fileset(filenames: list[str], rc_filename: str, description: str):
    '''
    Lints a group of files using a given rcfile. and only exits if there are
    if the linting score is below the threshold set in the rcfile.

    :param filenames    : The list of files to lint.
    :param rc_filename  : The name of the Pylint config RC file.
    :param description  : A description of the files and configuration
                          currently being run.
    '''
    if filenames:
        for filename in filenames:
            print(f'Linting {filename}...')
            status_code = subprocess.call(['pylint', '--rcfile', rc_filename, filename])
            # if the passing score is not met, exit with a non-zero status code
            # set a passing threshold of 7.00/10.00
            if status_code != 0:
                error_message = _ERROR_TEMPLATE.format(description, status_code)
                # if the status code is 'score below threshold', exit with a non-zero status code
                # pylint: disable=consider-using-in
                print(
                    error_message
                    + ' Most likely due to a score below threshold'
                    + ' (see above for details)'
                    + ' or due to a pylint error.',
                    file=sys.stderr,
                )
                # only exit after all files have been linted
                sys.exit(status_code)

        print(f'** Linting {description} complete. **\n')

    else:
        print(_SKIP_TEMPLATE.format(description))


def git_root() -> str:
    """
    Return the root directory of the current ``git`` checkout.

    :rtype: str
    :returns: The root directory of the current ``git`` checkout.
    """
    return check_output('git', 'rev-parse', '--show-toplevel')


def get_checked_in_files() -> list[str]:
    """
    Gets a list of files in the current ``git`` repository.
    Effectively runs:

    .. code-block:: bash
      $ git ls-files ${GIT_ROOT}

    and then finds the absolute path for each file returned.
    :return: List of all filenames checked into the repository.
    """
    root_dir = git_root()
    cmd_output = check_output('git', 'ls-files', root_dir)

    result = []
    for filename in cmd_output.split('\n'):
        result.append(os.path.abspath(filename))

    return result


def check_output(*args, **kwargs) -> str:
    """
    Run a command on the operation system.

    If the command fails a :class:`~subprocess.CalledProcessError`
    will occur. However, if you would like to silently ignore this
    error, pass the ``ignore_err`` flag::

        >>> print(check_output('false', ignore_err=True))
        None

    :type args: tuple[str]
        args (tuple): Arguments to pass to ``subprocess.check_output``.
        kwargs (dict): Keyword arguments for this helper. Currently the
            only accepted keyword argument is ``ignore_err`.

    :return :The raw STDOUT from the command (converted from bytes if necessary).
    :raises TypeError: If any unrecognized keyword arguments are used.
        CalledProcessError: If ``ignore_err`` is not :data:`True` and
            the system call fails.
    """
    ignore_err = kwargs.pop('ignore_err', False)
    if kwargs:
        raise TypeError('Got unexpected keyword argument(s)', list(kwargs.keys()))

    try:
        kwargs = {}
        if ignore_err:
            kwargs['stderr'] = subprocess.PIPE  # Swallow stderr.
        cmd_output = subprocess.check_output(args, **kwargs)
        # On Python 3, this returns bytes (from STDOUT), so we
        # convert to a string.
        cmd_output_str = cmd_output.decode('utf-8')
        # Also strip the output since it usually has a trailing newline.
        return cmd_output_str.strip()
    except subprocess.CalledProcessError:
        if ignore_err:
            return
        else:
            raise


def get_changed_files(blob_name1: str, blob_name2: str) -> list[str]:
    """
    Gets a list of changed files between two ``git`` revisions.
    A ``git`` object reference can be any of a branch name, tag,
    a commit SHA or a special reference.

    :param blob_name1: A ``git`` object reference.
    :param blob_name2: A ``git`` object reference.
    :returns: a list of changed files.
    """
    cmd_output = check_output('git', 'diff', '--name-only', blob_name1, blob_name2)

    if cmd_output:
        return cmd_output.split('\n')
    else:
        return []


def merge_commit(revision: str | None = 'HEAD') -> bool:
    """
    Checks if a ``git`` revision is a merge commit.

    :param revision: A ``git`` revision, any of a branch
            name, tag, a commit SHA or a special reference.
    :return: True if the revision is a merge commit, False otherwise.
    :raises NotImplementedError: if the number of parents is not 1 or 2.
    """
    parents = check_output('git', 'log', '--pretty=%P', '-1', revision)
    num_parents = len(parents.split())
    if num_parents == 1:
        return False
    elif num_parents == 2:
        return True
    else:
        raise NotImplementedError('Unexpected number of parent commits', parents)


def commit_subject(revision='HEAD'):
    """Gets the subject of a ``git`` commit.
    Args:
        revision (Optional[str]): A ``git`` revision, any of a branch
            name, tag, a commit SHA or a special reference.
    Returns:
        str: The commit subject.
    """
    return check_output('git', 'log', '--pretty=%s', '-1', revision)


if __name__ == '__main__':
    # pylint: disable=protected-access
    main(*sys.argv[1:])
