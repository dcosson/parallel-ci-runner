from parallel_ci_runner.runner import CIRunner, logger, subprocess

from mock import patch
from unittest import TestCase


class RunnerTests(TestCase):
    """ Test some of the easily unit-testable methods on CIRunner and
    other runners. The integration test provides an end-to-end test.
    """
    def test_add_command_steps(self):
        r = CIRunner()
        r.add_serial_command_step('foo')
        r.add_parallel_command_step('bar')
        r.add_parallel_command_step('one', 'two', 'three')
        self.assertEqual(r.command_steps, [['foo'], ['bar'], ['one', 'two', 'three']])
