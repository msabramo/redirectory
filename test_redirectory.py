from __future__ import with_statement

import os
import sys
from tempfile import TemporaryFile, NamedTemporaryFile
from six import u
from six.moves import input, StringIO

from redirectory import (
    stdin_from, stdout_to, stderr_to,
    stdout_to_file,
    stdin_fd_from_file,
    stdout_fd_to_file,
    stderr_fd_to_file,
    redirect_file_obj,
)

temp_file_1 = TemporaryFile(mode='r+')
temp_file_1.write("one\ntwo\nthree\n")
temp_file_1.flush()
temp_file_1.seek(0)

temp_file_2 = TemporaryFile(mode='r+')
temp_file_2.write("four\nfive\nsix\n")
temp_file_2.flush()
temp_file_2.seek(0)

temp_file_3 = NamedTemporaryFile(mode='r')


#----------------------------------------------------------------------------
# redirect an arbitrary file object
#----------------------------------------------------------------------------
def test_redirect_fileobj_to_str():
    target = 'test_redirectory.temp_file_1'

    with redirect_file_obj(target, "ONE\nTWO\nTHREE\n"):
        assert temp_file_1.readline() == 'ONE\n'
        assert temp_file_1.readline() == 'TWO\n'
        assert temp_file_1.readline() == 'THREE\n'


#----------------------------------------------------------------------------
# redirect an arbitrary file object
#----------------------------------------------------------------------------
def test_redirect_fileobj_to_fileobj():
    target = 'test_redirectory.temp_file_1'

    with redirect_file_obj(target, temp_file_2):
        assert temp_file_1.readline() == 'four\n'
        assert temp_file_1.readline() == 'five\n'
        assert temp_file_1.readline() == 'six\n'


#----------------------------------------------------------------------------
# stdin_from with a StringIO as input
#----------------------------------------------------------------------------
def test_stdin_from_StringIO():
    a_string = u("bleargh")

    with stdin_from(StringIO(a_string)) as stringio:
        input_return_value = input()

    assert stringio.getvalue() == 'bleargh'
    assert input_return_value == 'bleargh'


#----------------------------------------------------------------------------
# stdin_from with a str as input
#----------------------------------------------------------------------------
def test_stdin_from_str():
    with stdin_from("some text") as stringio:
        input_return_value = input()

    assert stringio.getvalue() == 'some text'
    assert input_return_value == 'some text'


#----------------------------------------------------------------------------
# stdin_from with a file as input
#----------------------------------------------------------------------------
def test_stdin_from_file():
    with stdin_from(temp_file_1):
        assert input() == 'one'
        assert input() == 'two'
        assert input() == 'three'


#----------------------------------------------------------------------------
# stdin_from with an iterable as input
#----------------------------------------------------------------------------
def test_stdin_from_iterable():
    with stdin_from(['one', 'two', 'three']):
        assert input() == 'one'
        assert input() == 'two'
        assert input() == 'three'


#----------------------------------------------------------------------------
# stdin_from with a generator function as input
#----------------------------------------------------------------------------
def test_stdin_from_generator_function():
    def generator_func():
        for word in ['one', 'two', 'three']:
            yield word

    with stdin_from(generator_func()):
        assert input() == 'one'
        assert input() == 'two'
        assert input() == 'three'


#----------------------------------------------------------------------------
# stdin_from with a generator expression as input
#----------------------------------------------------------------------------
def test_stdin_from_generator_expression():
    generator = (x for x in ['one', 'two', 'three'])

    with stdin_from(generator):
        assert input() == 'one'
        assert input() == 'two'
        assert input() == 'three'


#----------------------------------------------------------------------------
# stdout_to captures stdout to a StringIO
#----------------------------------------------------------------------------
def test_stdout_to_StringIO():
    s = StringIO()

    with stdout_to(s):
        sys.stdout.write(u("hello"))

    assert s.getvalue() == 'hello'


#----------------------------------------------------------------------------
# stdout_to captures stdout to a StringIO
#----------------------------------------------------------------------------
def test_stdout_to_as_StringIO():
    with stdout_to() as s:
        sys.stdout.write(u("hello"))

    assert s.getvalue() == 'hello'


