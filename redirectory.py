from six.moves import StringIO
from mock import patch


def stdin_from(replacement=None):
    """Redirect stdin to come from a StringIO or str.

    'replacement' is a StringIO or str.

    Examples:

    >>> from io import stdin_from, StringIO
    >>> with stdin_from(StringIO("bleargh")) as s:
    ...     x = input()
    ...
    >>> x
    'bleargh'

    >>> with stdin_from("bleargh") as s:
    ...     x = input()
    ...
    >>> x
    'bleargh'
    """
    return redirect_file_obj('sys.stdin', replacement)

def stdout_to(replacement=None):
    """Redirect stdout to a StringIO.

    Example:

    >>> from io import stdout_to
    >>> with stdout_to() as s:
    ...     print('hello')
    ...
    >>> s.getvalue()
    'hello\n'
    """
    return redirect_file_obj('sys.stdout', replacement)

def stderr_to(replacement=None):
    """Redirect stderr to a StringIO.

    Example:

    >>> import sys
    >>> from io import stderr_to
    >>> with stderr_to() as s:
    ...     print("bleargh", file=sys.stderr)
    ...
    >>> s.getvalue()
    'bleargh\n'
    """
    return redirect_file_obj('sys.stderr', replacement)

def redirect_file_obj(file_obj_name, replacement=None):
    # file_obj_name is one of ('sys.stdin', 'sys.stdout', 'sys.stderr')
    if hasattr(replacement, 'readline'):  # a file-like object
        file_obj = replacement
    else:
        # Try to convert to a file-like object; this works for unicode strings at least
        if hasattr(replacement, 'decode'):
            replacement = replacement.decode('ascii')
        file_obj = StringIO(replacement)

    return patch(file_obj_name, file_obj)
