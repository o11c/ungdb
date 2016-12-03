import itertools
import os
import shutil

from twisted.internet import endpoints
from twisted.protocols import basic

from .mixin import MiCommandsMixin
from .parser import parse


class GdbMiProtocol(basic.LineOnlyReceiver, MiCommandsMixin):
    ''' Twisted Protocol that parses GDB/MI lines.

        Nothing interesting is done with them - subclass me!

        You should subclass this to actually *do* something with the MI.

        Note: all methods provided by this package use snake_case. Only
        methods inherited from twisted use camelCase.
    '''
    MAX_LENGTH = float('inf')
    delimiter = b'\n'

    @property
    def _proc(self):
        return self.transport._process

    def connectionMade(self):
        ''' Implements twisted's interface.
        '''
        # Work around a Twisted bug.
        if not hasattr(self.transport, 'disconnecting'):
            self.transport.disconnecting = False

        self.counter = itertools.count()
        self.handle_begin()

    def connectionLost(self, reason):
        ''' Implements twisted's interface.
        '''
        # e.g. someone called `self.transport.loseConnection()`
        del self.counter
        self.handle_end()

    def lineReceived(self, line):
        ''' Implements twisted's interface.
        '''
        line = line.decode('ascii')
        record = parse(line)
        self.handle_record(record)

    def handle_begin(self):
        pass

    def handle_end(self):
        pass

    def handle_record(self, record):
        raise NotImplementedError()

    def raw_command(self, token, line):
        line = line.encode('ascii')
        self.sendLine(line)
        return token

    def do_signal_interrupt(self):
        ''' Ask GDB to sit down, shut up, and pay attention.

            You should probably use mi_exec_interrupt() instead,
            but in certain cases that may not be appropriate.
        '''
        self._proc.signalProcess('INT')
    def do_signal_terminate(self):
        ''' Kill GDB politely.

            You should probably use mi_gdb_exit() instead.
        '''
        self._proc.signalProcess('TERM')
    def do_signal_kill(self):
        ''' Kill GDB unstoppably.

            You should probably use mi_gdb_exit() instead.
        '''
        self._proc.signalProcess('KILL')
    def do_close(self):
        ''' Close I/O streams, letting GDB die out of our control.

            You should probably use mi_gdb_exit() instead.
        '''
        self.transport.loseConnection()


class ExecGdbMiEndpoint(endpoints.ProcessEndpoint):
    def __init__(self, reactor, exe='gdb'):
        ''' Endpoint that spawns an instance of GDB/MI.
        '''
        full_exe = shutil.which(exe)
        args = [exe, '--interpreter=mi2']
        env = os.environ.copy() # The default is retarded.
        #env['SHELL'] = 'gdb-xterm-sh'
        # Default is to pipe stderr, but passthrough is a better idea.
        #childFDs= { 0: "w", 1: "r", 2: "r" }
        childFDs = { 0: "w", 1: "r", 2: 2 }
        endpoints.ProcessEndpoint.__init__(self, reactor, full_exe,
                args=args, env=env, childFDs=childFDs)
