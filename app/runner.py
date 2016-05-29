import subprocess

from .logger import logger


class BaseRunner(object):

    def __init__(self):
        self.commands = []

    def add_command(self, command):
        """ Add a command to run.
            A command is a function that takes in process number and returns a
            string to be executed as a subcommand in a shell.
        """
        self.commands.append(command)

    def _run_single(self, cmd_string):
        return subprocess.Popen(
            cmd_string,
            shell=True,
            stdout=subprocess.PIPE,
        )

    def log_result(self, proc, i):
        cmd_string = proc.args
        output = proc.stdout.read().decode('utf-8')
        logger.info("")
        logger.info("=" * 50)
        logger.info("Ran command {0} of {1}:".format(i, len(self.commands)))
        logger.info("  {0}".format(cmd_string))
        logger.info("")
        logger.info(output)
        logger.info("")
        logger.info("=" * 50)
        logger.info("")

    def add_serial_command(self, command):
        pass


class SerialRunner(BaseRunner):

    def run(self):
        # use 1-offset indexes
        for i0, command in enumerate(self.commands):
            i = i0 + 1
            cmd_string = command(0)
            p = self._run_single(cmd_string)
            p.wait()
            self.log_result(p, i)


class ParallelRunner(BaseRunner):

    def run(self):
        procs = []
        for i0, command in enumerate(self.commands):
            i = i0 + 1
            cmd_string = command(0)
            p = self._run_single(cmd_string)
            procs.append(p)
        for i0, p in enumerate(procs):
            i = i0 + 1
            p.wait()
            self.log_result(p, i)
