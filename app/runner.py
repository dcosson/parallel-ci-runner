import subprocess


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

    def print_result(self, cmd_string, proc, i):
        output = proc.stdout.read().decode('utf-8')
        print("")
        print("==================================================")
        print("Ran command {0} of {1}:".format(i, len(self.commands)))
        print("  {0}".format(cmd_string))
        print("")
        print(output)
        print("")
        print("==================================================")
        print("")


class SerialRunner(BaseRunner):

    def run(self):
        for i, command in enumerate(self.commands):
            cmd_string = command(0)
            p = self._run_single(cmd_string)
            p.wait()
            self.print_result(cmd_string, p, i)


class ParallelRunner(BaseRunner):

    def run(self):
        procs = []
        for i, command in enumerate(self.commands):
            cmd_string = command(0)
            p = self._run_single(cmd_string)
            procs.append(p)
        for i, p in enumerate(procs):
            p.wait()
            self.print_result(cmd_string, p, i)
