import unittest
from src.lightning_links_creator import find_min_of_indexes, get_top_n_similarities_from_row, get_all_top_n_similarities
from src.note_handler import FileParser
import torch


class TestFindMinFromIndexes(unittest.TestCase):
    def test_single_element(self):
        # Single element in indexes
        self.assertEqual(find_min_of_indexes([2], [4, 5, 1, 7]), 2)
        self.assertEqual(find_min_of_indexes([0], [8, 6, 2, 1]), 0)
        self.assertEqual(find_min_of_indexes([3], [1, 3, 5, 0]), 3)

    def test_multiple_elements(self):
        # Multiple elements in indexes
        self.assertEqual(find_min_of_indexes([1, 3, 4], [8, 3, 6, 2, 5]), 3)
        self.assertEqual(find_min_of_indexes([0, 2, 3], [4, 7, 2, 1]), 3)
        self.assertEqual(find_min_of_indexes([2, 5, 6], [9, 12, 7, 15, 10, 3, 2]), 6)

    def test_min_at_start(self):
        # Minimum at the start of indexes
        self.assertEqual(find_min_of_indexes([0, 2, 4], [1, 7, 3, 9, 10]), 0)
        self.assertEqual(find_min_of_indexes([1, 2, 3], [3, 5, 9, 12]), 1)
        self.assertEqual(find_min_of_indexes([0, 3, 4], [2, 7, 9, 3, 8]), 0)

    def test_min_at_end(self):
        # Minimum at the end of indexes
        self.assertEqual(find_min_of_indexes([1, 3, 5, 6], [9, 12, 8, 15, 10, 6, 3]), 6)
        self.assertEqual(find_min_of_indexes([0, 4, 5, 8], [8, 12, 15, 18, 3, 5, 6, 7, 1]), 8)
        self.assertEqual(find_min_of_indexes([2, 3, 7], [9, 8, 5, 10, 11, 15, 18, 3]), 7)


class TestGetTopNSimilaritiesFromRow(unittest.TestCase):
    def test_basic_case(self):
        row = [1.0, 2.0, 3.0, 4.0, 5.0]
        num_similarities = 3
        result = get_top_n_similarities_from_row(row, num_similarities)
        result = sorted(result, reverse=True)
        expected = [4, 3, 2]  # Indices of highest values in descending order
        self.assertEqual(expected, result)

    def test_smaller_num_similarities_than_row_length(self):
        row = [1.5, 2.5, 0.0, 3.5, 4.5]
        num_similarities = 2
        result = get_top_n_similarities_from_row(row, num_similarities)
        result = sorted(result, reverse=True)
        expected = [4, 3]  # Indices of top 2 values
        self.assertEqual(expected, result)

    def test_equal_num_similarities_to_row_length(self):
        row = [5.0, 4.0, 3.0, 2.0, 1.0]
        num_similarities = 5
        result = get_top_n_similarities_from_row(row, num_similarities)
        result = sorted(result)
        expected = [0, 1, 2, 3, 4]  # All indices as the entire row is included
        self.assertEqual(expected, result)

    def test_empty_row(self):
        row = []
        num_similarities = 3
        result = get_top_n_similarities_from_row(row, num_similarities)
        expected = []
        self.assertEqual(expected, result)

    def test_with_negative_values(self):
        row = [-1, -2, -3, -4, -5]
        num_similarities = 3
        result = get_top_n_similarities_from_row(row, num_similarities)
        result = sorted(result)
        expected = [0, 1, 2]  # Indices of top 3 (least negative values)
        self.assertEqual(expected, result)

    def test_zero_similarities(self):
        row = [1, 2, 3, 4, 5]
        num_similarities = 0
        result = get_top_n_similarities_from_row(row, num_similarities)
        expected = []  # No indices should be returned
        self.assertEqual(expected, result)

    def test_larger_num_similarities_than_row_length(self):
        row = [1, 2, 3]
        expected = [0, 1, 2]
        num_similarities = 5
        result = get_top_n_similarities_from_row(row, num_similarities)
        self.assertEqual(expected, result)

    def test_duplicate_values(self):
        row = [5, 5, 3, 3, 1, 1]
        num_similarities = 4
        result = get_top_n_similarities_from_row(row, num_similarities)
        result = sorted(result)
        expected = [0, 1, 2, 3]  # Indices of the top 4 values
        self.assertEqual(expected, result)


class TestGetAllTopNSimilarities(unittest.TestCase):

    def test_get_all_top_n_similarities_basic(self):
        similarities = torch.tensor([
            [0.1, 0.5, 0.3],
            [0.8, 0.2, 0.4],
            [0.6, 0.9, 0.7]
        ])
        n = 2
        expected = [
            [1, 2],
            [0, 2],
            [1, 2]
        ]
        result = get_all_top_n_similarities(similarities, n)
        for row in result:
            row.sort()

        self.assertEqual(expected, result, )

    def test_get_all_top_n_similarities_single_row(self):
        similarities = torch.tensor([
            [0.9, 0.4, 0.6]
        ])
        n = 2
        expected = [
            [0, 2]
        ]
        result = get_all_top_n_similarities(similarities, n)
        self.assertEqual(result, expected)

    def test_get_all_top_n_similarities_n_greater_than_length(self):
        similarities = torch.tensor([
            [0.5, 0.8, 0.3],
            [0.4, 0.2, 0.1]
        ])
        n = 5
        expected = [
            [0, 1, 2],
            [0, 1, 2]
        ]
        result = get_all_top_n_similarities(similarities, n)
        for row in result:
            row.sort()
        self.assertEqual(expected, result)

    def test_get_all_top_n_similarities_n_equals_zero(self):
        similarities = torch.tensor([
            [0.1, 0.5, 0.3],
            [0.8, 0.2, 0.4]
        ])
        n = 0
        expected = [
            [],
            []
        ]
        result = get_all_top_n_similarities(similarities, n)
        for row in result:
            row.sort()

        self.assertEqual(expected, result)


class TestFileParser(unittest.TestCase):
    def setUp(self):

        # initialize the file parser
        self.test_vault = 'testNoteDirectory/'
        self.file_parser = FileParser(self.test_vault)

    def test_get_note_names(self):

        # file names are calculated during the __init__ process so we are just checking validity

        # ensure that the non-valid notes are not part of the project
        self.assertNotIn('invalid.png', self.file_parser.note_names)
        self.assertNotIn('exampleDrawing.excalidraw.md', self.file_parser.note_names)
        # .md would be removed if it is considered valid
        self.assertNotIn('exampleDrawing.excalidraw', self.file_parser.note_names)

        # check for the valid notes
        self.assertIn('contains alias', self.file_parser.note_names)
        self.assertIn('example note', self.file_parser.note_names)
        self.assertIn('invalid ending', self.file_parser.note_names)

        # check that the valid notes do not have the file extension
        self.assertNotIn('contains alias.md', self.file_parser.note_names)
        self.assertNotIn('example note.md', self.file_parser.note_names)
        self.assertNotIn('invalid ending.md', self.file_parser.note_names)



if __name__ == '__main__':
    unittest.main()