#----------------------------------------------------------------------------
# stdout_to_file captures stdout to a file; takes same args as open
#----------------------------------------------------------------------------
def test_stdout_to_file():
    with stdout_to_file(temp_file_3.name):
        sys.stdout.write(u("going to a file\n"))

    with open(temp_file_3.name) as f:
        assert f.read() == 'going to a file\n'


#----------------------------------------------------------------------------
# stdout_to_file appending to a file
#----------------------------------------------------------------------------
def test_stdout_to_file_append():
    # Open file for writing
    with stdout_to_file(temp_file_3.name, 'w'):
        sys.stdout.write(u("1 - going to a file\n"))

    # Open file for appending
    with stdout_to_file(temp_file_3.name, 'a'):
        sys.stdout.write(u("2 - going to a file\n"))

    with open(temp_file_3.name) as f:
        assert f.read() == '1 - going to a file\n2 - going to a file\n'


#----------------------------------------------------------------------------
# stderr_to captures stderr to a StringIO
#----------------------------------------------------------------------------
def test_stderr_to_StringIO():
    s = StringIO()

    with stderr_to(s):
        sys.stderr.write(u("hello"))

    assert s.getvalue() == 'hello'


#----------------------------------------------------------------------------
# stderr_to captures stderr to a StringIO
#----------------------------------------------------------------------------
def test_stderr_to_as_StringIO():
    with stderr_to() as s:
        sys.stderr.write(u("hello"))

    assert s.getvalue() == 'hello'


#----------------------------------------------------------------------------
# Using stdout_to and stdin_from together
# stdout_to suppresses the prompt from `input`
# stdin_from with a str as input
#----------------------------------------------------------------------------
def test_stdout_to_and_stdin():
    with stdout_to():
        with stdin_from("bleargh") as stringio:
            input_return_value = input(u("Type something> "))

    assert stringio.getvalue() == 'bleargh'
    assert input_return_value == 'bleargh'


#----------------------------------------------------------------------------
# stdin_fd_from_file feeds stdin from a file,
# including for subprocesses
#----------------------------------------------------------------------------
def test_stdin_fd_from_file():
    with NamedTemporaryFile() as temp_file_in:
        with NamedTemporaryFile() as temp_file_out:
            temp_file_in.write("print(23 * 2)\n".encode("ascii"))
            temp_file_in.flush()

            with stdin_fd_from_file(temp_file_in.name):
                with stdout_fd_to_file(temp_file_out.name):
                    os.system('python')

            with open(temp_file_out.name) as f:
                assert f.read() == '46\n'


#----------------------------------------------------------------------------
# stdout_fd_to_file captures stdout to a file,
# including for subprocesses
#----------------------------------------------------------------------------
def test_stdout_fd_to_file():
    with NamedTemporaryFile() as temp_file:
        with stdout_fd_to_file(temp_file.name):
            os.system('echo "*** Hello there ***"')

        with open(temp_file.name) as f:
            assert f.read() == '*** Hello there ***\n'


#----------------------------------------------------------------------------
# stdout_fd_to_file captures stdout to a file (os.devnull),
# including for subprocesses
#----------------------------------------------------------------------------
def test_stdout_fd_to_os_devnull():
    with stdout_fd_to_file(os.devnull):
        os.system('echo "*** Hello there ***"')


#----------------------------------------------------------------------------
# stderr_fd_to_file captures stderr to a file,
# including for subprocesses
#----------------------------------------------------------------------------
def test_stderr_fd_to_file():
    with NamedTemporaryFile() as temp_file:
        with stderr_fd_to_file(temp_file.name):
            os.system('echo "*** Hello there ***" 1>&2')

        with open(temp_file.name) as f:
            assert f.read() == '*** Hello there ***\n'


#----------------------------------------------------------------------------
# stderr_fd_to_file captures stderr to a file (os.devnull),
# including for subprocesses
#----------------------------------------------------------------------------
def test_stderr_fd_to_os_devnull():
    with stderr_fd_to_file(os.devnull):
        os.system('echo "*** Hello there ***" 1>&2')
