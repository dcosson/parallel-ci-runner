from datetime import datetime, timedelta
import subprocess
# from threading import Thread
import time
# try:
#     from Queue import Queue, Empty
# except ImportError:
#     from queue import Queue, Empty  # python 3.x

from .logger import logger
from .utils import time_duration_pretty, format_with_colors


class BaseRunner(object):

    def __init__(self):
        # command_steps is an array of "command_steps", where each
        # command_step is an array of commands to be run in parallel
        self.command_steps = []

    def add_serial_command_step(self, command, timeout=None):
        """ Add a command to run.
            A command is a function that takes in process number and returns a
            string to be executed as a subcommand in a shell.
        """
        self.command_steps.append((1, [command], timeout))

    def add_parallel_command_step(self, commands_list, timeout=None):
        self.command_steps.append((len(commands_list), commands_list, timeout))

    def _run_single(self, cmd_string):
        return subprocess.Popen(
            cmd_string,
            shell=True,
            stdout=subprocess.PIPE,
        )

    def _run_command_step(self, command_step, step_num, num_steps, timeout):
        self.log_step(step_num, num_steps, len(command_step))
        procs = []
        tick_seconds = 1
        log_status_every_seconds = 30
        started_at = datetime.now()
        next_log_status_at = started_at + timedelta(seconds=log_status_every_seconds)
        # launch commands
        for i, command in enumerate(command_step):
            proc_num = i + 1
            cmd_string = command(proc_num)
            proc = Process.create(proc_num, cmd_string, timeout)
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
            self._run_command_step(command_step, i + 1, num_steps, timeout)

    @classmethod
    def log_step(cls, step_num, num_steps, num_commands):
        info = "Running step {0} of {1}".format(step_num, num_steps)
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


class Process(object):
    @classmethod
    def create(cls, number, cmd_string, timeout):
        """ Run the given command string in a shell as a new process,
        initializing a Process object wrapper for it.
        """
        p = subprocess.Popen(
            cmd_string,
            shell=True,
            stdout=subprocess.PIPE,
        )
        return cls(number, cmd_string, p, datetime.now(), timeout)

    def __init__(self, number, cmd_string, popen_process,
                 started_at, timeout):
        self.number = number
        self.cmd_string = cmd_string
        self.popen_process = popen_process
        self.started_at = started_at
        self.timeout = timeout
        self.status = None

    def update_status(self):
        self.status = self.popen_process.poll()
        timeout_diff = datetime.now() - self.started_at
        if self.timeout is not None and self.is_pending() and timeout_diff >= self.timeout:
            self.status = -1

    # def output_lines(self):
    #     # process stdout/stderr read() is blocking, which defeats the point of timeout.
    #     # Instead, we can use Queue.get_nowait() for a non-blocking read from
    #     # another process.
    #     def enqueue_output(out, queue):
    #         for line in iter(out.readline, b''):
    #             import ipdb; ipdb.set_trace()
    #             queue.put(line)
    #         out.close()

    #     q = Queue()
    #     t = Thread(target=enqueue_output, args=(self.popen_process.stdout, q))
    #     t.daemon = True  # make sure thread exits when program does
    #     t.start()

    #     lines = []
    #     while True:
    #         try:
    #             line = q.get_nowait()
    #             lines.append(line)
    #         except Empty:
    #             pass
    #     return lines

    def output(self):
        if self.is_timed_out():
            output = "<No output from timed out process>"
        else:
            output = self.popen_process.stdout.read().decode('utf-8')
        return output

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
        logger.info("")
        logger.info("Output:")
        for line in self.output().split('\n'):
            logger.info(line)
