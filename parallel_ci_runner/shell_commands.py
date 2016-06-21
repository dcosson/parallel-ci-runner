from functools import partial
import sys


class SpecCommandInGroups(object):
    def __init__(self, spec_command):
        self.spec_command = spec_command
        self.all_specs = []

    def load_specs(self, specs_output_lines):
        for line in specs_output_lines:
            self.all_specs.append(line)
        # if we got no output, treat as failure and return False
        return len(self.all_specs) > 0

    def _spec_groups(self, num_groups):
        result = [[] for _ in range(num_groups)]
        for i, val in enumerate(self.all_specs):
            result[i % num_groups].append(val)
        return result

    def _build_cmd(self, number, total_number):
        files = ' '.join(self._spec_groups(total_number)[number - 1])
        return "{0} {1}".format(self.spec_command, files)

    def build(self, total_number):
        return partial(self._build_cmd, total_number=total_number)


def is_string(value):
    """ Python 2 & 3 compatible method to determine if a string is string-like
    (either a unicode or byte string).
    """
    if sys.version_info[0] == 2:
        string_types = (str,)
    else:
        string_types = (basestring,)
    return isinstance(value, string_types)


def convert_command_to_function(command):
    if is_string(command):
        def wrapped_command(command_number):
            return command
        return wrapped_command
    else:
        return command


def and_commands(*commands):
    """ Concatenates multiple commands with a shell '&&'
    """
    command_fns = [convert_command_to_function(c) for c in commands]

    def wrapped_and_command(command_number):
        return ' && '.join(command_fn(command_number) for command_fn in command_fns)
    return wrapped_and_command

