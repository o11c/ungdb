''' Interfaces to GDB's MI mode.

    There are three ways to use this module:
      * Synchronously, by creating an instance of .sync.GdbMi
        (This is the easiest way for scripting).
      * Asynchronously, by subclassing .protocol.GdbMiProtocol and handling
        events as they come. Note that under normal circumstances, GDB is
        not *truly* asynchronous, but it can be configured to be.
        (This is what you need to do if you're writing a GUI).
      * Manually, calling .parser.parse on lines you have retrieved some
        other way. This could be useful e.g. from Python *within* gdb,
        when using `gdb.execute('interpreter-exec mi ...'), as a superior
        alternative to parsing CLI output. In this case, you might want to
        use `MiCommandsMixin` also.
'''
