from unittest import TestCase

from app.utils import split_files_into_groups


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
