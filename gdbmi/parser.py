import abc

import six

from .parse_utils import Tokenizer
from . import utils


class Class(utils.Constant):
    pass
Class._sealed = False
# Note, dashes are replaced with underscores during parsing.
# For the instances created here, they are uppercase class attributes.
# result classes:
Class('done')
Class('connected')
Class('error')
Class('exit')
# async classes:
Class('running')
Class('stopped')
Class('thread_group_added')
Class('thread_group_removed')
Class('thread_group_started')
Class('thread_group_exited')
Class('thread_created')
Class('thread_exited')
Class('thread_selected')
Class('library_loaded')
Class('library_unloaded')
Class('traceframe_changed')
Class('tsv_created')
Class('tsv_deleted')
Class('tsv_modified')
Class('breakpoint_created')
Class('breakpoint_modified')
Class('breakpoint_deleted')
Class('record_started')
Class('record_stopped')
Class('cmd_param_changed')
Class('memory_changed')
# More may be added, but these are here to prevent typos.
Class._sealed = True


class Record:
    _simple = False

    def __init__(self, token, simple_value, complex_class, complex_args):
        if self.__class__._simple:
            assert token is None, 'simple forbids token'
            assert simple_value is not None, 'simple requires value'
            assert complex_class is None, 'simple forbids class'
            assert complex_args is None, 'simple forbids args'
            self._value = simple_value
        else:
            assert simple_value is None, 'complex forbids value'
            assert complex_class is not None, 'complex requires class'
            assert complex_args is not None, 'complex requires args'
            if isinstance(self, ResultRecord) and complex_class == 'running':
                # for async records, the substitution is *not* done.
                complex_class = 'done'
            self._token = token # may be None
            self._class = Class(complex_class)
            for k, v in complex_args.items():
                assert not k.startswith('_'), k
                setattr(self, k, v)

    def __repr__(self):
        cls = self.__class__
        if cls._simple:
            bits = [repr(self._value)]
        else:
            bits = []
            for k, v in sorted(self.__dict__.items()):
                bits.append('%s=%r' % (k, v))
        return '%s(%s)' % (cls.__name__, ', '.join(bits))

class PromptRecord(Record):
    ''' "(gdb)"
    '''

    def __init__(self):
        pass

    def __repr__(self):
        return 'PromptRecord()'

class ResultRecord(Record):
    ''' "^" result-class ( "," result )*
    '''
    _lead = '^'

class OutOfBandRecord(Record):
    pass

class AsyncRecord(OutOfBandRecord):
    pass

class ExecAsyncRecord(AsyncRecord):
    ''' "*" async-class ( "," result )*
    '''
    _lead = '*'

class StatusAsyncRecord(AsyncRecord):
    ''' "+" async-class ( "," result )*
    '''
    _lead = '+'

class NotifyAsyncRecord(AsyncRecord):
    ''' "=" async-class ( "," result )*
    '''
    _lead = '='

class StreamRecord(OutOfBandRecord):
    _simple = True

class ConsoleStreamRecord(StreamRecord):
    ''' "~" c-string
    '''
    _lead = '~'
class TargetStreamRecord(StreamRecord):
    ''' "@" c-string
    '''
    _lead = '@'
class LogStreamRecord(StreamRecord):
    ''' "&" c-string
    '''
    _lead = '&'

_prefix_classes = {
    cls._lead: cls
    for cls in [
        #PromptRecord,
        ResultRecord,
        ExecAsyncRecord,
        StatusAsyncRecord,
        NotifyAsyncRecord,
        ConsoleStreamRecord,
        TargetStreamRecord,
        LogStreamRecord,
]}


_escapes = {
    'a': b'\a',
    'b': b'\b',
    't': b'\t',
    'n': b'\n',
    'v': b'\v',
    'f': b'\f',
    'r': b'\r',
    '"': b'\"',
    '\\': b'\\',
}

