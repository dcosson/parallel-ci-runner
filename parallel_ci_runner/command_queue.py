class CommandQueue(object):
    """ An ordered queue of commands, to run in a parallel build step.
        For example, you could start up 4 worker processes via docker-compose
        up -d, then create a queue of 20 test files to run and have them run
        via `docker exec` one at a time on whichever worker is available first.
    """

    def __init__(self):
        self.commands = []

    def add_command(self, command):
        self.commands.append(command)

    def next_command(self):
        return self.commands.pop(0)

    def is_empty(self):
        return len(self.commands) == 0
