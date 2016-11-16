from functools import partial
import sys


class SpecCommandInGroups(object):
    def __init__(self, spec_command):
        self.spec_command = spec_command
        self.specs_to_distribute = []
        self.specs_to_run_separately = []

    def load_specs(self, spec_files, run_separately=None):
        if run_separately is None:
            run_separately = []
        _individual_for_own_procs = set([
            f for specs in run_separately for f in specs.split()])

        for sf in spec_files:
            if sf not in _individual_for_own_procs:
                self.specs_to_distribute.append(sf)
        self.specs_to_run_separately.extend(run_separately)

        # if we got no output, treat as failure and return False
        return len(self.specs_to_distribute + self.specs_to_run_separately) > 0

    def _spec_groups(self, num_groups):
        separate_results = [[s] for s in self.specs_to_run_separately]

        num_groups_to_distribute = num_groups - len(self.specs_to_run_separately)
        distributed_results = [[] for _ in range(num_groups_to_distribute)]
        for i, val in enumerate(self.specs_to_distribute):
            distributed_results[i % num_groups_to_distribute].append(val)
        return separate_results + distributed_results

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
