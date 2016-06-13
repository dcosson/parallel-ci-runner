from unittest import TestCase

from app.utils import (
    split_files_into_groups,
    time_duration_pretty,
)


class UtilsTests(TestCase):

    def test_split_files_into_groups(self):
        result = split_files_into_groups(3, 'tests/unit/file_test_helpers/**/file*.txt', False)
        self.assertEqual(len(result), 3)
        self.assertEqual(
            result[0],
            ['tests/unit/file_test_helpers/file1.txt',
             'tests/unit/file_test_helpers/nested_dir/file10.txt'])
        self.assertEqual(
            result[1], ['tests/unit/file_test_helpers/file2.txt'])
        self.assertEqual(
            result[2], ['tests/unit/file_test_helpers/file3.txt'])

    def test_time_duration_pretty(self):
        self.assertEqual(
            time_duration_pretty(0), "0 seconds")
        self.assertEqual(
            time_duration_pretty(1), "1 second")
        self.assertEqual(
            time_duration_pretty(2), "2 seconds")
        self.assertEqual(
            time_duration_pretty(60), "1 minute, 0 seconds")
        self.assertEqual(
            time_duration_pretty(90), "1 minute, 30 seconds")
        self.assertEqual(
            time_duration_pretty(60 * 60),
            "1 hour, 0 minutes, 0 seconds")
        self.assertEqual(
            time_duration_pretty(3 * 3600 + 121),
            "3 hours, 2 minutes, 1 second")
        self.assertEqual(
            time_duration_pretty(24 * 60 * 60),
            "1 day, 0 hours, 0 minutes, 0 seconds")
        self.assertEqual(
            time_duration_pretty(4 * 24 * 60 * 60 + 3 * 3600 + 121),
            "4 days, 3 hours, 2 minutes, 1 second")
        self.assertEqual(
            time_duration_pretty(100 * 24 * 60 * 60),
            "100 days, 0 hours, 0 minutes, 0 seconds")
