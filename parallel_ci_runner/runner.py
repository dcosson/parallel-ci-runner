from datetime import datetime, timedelta
import subprocess
import sys
from threading import Thread
import time
try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x

from .logger import logger
from .utils import time_duration_pretty, format_with_colors


class CIRunner(object):

    def __init__(self):
        self.command_steps = []
        self.cleanup_steps = []

    def add_serial_command_step(self, command, timeout=None, stdout_callback=None):
        """ Add a command to run.
            A command is a function that takes in process number and returns a
            string to be executed as a subcommand in a shell.
        """
        cmd = Command(command, stdout_callback=stdout_callback)
        self.command_steps.append((1, [cmd], timeout))

    def add_parallel_command_step(self, commands_list, timeout=None):
        cmd_list = [Command(c) for c in commands_list]
        self.command_steps.append((len(cmd_list), cmd_list, timeout))

    def add_serial_cleanup_step(self, command, timeout=None):
        cmd = Command(command)
        self.cleanup_steps.append((1, [cmd], timeout))

    def add_parallel_cleanup_step(self, commands_list, timeout=None):
        cmd_list = [Command(c) for c in commands_list]
        self.cleanup_steps.append((len(cmd_list), cmd_list, timeout))

    def _run_single(self, cmd_string):
        return subprocess.Popen(
            cmd_string,
            shell=True,
            stdout=subprocess.PIPE,
        )

    def _run_command_step(self, command_step, step_num, num_steps, timeout,
                          is_cleanup):
        self.log_step(step_num, num_steps, len(command_step), is_cleanup)
        procs = []
        tick_seconds = 1
        log_status_every_seconds = 30
        started_at = datetime.now()
        next_log_status_at = started_at + timedelta(seconds=log_status_every_seconds)
        # launch commands
        for i, command in enumerate(command_step):
            proc_num = i + 1
            cmd_string = command.command_fn(proc_num)
            proc = Process.create(proc_num, cmd_string, timeout, command.stdout_callback)
            procs.append(proc)
        pending_procs = procs

        # poll til completion or timeout
        while True:
            for proc in pending_procs:
                proc.update_status()

            # log results of any that have completed
            newly_complete_procs = [proc for proc in pending_procs if proc.is_complete()]
            for proc in newly_complete_procs:
                proc.log_result()

            # kill & log results for any procs past timeout
            timed_out_procs = [proc for proc in pending_procs if proc.is_timed_out()]
            for proc in timed_out_procs:
                proc.kill()
                proc.log_result()

            # update pending_procs list for next loop tick
            pending_procs = [proc for proc in procs if proc.is_pending()]

            # exit if all proccesses have finished
            if len(pending_procs) == 0:
                return procs

            # if only 1 proc still running, start logging its output in real time
            if len(pending_procs) == 1:
                pending_procs[0].log_latest_output()

            # Log time running if necessary, then sleep til next tick
            now = datetime.now()
            if now > next_log_status_at:
                diff = next_log_status_at - started_at
                logger.info("Running for " + time_duration_pretty(diff.seconds))
                next_log_status_at += timedelta(seconds=log_status_every_seconds)

            time.sleep(tick_seconds)

    def run(self):
        num_steps = len(self.command_steps)
        for i, command_step_tuple in enumerate(self.command_steps):
            _, command_step, timeout = command_step_tuple
            procs = self._run_command_step(
                command_step, i + 1, num_steps, timeout, False)
            if not self.all_succeeded(procs):
                logger.info("")
                logger.info(format_with_colors(
                    "{red}Exiting due to 1 or more commands failed{end}"))
                logger.info("")
                self._run_cleanup()
                sys.exit(1)
        self._run_cleanup()

    def _run_cleanup(self):
        num_steps = len(self.cleanup_steps)
        for i, command_step_tuple in enumerate(self.cleanup_steps):
            _, command_step, timeout = command_step_tuple
            # in cleanup, run all steps regardless of if any previous ones fail
            self._run_command_step(command_step, i + 1, num_steps, timeout, True)

    @classmethod
    def all_succeeded(cls, procs):
        return all(p.status == 0 for p in procs)

    @classmethod
    def log_step(cls, step_num, num_steps, num_commands, is_cleanup):
        cleanup_str = "Cleanup " if is_cleanup else "Running "
        info = "{0}step {1} of {2}".format(cleanup_str, step_num, num_steps)
        if num_commands == 1:
            info += " (single command)"
        else:
            info += " ({0} commands in parallel)".format(num_commands)
        desired_len = 100
        pre_len = (desired_len - len(info)) // 2 - 1
        pre_str = "=" * pre_len
        post_len = desired_len - len(info) - pre_len - 2
        post_str = "=" * post_len
        info = format_with_colors("{0} {1} {2}", pre_str, info, post_str)
        logger.info(info)


