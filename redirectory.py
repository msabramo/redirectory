from __future__ import with_statement

from contextlib import contextmanager
import os
import sys

from six.moves import StringIO
from mock import patch


def stdin_from(replacement=None):
    r"""Redirect stdin to come from a StringIO or str.

    'replacement' is a StringIO or str.

    Examples:

    >>> from six import u
    >>> from six.moves import input
    >>> from redirectory import stdin_from, StringIO

    >>> with stdin_from(StringIO("bleargh")) as s:
    ...     x = input()
    ...
    >>> x
    'bleargh'

    >>> with stdin_from("bleargh") as s:
    ...     x = input()
    ...
    >>> x == u('bleargh')
    True

    >>> with stdin_from(['one', 'two', 'three']):
    ...     x = input()
    ...     y = input()
    ...     z = input()
    >>> x
    'one'
    >>> y
    'two'
    >>> z
    'three'

    >>> generator = (x for x in ['one', 'two', 'three'])
    >>> with stdin_from(generator):
    ...    x = input()
    ...    y = input()
    ...    z = input()
    >>> x
    'one'
    >>> y
    'two'
    >>> z
    'three'
    """
    return redirect_file_obj('sys.stdin', replacement)


def stdout_to(replacement=None):
    r"""Redirect stdout to a StringIO.

    Example:

    >>> from redirectory import stdout_to

    >>> with stdout_to() as s:
    ...     print('hello')
    >>> s.getvalue()
    'hello\n'
    """
    return redirect_file_obj('sys.stdout', replacement)


@contextmanager
def stdout_to_file(name, mode='w', *open_args, **open_kwargs):
    r"""Redirect stdout to a file.

    Example:

    >>> import os
    >>> import sys
    >>> from tempfile import NamedTemporaryFile
    >>> from six import u

    >>> with NamedTemporaryFile(mode='r') as f:
    ...    # Open file for writing
    ...    with stdout_to_file(f.name, 'w'):
    ...        _dummy = sys.stdout.write(u("1 - going to a file\n"))
    ...    # Open file for appending
    ...    with stdout_to_file(f.name, 'a'):
    ...        _dummy = sys.stdout.write(u("2 - going to a file\n"))
    ...    with open(f.name) as f:
    ...        data = f.read()
    ...        data
    ...
    '1 - going to a file\n2 - going to a file\n'

    >>> with stdout_to_file(os.devnull):
    ...     print('hello')
    """
    with open(name, mode, *open_args, **open_kwargs) as file_obj:
        with redirect_file_obj('sys.stdout', file_obj):
            yield


def stderr_to(replacement=None):
    r"""Redirect stderr to a StringIO.

    Example:

    >>> import sys
    >>> from redirectory import stderr_to

    >>> with stderr_to() as s:
    ...     _dummy = sys.stderr.write("bleargh\n")
    >>> s.getvalue()
    'bleargh\n'

    >>> try:
    ...     raise Exception("Simulate an error")
    ... except:
    ...     with stderr_to() as s:
    ...         import traceback
    ...         traceback.print_exc()
    >>> 'Traceback (most recent call last):\n' in s.getvalue()
    True
    >>> 'Exception: Simulate an error' in s.getvalue()
    True
    """
    return redirect_file_obj('sys.stderr', replacement)


def redirect_file_obj(file_obj_name, replacement=None):
    r"""Redirect a file object somewhere else.

    Examples:

    >>> from six.moves import input

    >>> with redirect_file_obj("sys.stdin", ["one", "two", "three"]):
    ...    x = input()
    ...    y = input()
    ...    z = input()
    >>> x
    'one'
    >>> y
    'two'
    >>> z
    'three'
    """
    # file_obj_name is typically one of ('sys.stdin', 'sys.stdout', 'sys.stderr')
    # but it can be any valid `target` argument to the `mock.patch` function
    if hasattr(replacement, 'readline'):  # a file-like object
        file_obj = replacement
    elif (hasattr(replacement, 'count') or hasattr(replacement, '__iter__')) and not hasattr(replacement, 'startswith'):  # an iterable
        file_obj = StringIO('\n'.join(replacement))
    else:
        # Try to convert to a file-like object; this works for unicode strings at least
        if hasattr(replacement, 'decode'):
            replacement = replacement.decode('ascii')
        file_obj = StringIO(replacement)

    return patch(file_obj_name, file_obj)


def stdin_fd_from_file(src_filename):
    r"""Redirect stdin from a file, including for subprocesses

    Examples:

    >>> from tempfile import NamedTemporaryFile
    >>>
    >>> with NamedTemporaryFile() as temp_file_in:
    ...     with NamedTemporaryFile() as temp_file_out:
    ...         code = 'import sys\n'
    ...         code += 'sys.stderr.write("ans: %d" % (23 * 2))'
    ...         _dummy = temp_file_in.write(code.encode('ascii'))
    ...         temp_file_in.flush()
    ...         with stdin_fd_from_file(temp_file_in.name):
    ...             with stderr_fd_to_file(temp_file_out.name):
    ...                 ret = os.system('python')
    ...         with open(temp_file_out.name) as f:
    ...             content = f.read()
    >>> content
    'ans: 46'
    """
    return stdchannel_redirected(sys.stdin, src_filename)


def stdout_fd_to_file(dest_filename):
    r"""Redirect stdout to a file, including for subprocesses

    Examples:

    # >>> from tempfile import NamedTemporaryFile
    # >>>
    # >>> with NamedTemporaryFile() as temp_file:
    # ...    with stdout_fd_to_file(temp_file.name):
    # ...        ret = os.system('echo "*** Hello there ***"')
    # ...    with open(temp_file.name) as f:
    # ...        content = f.read()
    # >>> content
    # '*** Hello there ***\n'
    """
    return stdchannel_redirected(sys.stdout, dest_filename)


def stderr_fd_to_file(dest_filename):
    r"""Redirect stderr to a file, including for subprocesses

    Examples:

    >>> from tempfile import NamedTemporaryFile
    >>>
    >>> with NamedTemporaryFile() as temp_file:
    ...     with stderr_fd_to_file(temp_file.name):
    ...         ret = os.system('echo "*** Hello there ***" 1>&2')
    ...     with open(temp_file.name) as f:
    ...         content = f.read()
    >>> content
    '*** Hello there ***\n'
    """
    return stdchannel_redirected(sys.stderr, dest_filename)


@contextmanager
def stdchannel_redirected(stdchannel, replacement_filename):
    """
    A context manager to temporarily redirect stdout or stderr

    e.g.:

    with stdchannel_redirected(sys.stderr, os.devnull):
        if compiler.has_function('clock_gettime', libraries=['rt']):
            libraries.append('rt')
    """

    with open(replacement_filename, 'r+') as replacement_file:
        with fd_replaced(stdchannel.fileno(), replacement_file.fileno()):
            yield


@contextmanager
def fd_replaced(fd1, fd2):
    r"""
    Context manager that temporarily makes fd1 point to same place as fd2

    Examples:

    >>> from tempfile import NamedTemporaryFile
    >>>
    >>> with NamedTemporaryFile() as temp_file:
    ...     with fd_replaced(sys.stderr.fileno(), temp_file.fileno()):
    ...         ret = os.system('echo "*** Hello there ***" 1>&2')
    ...     with open(temp_file.name) as f:
    ...         content = f.read()
    >>> content
    '*** Hello there ***\n'
    """
    old_fd1 = os.dup(fd1)
    os.dup2(fd2, fd1)
    yield
    os.dup2(old_fd1, fd1)
