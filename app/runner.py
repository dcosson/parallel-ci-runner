from datetime import datetime, timedelta
import subprocess
import time

from .logger import logger
from .utils import time_duration_pretty, format_with_colors


class BaseRunner(object):

    def __init__(self):
        # command_steps is an array of "command_steps", where each
        # command_step is an array of commands to be run in parallel
        self.command_steps = []

    def add_serial_command_step(self, command):
        """ Add a command to run.
            A command is a function that takes in process number and returns a
            string to be executed as a subcommand in a shell.
        """
        self.command_steps.append([command])

    def add_parallel_command_step(self, commands_list):
        self.command_steps.append(commands_list)

    def _run_single(self, cmd_string):
        return subprocess.Popen(
            cmd_string,
            shell=True,
            stdout=subprocess.PIPE,
        )

    def _run_command_step(self, command_step, step_num, num_steps, timeout_seconds):
        self.log_step(step_num, num_steps, len(command_step))
        procs = []
        tick_seconds, num_ticks = 1, 0
        log_status_every_seconds = 30
        started_at = datetime.now()
        next_log_status_at = started_at + timedelta(seconds=log_status_every_seconds)
        # launch commands
        for i, command in enumerate(command_step):
            proc_num = i + 1
            cmd_string = command(proc_num)
            proc = Process.create(proc_num, cmd_string, 30)
            procs.append(proc)
        pending_procs = procs

        # poll til completion or timeout
        while True:
            for proc in pending_procs:
                proc.update_status()
                if proc.is_complete():
                    proc.log_result()

            # we're done if everything is completed
            pending_procs = [proc for proc in procs if proc.is_pending()]
            if len(pending_procs) == 0:
                return procs

            # if past timeout, kill timed-out procs and return
            # time_elapsed = tick_seconds * num_ticks
            # if time_elapsed >= timeout_seconds:
            #     timed_out_procs = [ptup for ptup in procs if ptup[2] == -1]
            #     for proc in procs:
            #         proc_num, p, status = proc

            # Log time running if necessary, then sleep til next tick
            now = datetime.now()
            if now > next_log_status_at:
                diff = next_log_status_at - started_at
                logger.info("Running for " + time_duration_pretty(diff.seconds))
                next_log_status_at += timedelta(seconds=log_status_every_seconds)
            time.sleep(tick_seconds)
            num_ticks += 1

    def run(self):
        num_steps = len(self.command_steps)
        for i, command_step in enumerate(self.command_steps):
            self._run_command_step(command_step, i + 1, num_steps, 60)

    @classmethod
    def log_step(cls, step_num, num_steps, num_commands):
        _break = "=" * 80
        logger.info(_break)
        info = "Running step {0} of {1}".format(step_num, num_steps)
        if num_commands == 1:
            info += " (single command)"
        else:
            info += " ({0} commands in parallel)".format(num_commands)
        info = format_with_colors("{0}", info)
        logger.info(info)


class Process(object):
    @classmethod
    def create(cls, number, cmd_string, timeout_seconds):
        """ Run the given command string in a shell as a new process,
        initializing a Process object wrapper for it.
        """
        p = subprocess.Popen(
            cmd_string,
            shell=True,
            stdout=subprocess.PIPE,
        )
        return cls(number, cmd_string, p, datetime.now(), timeout_seconds)

    def __init__(self, number, cmd_string, popen_process,
                 started_at, timeout_seconds):
        self.number = number
        self.cmd_string = cmd_string
        self.popen_process = popen_process
        self.started_at = started_at
        self.timeout_seconds = timeout_seconds
        self.status = None

    def update_status(self):
        self.status = self.popen_process.poll()
        if self.is_pending() and self.is_past_timeout():
            self.status = -1

    def output(self):
        return self.popen_process.stdout.read().decode('utf-8')

    def is_pending(self):
        return self.status is None

    def is_complete(self):
        return not self.is_pending()

    def is_past_timeout(self):
        diff = datetime.now() - self.started_at
        return diff.total_seconds() >= self.timeout_seconds

    def kill_process(self):
        self.popen_process.kill()  # kill -9 the process

    def log_result(self):
        if self.status is None:
            col = "{yellow}"
            exit_phrase = "still running"
        elif self.status == 0:
            col = "{green}"
            exit_phrase = "exited successfully"
        if self.status > 0:
            col = "{red}"
            exit_phrase = "failed with exit code {0}".format(self.status)
        if self.status == -1:
            col = "{red}"
            exit_phrase = "timed out after {0}".format(0)
        logger.info(format_with_colors(
            col + "Command {0} {1}{end}", self.number, exit_phrase))
        logger.info(format_with_colors(col + self.cmd_string + "{end}"))
        logger.info("")
        logger.info("Output:")
        for line in self.output().split('\n'):
            logger.info(line)
