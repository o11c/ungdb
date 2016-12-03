import enum


def quote(s):
    s.encode('ascii') # just for side-effects
    return '"%s"' % ''.join('\\%03o' % ord(c) for c in s)

def flag(b):
    return '' if b else None


class PrintValues(enum.IntEnum):
    no_values = 0
    all_values = 1
    simple_values = 2


class DisassembleMode(enum.IntEnum):
    disassembly_only = 0
    mixed_source_and_disassembly_deprecated = 1
    disassembly_with_raw opcodes = 2
    mixed_source_and_disassembly_with_raw_opcodes_deprecated = 3
    mixed_source_and_disassembly = 4
    mixed_source_and_disassembly_with_raw_opcodes = 5


class MiCommandsMixin(object):
    ''' Mixin that provides convenient functions to call gdb commands.

        All MI commands are provided, though arguments are a WIP.

        Additionally, some CLI commands are provided.
    '''

    def _mi(self, cmd, args, kwargs, extra_lines=[]):
        token = next(self.counter)
        bits = ['%d%s' % (token, cmd)]
        has_kwargs = False
        for (k, v) in sorted(kwargs.items()):
            if v is None:
                continue
            has_kwargs = True
            k = k.replace('_', '-')
            if len(k) > 1:
                bits.append('--' + k)
            else:
                bits.append('-' + k)
            if v:
                bits.append(quote(v))
        if args:
            if has_kwargs:
                bits.append('--')
            for a in args:
                if a is None:
                    continue
                bits.append(quote(a))
        line = ' '.join(bits)
        if extra_lines:
            line = '\n'.join([line] + extra_lines)
        return self.raw_command(token, line)

    # Breakpoint Commands
    def mi_break_after(self, number, count):
        args = [number, count]
        kwargs = {}
        return self._mi('-break-after', args, kwargs)

    def mi_break_commands(self, number, *commands):
        args = [number] + commands
        kwargs = {}
        return self._mi('-break-commands', args, kwargs)

    def mi_break_condition(self, number, expr):
        args = [number, expr]
        kwargs = {}
        return self._mi('-break-condition', args, kwargs)

    def mi_break_delete(self, *breakpoints):
        args = breakpoints
        kwargs = {}
        return self._mi('-break-delete', args, kwargs)

    def mi_break_disable(self, *breakpoints):
        args = breakpoints
        kwargs = {}
        return self._mi('-break-disable', args, kwargs)

    def mi_break_enable(self, *breakpoints):
        args = breakpoints
        kwargs = {}
        return self._mi('-break-enable', args, kwargs)

    def mi_break_info(self, breakpoint):
        args = [breakpoint]
        kwargs = {}
        return self._mi('-break-info', args, kwargs)

    def mi_break_insert(self, location=None, temporary=False, hardware=False, pending=False, disabled=False, tracepoint=False, condition=None, ignore_count=None, thread=None):
        args = [location]
        kwargs = {
            't': flag(temporary),
            'h': flag(hardware),
            'f': flag(pending),
            'd': flag(disabled),
            'a': flag(tracepoint),
            'c': condition,
            'i': ignore_count,
            'p': thread,
        }
        return self._mi('-break-insert', args, kwargs)

    def mi_dprintf_insert(self, location=None, format=None, *arguments, temporary=False, pending=False, disabled=False, condition=None, ignore_count=None, thread=None):
        args = [location, format] + arguments
        kwargs = {
            't': flag(temporary),
            'f': flag(pending),
            'd': flag(disabled),
            'c': condition,
            'i': ignore_count,
            'p': thread,
        }
        return self._mi('-dprintf-insert', args, kwargs)

    def mi_break_list(self):
        args = []
        kwargs = {}
        return self._mi('-break-list', args, kwargs)

    def mi_break_passcount(self, tracepoint_number, passcount):
        args = [tracepoint_number, passcount]
        kwargs = {}
        return self._mi('-break-passcount', args, kwargs)

    def mi_break_watch(self, access=False, read=False):
        args = []
        kwargs = {
            'a': flag(access),
            'r': flag(read),
        }
        return self._mi('-break-watch', args, kwargs)

    # Shared Library Catchpoint Commands
    def mi_catch_load(self, regexp, temporary=False, disabled=False):
        args = [regexp]
        kwargs = {
            't': flag(temporary),
            'd': flag(disabled),
        }
        return self._mi('-catch-load', args, kwargs)

    def mi_catch_unload(self, regexp, temporary=False, disabled=False):
        args = [regexp]
        kwargs = {
            't': flag(temporary),
            'd': flag(disabled),
        }
        return self._mi('-catch-unload', args, kwargs)

    # Ada Exception Catchpoint Commands
    def mi_catch_assert(self, condition=None, disabled=False, temporary=False):
        args = []
        kwargs = {
            'c': condition,
            'd': flag(disabled),
            't': flag(temporary),
        }
        return self._mi('-catch-assert', args, kwargs)

    def mi_catch_exception(self, condition=None, disabled=False, exception_name=None, temporary=False, unhandled=False):
        args = []
        kwargs = {
            'c': condition,
            'd': flag(disabled),
            'e': exception_name,
            't': flag(temporary),
            'u': flag(unhandled),
        }
        return self._mi('-catch-exception', args, kwargs)

    # Progam Context
    def mi_exec_arguments(self, *args):
        args = args
        kwargs = {}
        return self._mi('-exec-arguments', args, kwargs)

    def mi_environment_cd(self, pathdir):
        args = [pathdir]
        kwargs = {}
        return self._mi('-environment-cd', args, kwargs)

    def mi_environment_directory(self, *pathdirs, reset=False):
        args = pathdirs
        kwargs = {
            'r': flag(reset),
        }
        return self._mi('-environment-directory', args, kwargs)

    def mi_environment_path(self, *pathdirs, reset=False):
        args = pathdirs
        kwargs = {
            'r': flag(reset),
        }
        return self._mi('-environment-path', args, kwargs)

    def mi_environment_pwd(self):
        args = []
        kwargs = {}
        return self._mi('-environment-pwd', args, kwargs)

    # Thread Commands
    def mi_thread_info(self, thread_id=None):
        args = [thread_id]
        kwargs = {}
        return self._mi('-thread-info', args, kwargs)

    def mi_thread_list_ids(self):
        args = []
        kwargs = {}
        return self._mi('-thread-list-ids', args, kwargs)

    def mi_thread_select(self, thread_select):
        args = [thread_select]
        kwargs = {}
        return self._mi('-thread-select', args, kwargs)

    # Ada Tasking Commands
    def mi_ada_task_info(self, task_id=None):
        args = [task_id]
        kwargs = {}
        return self._mi('-ada-task-info', args, kwargs)

    # Program Execution
    def mi_exec_continue(self, reverse=False, all=False, thread_group=None):
        args = []
        kwargs = {
            'reverse': flag(reverse),
            'all': flag(all),
            'thread_group': thread_group,
        }
        return self._mi('-exec-continue', args, kwargs)

    def mi_exec_finish(self, reverse=False):
        args = []
        kwargs = {
            'reverse': flag(reverse),
        }
        return self._mi('-exec-finish', args, kwargs)

    def mi_exec_interrupt(self, all=False, thread_group=None):
        args = []
        kwargs = {
            'all': flag(all),
            'thread_group': thread_group,
        }
        return self._mi('-exec-interrupt', args, kwargs)

    def mi_exec_jump(self, location):
        args = [location]
        kwargs = {}
        return self._mi('-exec-jump', args, kwargs)

    def mi_exec_next(self, reverse=False):
        args = []
        kwargs = {
            'reverse': flag(reverse),
        }
        return self._mi('-exec-next', args, kwargs)

    def mi_exec_next_instruction(self, reverse=False):
        args = []
        kwargs = {
            'reverse': flag(reverse),
        }
        return self._mi('-exec-next-instruction', args, kwargs)

    def mi_exec_return(self):
        args = []
        kwargs = {}
        return self._mi('-exec-return', args, kwargs)

    def mi_exec_run(self, all=False, thread_group=None, start=False):
        args = []
        kwargs = {
            'all': flag(all),
            'thread_group': thread_group,
            'start': flag(start),
        }
        return self._mi('-exec-run', args, kwargs)

    def mi_exec_step(self, reverse=False):
        args = []
        kwargs = {
            'reverse': flag(reverse),
        }
        return self._mi('-exec-step', args, kwargs)

    def mi_exec_step_instruction(self, reverse=False):
        args = []
        kwargs = {
            'reverse': flag(reverse),
        }
        return self._mi('-exec-step-instruction', args, kwargs)

    def mi_exec_until(self, location=None):
        args = [location]
        kwargs = {}
        return self._mi('-exec-until', args, kwargs)

    # Stack Manipulation Commands
    def mi_enable_frame_filters(self):
        args = []
        kwargs = {}
        return self._mi('-enable-frame-filters', args, kwargs)

    def mi_stack_info_frame(self):
        args = []
        kwargs = {}
        return self._mi('-stack-info-frame', args, kwargs)

    def mi_stack_info_depth(self, max_depth):
        args = [max_depth]
        kwargs = {}
        return self._mi('-stack-info-depth', args, kwargs)

    def mi_stack_list_arguments(self, print_values, low_frame=None, high_frame=None, no_frame_filters=False, skip_unavailable=False):
        args = ['--' + print_values.name.replace('_', '-'), low_frame, high_frame]
        kwargs = {
            no_frame_filters = flag(no_frame_filters),
            skip_unavailable = flag(skip_unavailable),
        }
        return self._mi('-stack-list-arguments', args, kwargs)

    def mi_stack_list_frames(self, low_frame=None, high_frame=None, no_frame_filters=False):
        args = [low_frame, high_frame]
        kwargs = {
            no_frame_filters = flag(no_frame_filters),
        }
        return self._mi('-stack-list-frames', args, kwargs)

    def mi_stack_list_locals(self, print_values, no_frame_filters=False, skip_unavailable=False):
        args = [print_values]
        kwargs = {
            no_frame_filters = flag(no_frame_filters),
            skip_unavailable = flag(skip_unavailable),
        }
        return self._mi('-stack-list-locals', args, kwargs)

    def mi_stack_list_variables(self, print_values, no_frame_filters=False, skip_unavailable=False):
        args = [print_values]
        kwargs = {
            no_frame_filters = flag(no_frame_filters),
            skip_unavailable = flag(skip_unavailable),
        }
        return self._mi('-stack-list-variables', args, kwargs)

    def mi_stack_select_frame(self, framenum):
        args = [framenum]
        kwargs = {}
        return self._mi('-stack-select-frame', args, kwargs)

    # Variable Objects
    def mi_enable_pretty_printing(self):
        args = []
        kwargs = {}
        return self._mi('-enable-pretty-printing', args, kwargs)

    def mi_var_create(self, name, frame_addr, expression):
        args = [name, frame_addr, expression]
        kwargs = {}
        return self._mi('-var-create', args, kwargs)

    def mi_var_delete(self, name, children_only=False):
        args = [name]
        kwargs = {
            'c': flag(children_only),
        }
        return self._mi('-var-delete', args, kwargs)

    def mi_var_set_format(self, name, format_spec):
        args = [name, format_spec]
        kwargs = {}
        return self._mi('-var-set-format', args, kwargs)

    def mi_var_show_format(self, name):
        args = [name]
        kwargs = {}
        return self._mi('-var-show-format', args, kwargs)

    def mi_var_info_num_children(self, name):
        args = [name]
        kwargs = {}
        return self._mi('-var-info-num-children', args, kwargs)

    def mi_var_list_children(self, name, from_=None, to=None, print_values=PrintValues.no_values):
        args = [name, from_, to]
        kwargs = {
            # This is possible here because there are no other kwargs.
            print_values.name: '',
        }
        return self._mi('-var-list-children', args, kwargs)

    def mi_var_info_type(self, name):
        args = [name]
        kwargs = {}
        return self._mi('-var-info-type', args, kwargs)

    def mi_var_info_expression(self, name):
        args = [name]
        kwargs = {}
        return self._mi('-var-info-expression', args, kwargs)

    def mi_var_info_path_expression(self, name):
        args = [name]
        kwargs = {}
        return self._mi('-var-info-path-expression', args, kwargs)

    def mi_var_show_attributes(self, name):
        args = [name]
        kwargs = {}
        return self._mi('-var-show-attributes', args, kwargs)

    def mi_var_evaluate_expression(self, name, format_spec=None):
        args = [name]
        kwargs = {
            'f': format_spec
        }
        return self._mi('-var-evaluate-expression', args, kwargs)

    def mi_var_assign(self, name, expression):
        args = [name, expression]
        kwargs = {}
        return self._mi('-var-assign', args, kwargs)

    def mi_var_update(self, name, print_values=PrintValues.no_values):
        args = [name]
        kwargs = {
            # This is possible here because there are no other kwargs.
            print_values.name: '',
        }
        return self._mi('-var-update', args, kwargs)

    def mi_var_set_frozen(self, name, flag):
        args = [name, int.__str__(flag)]
        kwargs = {}
        return self._mi('-var-set-frozen', args, kwargs)

    def mi_var_set_update_range(self, name, from_, to):
        args = [name, from_, to]
        kwargs = {}
        return self._mi('-var-set-update-range', args, kwargs)

    def mi_var_set_visualizer(self, name, visualizer):
        args = [name, visualizer]
        kwargs = {}
        return self._mi('-var-set-visualizer', args, kwargs)

    # Data Manipulation
    def mi_data_disassemble(self, mode, start_addr=None, end_addr=None, filename=None, linenum=None, lines=None):
        args = [mode.value]
        kwargs = {
            's': start_addr,
            'e': end_addr,
            'f': filename,
            'l': linenum,
            'n': lines,
        }
        return self._mi('-data-disassemble', args, kwargs)

    def mi_data_evaluate_expression(self, expr):
        args = [expr]
        kwargs = {}
        return self._mi('-data-evaluate-expression', args, kwargs)

    def mi_data_list_changed_registers(self):
        args = []
        kwargs = {}
        return self._mi('-data-list-changed-registers', args, kwargs)

    def mi_data_list_register_names(self, *regnos):
        args = regnos
        kwargs = {}
        return self._mi('-data-list-register-names', args, kwargs)

    def mi_data_list_register_values(self, fmt, *regnos, skip_unavailable=False):
        args = [fmt] + regnos
        kwargs = {
            skip_unavailable = flag(skip_unavailable),
        }
        return self._mi('-data-list-register-values', args, kwargs)

    def mi_data_write_register_values(self, *args, **kwargs):
        assert False, 'not documented = not implemented'
        #args = []
        #kwargs = {}
        return self._mi('-data-write-register-values', args, kwargs)

    def mi_data_read_memory_bytes(self, address, count, offset=None):
        args = [address, count]
        kwargs = {
            'o': offset,
        }
        return self._mi('-data-read-memory-bytes', args, kwargs)

    def mi_data_write_memory_bytes(self, address, contents, count=None):
        args = [address, contents, count]
        kwargs = {}
        return self._mi('-data-write-memory-bytes', args, kwargs)

    # Tracepoint Commands
    def mi_trace_find(self, mode, *parameters):
        args = [mode] + parameters
        kwargs = {}
        return self._mi('-trace-find', args, kwargs)

    def mi_trace_define_variable(self, name, value=None):
        args = [name, value]
        kwargs = {}
        return self._mi('-trace-define-variable', args, kwargs)

    def mi_trace_frame_collected(self, var_print_values=None, comp_print_values=None, registers_format=None, memory_contents=False):
        args = []
        kwargs = {
            'var_print_values': var_print_values,
            'comp_print_values': comp_print_values,
            'registers_format': registers_format,
            'memory_contents': flag(memory_contents),
        }
        return self._mi('-trace-frame-collected', args, kwargs)

    def mi_trace_list_variables(self):
        args = []
        kwargs = {}
        return self._mi('-trace-list-variables', args, kwargs)

    def mi_trace_save(self, filename, remote=False):
        args = [filename]
        kwargs = {
            'r': flag(remote),
        }
        return self._mi('-trace-save', args, kwargs)

    def mi_trace_start(self):
        args = []
        kwargs = {}
        return self._mi('-trace-start', args, kwargs)

    def mi_trace_status(self):
        args = []
        kwargs = {}
        return self._mi('-trace-status', args, kwargs)

    def mi_trace_stop(self):
        args = []
        kwargs = {}
        return self._mi('-trace-stop', args, kwargs)

    # Symbol Query Commands
    def mi_symbol_list_lines(self, filename):
        args = [filename]
        kwargs = {}
        return self._mi('-symbol-list-lines', args, kwargs)

    # File Commands
    def mi_file_exec_and_symbols(self, file=None):
        args = [file]
        kwargs = {}
        return self._mi('-file-exec-and-symbols', args, kwargs)

    def mi_file_exec_file(self, file=None):
        args = [file]
        kwargs = {}
        return self._mi('-file-exec-file', args, kwargs)

    def mi_file_list_exec_source_file(self):
        args = []
        kwargs = {}
        return self._mi('-file-list-exec-source-file', args, kwargs)

    def mi_file_list_exec_source_files(self):
        args = []
        kwargs = {}
        return self._mi('-file-list-exec-source-files', args, kwargs)

    def mi_file_symbol_file(self, file=None):
        args = [file]
        kwargs = {}
        return self._mi('-file-symbol-file', args, kwargs)

    # Target Manipulation Commands
    def mi_target_attach(self, pid_or_gid_or_file):
        args = [pid_or_gid_or_file]
        kwargs = {}
        return self._mi('-target-attach', args, kwargs)

    def mi_target_detach(self, pid_or_gid=None):
        args = [pid_or_gid]
        kwargs = {}
        return self._mi('-target-detach', args, kwargs)

    def mi_target_disconnect(self):
        args = []
        kwargs = {}
        return self._mi('-target-disconnect', args, kwargs)

    def mi_target_download(self):
        args = []
        kwargs = {}
        return self._mi('-target-download', args, kwargs)

    def mi_target_select(self, type, *parameters):
        args = [type] + parameters
        kwargs = {}
        return self._mi('-target-select', args, kwargs)

    # File Transfer Commands
    def mi_target_file_put(self, hostfile, targetfile):
        args = [hostfile, targetfile]
        kwargs = {}
        return self._mi('-target-file-put', args, kwargs)

    def mi_target_file_get(self, targetfile, hostfile):
        args = [targetfile, hostfile]
        kwargs = {}
        return self._mi('-target-file-get', args, kwargs)

    def mi_target_file_delete(self, targetfile):
        args = [targetfile]
        kwargs = {}
        return self._mi('-target-file-delete', args, kwargs)

    # Ada Exceptions
    def mi_info_ada_exceptions(self, regexp=None):
        args = [regexp]
        kwargs = {}
        return self._mi('-info-ada-exceptions', args, kwargs)

    # Support Commands
    def mi_info_gdb_mi_command(self, cmd_name):
        args = [cmd_name]
        kwargs = {}
        return self._mi('-info-gdb-mi-command', args, kwargs)

    def mi_list_features(self):
        args = []
        kwargs = {}
        return self._mi('-list-features', args, kwargs)

    def mi_list_target_features(self):
        args = []
        kwargs = {}
        return self._mi('-list-target-features', args, kwargs)

    # Miscellaneous Commands
    def mi_gdb_exit(self):
        #args = []
        #kwargs = {}
        return self._mi('-gdb-exit', args, kwargs)

    def mi_gdb_set(self):
        args = []
        kwargs = {}
        return self._mi('-gdb-set', args, kwargs)

    def mi_gdb_show(self):
        args = []
        kwargs = {}
        return self._mi('-gdb-show', args, kwargs)

    def mi_gdb_version(self):
        args = []
        kwargs = {}
        return self._mi('-gdb-version', args, kwargs)

    def mi_list_thread_groups(self, groups, available=False, recurse=None):
        args = groups
        kwargs = {
            'available': flag(available),
            'recurse': recurse,
        }
        return self._mi('-list-thread-groups', args, kwargs)

    def mi_info_os(self, *args, **kwargs):
        #args = []
        #kwargs = {}
        return self._mi('-info-os', args, kwargs)

    def mi_add_inferior(self):
        args = []
        kwargs = {}
        return self._mi('-add-inferior', args, kwargs)

    def mi_remove_inferior(self, inferior):
        args = [inferior]
        kwargs = {}
        return self._mi('-remove-inferior', args, kwargs)

    def mi_interpreter_exec(self, interpreter, cmd, extra_lines=[]):
        args = [interpreter, cmd]
        kwargs = {}
        return self._mi('-interpreter-exec', args, kwargs, extra_lines)

    def mi_inferior_tty_set(self, tty):
        args = [tty]
        kwargs = {}
        return self._mi('-inferior-tty-set', args, kwargs)

    def mi_inferior_tty_show(self):
        args = []
        kwargs = {}
        return self._mi('-inferior-tty-show', args, kwargs)

    def mi_enable_timings(self, flag):
        args = ['yes' if flag else 'no']
        kwargs = {}
        return self._mi('-enable-timings', args, kwargs)


    def _cli(self, *args):
        # Using this, rather than calling commands directly, will disable
        # the (deprecated) logged copy of the input.
        # Note that commands that take a block (using a secondary prompt)
        # do not work, they will hang. Use cli_multiline instead.
        return self.mi_interpreter_exec('console', ' '.join(args))

    def _cli_multiline(self, *lines):
        # Bypass the quoting machinery for multi-line commands.
        return self.mi_interpreter_exec('console', lines[0], lines[1:])

    def cli_nop(self):
        return self._cli()

    def cli_help(self, subject=None):
        if subject is not None:
            return self._cli('help', subject)
        else:
            return self._cli('help')

    def cli_apropos(self, regex):
        return self._cli('apropos', regex)
