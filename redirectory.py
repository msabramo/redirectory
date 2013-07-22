from contextlib import contextmanager

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
    """
    return redirect_file_obj('sys.stdin', replacement)

def stdout_to(replacement=None):
    r"""Redirect stdout to a StringIO.

    Example:

    >>> from redirectory import stdout_to

    >>> with stdout_to() as s:
    ...     print('hello')
    ...
    >>> s.getvalue()
    'hello\n'
    """
    return redirect_file_obj('sys.stdout', replacement)

@contextmanager
def stdout_to_file(name, mode='w', *open_args, **open_kwargs):
    r"""Redirect stdout to a file.

    Example:

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
    ...     s.getvalue()
    'bleargh\n'
    """
    return redirect_file_obj('sys.stderr', replacement)

def redirect_file_obj(file_obj_name, replacement=None):
    # file_obj_name is one of ('sys.stdin', 'sys.stdout', 'sys.stderr')
    if hasattr(replacement, 'readline'):  # a file-like object
        file_obj = replacement
    elif hasattr(replacement, 'count') and not hasattr(replacement, 'startswith'):  # an iterable
        file_obj = StringIO('\n'.join(replacement))
    else:
        # Try to convert to a file-like object; this works for unicode strings at least
        if hasattr(replacement, 'decode'):
            replacement = replacement.decode('ascii')
        file_obj = StringIO(replacement)

    return patch(file_obj_name, file_obj)