class Command(object):
    def __init__(self, command, stdout_callback=None):
        if hasattr(command, '__call__'):
            self.command_fn = command
        else:
            def wrapped_command(i):
                return command
            self.command_fn = wrapped_command
        self.stdout_callback = stdout_callback


class Process(object):
    @classmethod
    def create(cls, number, cmd_string, timeout, stdout_callback):
        """ Run the given command string in a shell as a new process,
        initializing a Process object wrapper for it.
        """
        p = subprocess.Popen(
            cmd_string,
            shell=True,
            stdout=subprocess.PIPE,
        )
        obj = cls(number, cmd_string, p, datetime.now(), timeout, stdout_callback)
        obj.start_output_listener()
        return obj

    def __init__(self, number, cmd_string, popen_process,
                 started_at, timeout, stdout_callback):
        self.number = number
        self.cmd_string = cmd_string
        self.popen_process = popen_process
        self.started_at = started_at
        self.timeout = timeout
        self.stdout_callback = stdout_callback
        self.status = None
        self.started_reading_output = False

    def update_status(self):
        self.status = self.popen_process.poll()
        timeout_diff = datetime.now() - self.started_at
        if self.timeout is not None and self.is_pending() and timeout_diff >= self.timeout:
            self.status = -1

    def start_output_listener(self):
        def enqueue_output(out, queue):
            for line in iter(out.readline, b''):
                queue.put(line)
            out.close()

        self.stdout_q = Queue()
        self.stdout_reader_t = Thread(
            target=enqueue_output, args=(self.popen_process.stdout, self.stdout_q))
        self.stdout_reader_t.daemon = True  # make sure thread exits when program does
        self.stdout_reader_t.start()

    def latest_output(self):
        self.started_reading_output = True
        while True:
            try:
                line = self.stdout_q.get_nowait()
                yield line.rstrip(b'\n').rstrip(b'\r').decode('utf-8')
            except Empty:
                raise StopIteration()

    def log_latest_output(self):
        if not self.started_reading_output:
            logger.info("Output for {0}:".format(self.number))
        for line in self.latest_output():
            logger.info(line)

    # Process can be either: pending, complete, or timed_out.
    # Complete processes can be successful or failed
    def is_pending(self):
        return self.status is None

    def is_complete(self):
        return self.status is not None and self.status >= 0

    def is_completed_successful(self):
        return self.status is not None and self.status == 0

    def is_completed_failed(self):
        return self.status is not None and self.status > 0

    def is_timed_out(self):
        return self.status is not None and self.status == -1

    def kill(self):
        self.popen_process.kill()  # kill -9 the process

    def log_result(self):
        if self.started_reading_output:  # output is above, log blank line before status
            logger.info("")
        if self.is_pending():
            col = "{yellow}"
            exit_phrase = "still running"
        elif self.is_completed_successful():
            col = "{green}"
            exit_phrase = "exited successfully"
        elif self.is_completed_failed():
            col = "{red}"
            exit_phrase = "failed with exit code {0}".format(self.status)
        elif self.is_timed_out():
            col = "{red}"
            exit_phrase = "timed out after {0}".format(time_duration_pretty(self.timeout))
        logger.info(format_with_colors(
            col + "Command {0} {1}{end}", self.number, exit_phrase))
        logger.info(format_with_colors(col + self.cmd_string + "{end}"))
        if not self.started_reading_output:
            # at this point, process is finished so the non-blocking
            # latest_output already has all output and we don't have to block.
            # And output is below, log blank line after status
            logger.info("")
            self.log_latest_output()
        logger.info("-" * 100)
