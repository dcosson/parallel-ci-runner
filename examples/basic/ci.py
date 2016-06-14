#!/usr/bin/env python

from datetime import timedelta
from parallel_ci_runner import CIRunner


def foo_cmd(i):
    return r"sleep 2 && echo ran command with {0}".format(i)


def foo_timeout_cmd(i):
    return r"sleep 10 && echo ran command with {0}".format(i)


runner = CIRunner()
runner.add_serial_command_step(foo_cmd)
runner.add_parallel_command_step([foo_cmd, 'echo command can be a string', foo_timeout_cmd], timeout=timedelta(seconds=3))
runner.run()
