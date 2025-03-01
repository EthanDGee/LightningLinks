import unittest
from src.main import find_min_of_indexes, get_top_n_similarities_from_row


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
        with self.assertRaises(IndexError):
            get_top_n_similarities_from_row(row, num_similarities)

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
        num_similarities = 5
        self.assertEqual(get_top_n_similarities_from_row(row, num_similarities), row)

    def test_duplicate_values(self):
        row = [5, 5, 3, 3, 1, 1]
        num_similarities = 4
        result = get_top_n_similarities_from_row(row, num_similarities)
        result = sorted(result)
        expected = [0, 1, 2, 3]  # Indices of the top 4 values
        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()