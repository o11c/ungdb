from collections import OrderedDict, deque
import importlib

from twisted.internet import base

from .mixin import MiCommandsMixin
from . import parser
from .protocol import GdbMiProtocol, ExecGdbMiEndpoint


def _init_reactor_map(__reactor_map=OrderedDict()):
    if not __reactor_map:
        from twisted.application import reactors

        # Delay the import of twisted.plugins as long as possible
        for r in reactors.getReactorTypes():
            try:
                m = importlib.import_module(r.moduleName)
            except ImportError:
                continue
            if m.__name__ != m.install.__module__:
                m = importlib.import_module(m.install.__module__)
            __reactor_map[r.shortName] = m
        assert __reactor_map
    return __reactor_map

def _guess_reactor_class(module):
    rv = []
    for name in module.install.__code__.co_names:
        cls = getattr(module, name, None)
        if isinstance(cls, type):
            if issubclass(cls, base.ReactorBase):
                assert cls.__module__ == module.__name__
                rv.append(cls)
    assert len(rv) == 1
    return rv[0]

def guess_reactor_class(name='default'):
    module = _init_reactor_map()[name]
    return _guess_reactor_class(module)

def list_reactor_classes():
    for key, module in _init_reactor_map().items():
        yield key, _guess_reactor_class(module)


# Is it actually worth making this a separate class, or should I just
# merge them?
class GdbMi(MiCommandsMixin):
    ''' Synchronous wrapper for GdbMiProtocol and a twisted reactor.
    '''
    def __init__(self, exe='gdb'):
        from twisted.internet import endpoints

        reactor = (guess_reactor_class())()
        endpoint = endpoint = ExecGdbMiEndpoint(reactor, exe=exe)
        proto = _SyncGdbMiProtocol(reactor)
        _ = endpoints.connectProtocol(endpoint, proto)

    def raw_command(self, token, line):
        self._proto.sendLine(line.encode('ascii'))
        return self._proto.wait_for_replies()

    @property
    def counter(self):
        return self._proto.counter

    @property
    def _proc(self):
        return self._proto._proc


class _SyncGdbMiProtocol(GdbMiProtocol):
    def __init__(self, reactor):
        self._reactor = reactor
        self._records = []
        self._hook = None
        self._queue = deque()
        self._running = False
    def handle_begin(self):
        assert self._hook is None
        # There is an initial set of records. Pull them, and put them
        # into the list for returning.
        # Note, significantly, that they are *not* put in the queue, and
        # thus are *not* subject to hooking, which would break everything
        # since the whole point of this is to get rid of the initial
        # PromptRecord.
        self._running = True
        self._records = self.wait_for_replies()
    def handle_end(self):
        # Set hook to None, as if it was satisfied.
        self._hook = None
        self._running = False
    def handle_record(self, r):
        if self._hook is not None:
            self._records.append(r)
            if (self._hook)(r):
                self._hook = None
        else:
            self._queue.append(r)
            print('DEBUG:', 'len(_queue) =', len(self._queue))
    def _requeue(self):
        ''' When a new hook has been installed, apply it to old records.
        '''
        while self._hook is not None and self._queue:
            self.handle_record(self._queue.popleft())
    def _pump_once(self):
        ''' Start the reactor, wait for at least one event, then stop it again.

            This will ultimately result in .handle_record() being called
            0 or more times, since FD events are not lines.
        '''
        assert self._running, 'Pumped when not running!'
        self._reactor.iterate(None)
    def _pump_harder(self):
        ''' Pump the reactor until the hook is satisfied.
        '''
        while self._hook is not None:
            self._pump_once()

    def _run_until(self, hook):
        ''' Install a hook, and run until it is satisfied.

            This returns all records up to, and including, the one the
            hook wanted.

            If the hook is entirely satisfied from the queue, this might
            not even need to start the reactor.
        '''
        assert self._hook is None
        self._hook = hook

        self._requeue()
        self._pump_harder()

        rv = self._records
        self._records = []
        return rv

    def wait_for_replies(self):
        ''' "How do we know when the replies are done" is a nontrivial question.

            The documentation is wrong, since notifications can occur *after*
            the ResultRecord (and before the PromptRecord). But, we aren't
            guaranteed to even *get* a PromptRecord, in a couple of cases:

              * if the -gdb-exit command is used, you get a 'exit' ResultRecord,
                followed by some notifications, then EOF.
              * if the quit command is used, or if gdb dies from a signal,
                you get *nothing*, then EOF.

            Additionally, at startup you get one PromptRecord (and a bunch
            of notifications) without asking.
        '''
        # EOF handling is elsewhere.
        return self._run_until(lambda rec: isinstance(rec, parser.PromptRecord))
