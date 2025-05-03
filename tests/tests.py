import unittest
import os
import torch
from src.lightning_links_creator import get_top_n_similarities_from_row, get_all_top_n_similarities
from src.note_handler import FileParser


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
        expected = [0, 1, 2]  # Indices of the top 3 (least negative values)
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

        # get all test file lines so that they can be safely rewritten to their original state after the tests
        # that modify the files are run.

        self.original_file_lines = {
            'contains YAML.md': [],
            'example note.md': [],
            'invalid ending.md': [],
            'valid ending no lightning links.md': [],
            'multiple sections note.md': [],
            'no headers.md': [],
            'single link.md': [],
            'no tags with header.md': [],
            '.obsidian/similar_notes.json': []
        }

        # loop through all files in the test vault and save their lines to the dictionary
        for file_name in self.original_file_lines.keys():
            with open(f'{self.test_vault}{file_name}', 'r') as file:
                self.original_file_lines[file_name] = file.readlines()

        # create a placeholder that will be used to store the current state of the files after each test
        self.current_file_lines = {
            'contains YAML.md': [],
            'example note.md': [],
            'invalid ending.md': [],
            'valid ending no lightning links.md': [],
            'multiple sections note.md': [],
            'no headers.md': [],
            'single link.md': [],
            'no tags with header.md': [],
            '.obsidian/similar_notes.json': []
        }

        self.reload_files()

        # expected file contents for example note
        self.example_body = (
            "\nThe [[science]] of computers from how they work, how to use them, and the process of evaluating new better "
            "ways to devise solutions to problems with there assistance.\n"
        )
        self.example_tags = "#computer-science #discrete-mathematics\n"
        self.example_single_tag = "#computer-science\n"
        self.example_links = "[[science]]\n[[electronics]]\n"
        self.example_header = "## BEEP BEEP BOOP BOOP\n"
        self.example_smart_links = (
            "[[Computer science isn't about computers.md]]     "
            "[[accessibility in computer science.md]]     "
            "[[Dijkstra.md]]     "
            "[[hardware.md]]     "
            "[[computer storage.md]]"
        )
        self.empty_yaml = ""

        self.example_yaml = "---\nAlias:\n  - CS\n---\n"

        # Create a dictionary mapping file names to their expected values
        # This reduces redundancy by centralizing the expected values
        self.expected_values = {
            'example note.md': {
                'links': self.example_links,
                'tags': self.example_tags,
                'body': self.example_body,
                'smart_links': self.example_smart_links,
                'yaml': ""
            },
            'contains YAML.md': {
                'links': self.example_links,
                'tags': self.example_tags,
                'body': self.example_body,
                'smart_links': self.example_smart_links,
                'yaml': self.example_yaml
            },
            'invalid ending.md': {
                'links': self.example_links,
                'tags': self.example_tags,
                'body': self.example_body[:-1],
                'smart_links': "",
                'yaml': self.empty_yaml
            },
            'no headers.md': {
                'links': "",
                'tags': self.example_tags,
                'body': self.example_body,
                'smart_links': self.example_smart_links,
                'yaml': self.empty_yaml
            },
            'no tags with header.md': {
                'links': self.example_links,
                'tags': "",
                'body': f"{self.example_header}{self.example_body}",
                'smart_links': self.example_smart_links,
                'yaml': self.empty_yaml
            },
            'valid ending no lightning links.md': {
                'links': self.example_links,
                'tags': self.example_single_tag,
                'body': self.example_body,
                'smart_links': "",
                'yaml': self.empty_yaml
            }
        }

    def reset_file(self, file_name):
        # a simple method that reset a single fle specified by file_name using original file_lines

        with open(f'{self.test_vault}{file_name}', 'w') as file:
            file.writelines(self.original_file_lines[file_name])

    def reset_files(self):
        # A method to reset the files to their original state using the stored data from setUp.

        for file_name in self.original_file_lines.keys():
            self.reset_file(file_name)

    def reload_files(self):
        # a method to reload the files from the current notes directory to test modifications made to the files.

        for file_name in self.current_file_lines.keys():
            with open(f'{self.test_vault}{file_name}', 'r') as file:
                self.current_file_lines[file_name] = file.readlines()

    def delete_file(self, file_name):
        # deletes a file.
        if file_name not in self.file_parser.file_names:
            os.remove(f'{self.test_vault}{file_name}')


    def compare_files(self, expected, actual):
        # compares a file to the expected original file.
        expected_lines = self.original_file_lines[expected]

        with open(actual, 'r') as file:
            current_line = file.readline()
            line_index = 0
            while current_line:
                # check match
                self.assertEqual(expected_lines[line_index], current_line)

                # move to the next line
                current_line = file.readline()
                line_index += 1

    def test_get_note_names(self):
        # file names are calculated during the __init__ process, so we are just checking validity

        # ensure that the non-valid notes are not part of the project
        self.assertNotIn('invalid.png', self.file_parser.note_names)
        self.assertNotIn('exampleDrawing.excalidraw.md', self.file_parser.note_names)
        # .md would be removed if it is considered valid
        self.assertNotIn('exampleDrawing.excalidraw', self.file_parser.note_names)

        # check for the valid notes
        self.assertIn('contains YAML', self.file_parser.note_names)
        self.assertIn('example note', self.file_parser.note_names)
        self.assertIn('invalid ending', self.file_parser.note_names)
        self.assertIn('valid ending no lightning links', self.file_parser.note_names)

        # check that the valid notes do not have the file extension
        self.assertNotIn('contains YAML.md', self.file_parser.note_names)
        self.assertNotIn('example note.md', self.file_parser.note_names)
        self.assertNotIn('invalid ending.md', self.file_parser.note_names)
        self.assertNotIn('valid ending no lightning links.md', self.file_parser.note_names)

    def test_get_file_names(self):
        # file names are calculated during the __init__ process, so we are just checking validity

        # ensure that the non-valid notes are not part of the project
        self.assertNotIn(f'{self.test_vault}invalid.png', self.file_parser.file_names)
        self.assertNotIn(f'{self.test_vault}exampleDrawing.excalidraw.md', self.file_parser.file_names)
        # .md would be removed if it is considered valid
        self.assertNotIn(f'{self.test_vault}exampleDrawing.excalidraw', self.file_parser.file_names)

        # check that the valid notes paths with the proper file extension
        self.assertIn(f'{self.test_vault}contains YAML.md', self.file_parser.file_names)
        self.assertIn(f'{self.test_vault}example note.md', self.file_parser.file_names)
        self.assertIn(f'{self.test_vault}invalid ending.md', self.file_parser.file_names)
        self.assertIn(f'{self.test_vault}valid ending no lightning links.md', self.file_parser.file_names)

        # check that notes do not remove the file extension
        self.assertNotIn(f'{self.test_vault}contains YAML', self.file_parser.file_names)
        self.assertNotIn(f'{self.test_vault}example note', self.file_parser.file_names)
        self.assertNotIn(f'{self.test_vault}invalid ending', self.file_parser.file_names)
        self.assertNotIn(f'{self.test_vault}valid ending no lightning links', self.file_parser.file_names)

    def test_ensure_proper_endings(self):
        # A test that ensures that the ensure proper endings method works as intended. This is done by checking
        # that the proper ending newline is only added to the file if it is missing. It also makes sure that
        # the files are not modified if they have a correct ending.

        # call function and reload the contents of files
        self.file_parser.ensure_proper_endings()
        self.reload_files()
        # reset files to the original state after the file changes have been loaded
        self.reset_files()

        # check to see if any of the valid files have been unnecessarily edited

        valid_files = list(self.original_file_lines.keys())
        valid_files.remove('.obsidian/similar_notes.json')
        valid_files.remove('invalid ending.md')

        for file_name in valid_files:
            self.assertEqual(self.original_file_lines[file_name], self.current_file_lines[file_name])

        # check to see if the invalid ending file was modified
        self.assertNotEqual(self.original_file_lines['invalid ending.md'], self.current_file_lines['invalid ending.md'])

        # check to see if only the ending newline was added to the invalid ending file
        self.assertEqual(
            self.original_file_lines['invalid ending.md'][-1] + '\n',
            self.current_file_lines['invalid ending.md'][-1]
        )

    def _test_parse_note(self, file_name):
        """
        Helper method to test parse_note for a given file with expected values.

        If individual expected values are not provided, it will use the values from self.expected_values.
        """
        self.reset_file(file_name)
        contents = self.file_parser.parse_note(f'{self.test_vault}{file_name}')

        # If individual expected values are provided, use them
        # Otherwise, use the values from self.expected_values
        self.assertIn(file_name, self.expected_values.keys())

        expected = self.expected_values[file_name]
        expected_links = expected['links']
        expected_tags = expected['tags']
        expected_body = expected['body']
        expected_smart_links = expected['smart_links']
        expected_yaml = expected['yaml']

        self.assertEqual(expected_links, contents["links"])
        self.assertEqual(expected_tags, contents["tags"])
        self.assertEqual(expected_body, contents["body"])
        self.assertEqual(expected_smart_links, contents["smart_links"])
        self.assertEqual(expected_yaml, contents["YAML"])

    def test_parse_all_notes(self):
        """Test parse_note for all note files except 'multiple sections note.md' and 'single link.md'."""
        # Exclude 'multiple sections note.md' and 'single link.md' as per requirements
        excluded_files = ['multiple sections note.md', 'single link.md']

        for file_name in self.expected_values.keys():
            if file_name not in excluded_files:
                with self.subTest(file_name=file_name):
                    self._test_parse_note(file_name)

    def test_valid_parse_note(self):
        # tests parse for the valid note
        self._test_parse_note(
            'example note.md'
        )

    def test_parse_note_contains_yaml(self):
        # tests parse for the note with YAML frontmatter
        self._test_parse_note(
            'contains YAML.md'
        )

    def test_parse_note_invalid_ending(self):
        # tests parse for the note with an invalid ending
        self._test_parse_note(
            'invalid ending.md'
        )

    def test_parse_note_no_headers(self):
        # tests parse for the note with no headers
        self._test_parse_note(
            'no headers.md'
        )

    def test_parse_note_no_tags_with_header(self):
        # tests parse for the note with no tags but with a header
        self._test_parse_note(
            'no tags with header.md'
        )

    def test_parse_note_valid_ending_no_lightning_links(self):
        # tests parse for the note with a valid ending but no lightning links
        self._test_parse_note(
            'valid ending no lightning links.md'
        )




if __name__ == '__main__':
    unittest.main()