def _c_string(s):
    rv = bytearray()
    try:
        s = iter(s[1:-1])
        for c in s:
            if c == '\\':
                c = next(s)
                try:
                    c = ord(_escapes[c])
                except KeyError:
                    # Gdb always emits exactly 3 octal digits.
                    c += next(s)
                    c += next(s)
                    c = int(c, 8)
                    assert 0 <= c < 256, 'invalid'
                    assert c >= 127 or (0 < c < 32 and not (7 <= c <= 13)), 'noncanonical'
            else:
                c = ord(c)
                assert 32 <= c <= 126, 'nonprintable'
                assert c != 34 and c != 92, 'unescaped'
            rv.append(c)
        return bytes(rv)
    except StopIteration:
        assert False, rv

def nop(v):
    return v

tokenizer = Tokenizer([
    ('INTEGER', r'\d+', int),
    ('PREFIX', r'(^|(?<=\d))[+*=^~@&]', nop),
    ('WORD', r'[-A-Za-z0-9]+', lambda s: s.replace('-', '_')),
    ('STRING', r'"([^\\"]|\\.)*"', _c_string),
    ('TUPLE_EMPTY', r'\{}', nop),
    ('TUPLE_BEGIN', r'\{', nop),
    ('TUPLE_END', r'}', nop),
    ('LIST_EMPTY', r'\[]', nop),
    ('LIST_BEGIN', r'\[', nop),
    ('LIST_END', r']', nop),
    ('COMMA', r',', nop),
    ('EQUALS', r'=', nop),
])
tokenizer.END = 'END'

def parse(line):
    # Does not support tokens (yet)
    assert '\n' not in line, repr(line)
    assert '\r' not in line, repr(line)
    if line == '(gdb) ':
        return PromptRecord()

    token = None
    prefix_class = None
    simple_value = None
    complex_class = None
    complex_args = None

    it = iter(tokenizer.tokenize(line))
    def n(sentinel=(tokenizer.END, '')):
        return next(it, sentinel)

    kind, match = n()
    if kind == tokenizer.INTEGER:
        token = match
        kind, match = n()
    assert kind == tokenizer.PREFIX, kind
    prefix_class = _prefix_classes[match]

    kind, match = n()
    if kind == tokenizer.STRING:
        simple_value = match
    else:
        assert kind == tokenizer.WORD, kind
        complex_class = match
        complex_args = {}
        while True:
            kind, match = n()
            if kind != tokenizer.COMMA:
                break
            k, v = _parse_result(n)
            assert k not in complex_args, k
            complex_args[k] = v
    kind, match = n()
    assert kind == tokenizer.END, kind
    return prefix_class(token, simple_value, complex_class, complex_args)

def _parse_result(n):
    kind, match = n()
    assert kind == tokenizer.WORD, kind
    key = match

    kind, match = n()
    assert kind == tokenizer.EQUALS, kind

    value = _parse_value(n)
    return (key, value)

def _parse_value(n, legacy=False):
    kind, match = n()
    if legacy and kind == tokenizer.WORD:
        kind, match = n()
        assert kind == tokenizer.EQUALS, kind
        kind, match = n()
    if kind == tokenizer.TUPLE_EMPTY:
        return {}
    if kind == tokenizer.TUPLE_BEGIN:
        rv = {}
        while True:
            k, v = _parse_result(n)
            assert k not in rv, k
            rv[k] = v
            kind, match = n()
            if kind == tokenizer.COMMA:
                continue
            else:
                break
        assert kind == tokenizer.TUPLE_END, kind
        return rv
    if kind == tokenizer.LIST_EMPTY:
        return []
    if kind == tokenizer.LIST_BEGIN:
        rv = []
        while True:
            rv.append(_parse_value(n, legacy=True))
            kind, match = n()
            if kind == tokenizer.COMMA:
                continue
            else:
                break
        assert kind == tokenizer.LIST_END, kind
        return rv
    assert kind == tokenizer.STRING, kind
    # Tokenizer has already called _c_string as a callback.
    return match
