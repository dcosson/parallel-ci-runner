from app.runner import BaseRunner, logger, SerialRunner, subprocess

from mock import patch
from unittest import TestCase


class RunnerTests(TestCase):
    """ Test some of the easily unit-testable methods on BaseRunner and
    other runners. The integration test provides an end-to-end test.
    """

    @patch.object(subprocess, 'Popen')
    def test_run_single(self, mock):
        mock.return_value = 'fakeval'

        r = BaseRunner()
        returnval = r._run_single('foo')

        self.assertEqual(returnval, 'fakeval')
        mock.assert_called_once_with(
            'foo', shell=True, stdout=subprocess.PIPE)

    @patch.object(logger, 'info')
    def test_logs_result(self, mock):
        # using a serial runner, test the log result output
        r = SerialRunner()
        r.add_command(lambda x: "echo foo {0}".format(x))
        r.run()

        self.assertEqual(mock.call_args_list[0][0][0], "")
        self.assertEqual(mock.call_args_list[1][0][0], "=" * 50)
        self.assertEqual(
            mock.call_args_list[2][0][0],
            "Ran command 1 of 1:")
        # Uses process_num 0 for serial commands instead of increasing
        # counter, since they're running in serial
        self.assertEqual(mock.call_args_list[3][0][0], "  echo foo 0")
        self.assertEqual(mock.call_args_list[4][0][0], "")
        self.assertEqual(mock.call_args_list[5][0][0], "foo 0\n")
        self.assertEqual(mock.call_args_list[6][0][0], "")
        self.assertEqual(mock.call_args_list[7][0][0], "=" * 50)
