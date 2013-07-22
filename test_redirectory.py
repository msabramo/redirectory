import sys
from tempfile import TemporaryFile
from six import u
from six.moves import input, StringIO

from redirectory import (
    stdin_from, stdout_to, stderr_to,
    redirect_file_obj,
)

a_temp_file = TemporaryFile(mode='r+')
a_temp_file.write("one\ntwo\nthree\n")
a_temp_file.flush()
a_temp_file.seek(0)


#----------------------------------------------------------------------------
# redirect an arbitrary file object
#----------------------------------------------------------------------------
def test_redirect_fileobj():
    target = 'test_redirectory.a_temp_file'

    with redirect_file_obj(target, "ONE\nTWO\nTHREE\n"):
        assert a_temp_file.readline() == 'ONE\n'
        assert a_temp_file.readline() == 'TWO\n'
        assert a_temp_file.readline() == 'THREE\n'


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
    with TemporaryFile(mode='r+') as f:
        f.write("one\ntwo\nthree\n")
        f.seek(0)

        with stdin_from(f):
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
