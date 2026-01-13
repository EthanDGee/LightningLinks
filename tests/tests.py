import os
import unittest

from src.note_handler import FileParser


class TestFileParser(unittest.TestCase):
    def setUp(self):
        # initialize the file parser
        self.test_vault = "testNoteDirectory/"
        self.file_parser = FileParser(self.test_vault)

        # get all test file lines so that they can be safely rewritten to their original state after the tests
        # that modify the files are run.

        self.original_file_lines = {
            "contains YAML.md": [],
            "example note.md": [],
            "invalid ending.md": [],
            "valid ending no lightning links.md": [],
            "multiple sections note.md": [],
            "no headers.md": [],
            "single link.md": [],
            "no tags with header.md": [],
            ".obsidian/similar_notes.json": [],
        }

        # loop through all files in the test vault and save their lines to the dictionary
        for file_name in self.original_file_lines.keys():
            with open(f"{self.test_vault}{file_name}", "r") as file:
                self.original_file_lines[file_name] = file.readlines()

        # create a placeholder that will be used to store the current state of the files after each test
        self.current_file_lines = {
            "contains YAML.md": [],
            "example note.md": [],
            "invalid ending.md": [],
            "valid ending no lightning links.md": [],
            "multiple sections note.md": [],
            "no headers.md": [],
            "single link.md": [],
            "no tags with header.md": [],
            ".obsidian/similar_notes.json": [],
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
            "[[Computer science isn't about computers]]     "
            "[[accessibility in computer science]]     "
            "[[Dijkstra]]     "
            "[[hardware]]     "
            "[[computer storage]]"
        )
        self.example_connections = [
            "Computer science isn't about computers.md",
            "accessibility in computer science.md",
            "Dijkstra.md",
            "hardware.md",
            "computer storage.md",
        ]
        self.empty_yaml = ""

        self.example_yaml = "---\nAlias:\n  - CS\n---\n"

        # Create a dictionary mapping file names to their expected values
        # This reduces redundancy by centralizing the expected values
        self.expected_values = {
            "example note.md": {
                "links": self.example_links,
                "tags": self.example_tags,
                "body": self.example_body,
                "smart_links": self.example_smart_links,
                "yaml": "",
            },
            "contains YAML.md": {
                "links": self.example_links,
                "tags": self.example_tags,
                "body": self.example_body,
                "smart_links": self.example_smart_links,
                "yaml": self.example_yaml,
            },
            "invalid ending.md": {
                "links": self.example_links,
                "tags": self.example_tags,
                "body": self.example_body[:-1],
                "smart_links": "",
                "yaml": self.empty_yaml,
            },
            "no headers.md": {
                "links": "",
                "tags": self.example_tags,
                "body": self.example_body,
                "smart_links": self.example_smart_links,
                "yaml": self.empty_yaml,
            },
            "no tags with header.md": {
                "links": self.example_links,
                "tags": "",
                "body": f"{self.example_header}{self.example_body}",
                "smart_links": self.example_smart_links,
                "yaml": self.empty_yaml,
            },
            "valid ending no lightning links.md": {
                "links": self.example_links,
                "tags": self.example_single_tag,
                "body": self.example_body,
                "smart_links": "",
                "yaml": self.empty_yaml,
            },
        }

    def reset_file(self, file_name):
        # a simple method that reset a single fle specified by file_name using original file_lines

        with open(f"{self.test_vault}{file_name}", "w") as file:
            file.writelines(self.original_file_lines[file_name])

    def reset_files(self):
        # A method to reset the files to their original state using the stored data from setUp.

        for file_name in self.original_file_lines.keys():
            self.reset_file(file_name)

    def reload_files(self):
        # a method to reload the files from the current notes directory to test modifications made to the files.

        for file_name in self.current_file_lines.keys():
            with open(f"{self.test_vault}{file_name}", "r") as file:
                self.current_file_lines[file_name] = file.readlines()

    def delete_file(self, file_name):
        # deletes a file.
        if file_name not in self.file_parser.file_names:
            os.remove(f"{self.test_vault}{file_name}")

    def compare_files(self, expected, actual):
        # compares a file to the expected original file.
        expected_lines = self.original_file_lines[expected]

        with open(actual, "r") as file:
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
        self.assertNotIn("invalid.png", self.file_parser.note_names)
        self.assertNotIn("exampleDrawing.excalidraw.md", self.file_parser.note_names)
        # .md would be removed if it is considered valid
        self.assertNotIn("exampleDrawing.excalidraw", self.file_parser.note_names)

        # check for the valid notes
        self.assertIn("contains YAML", self.file_parser.note_names)
        self.assertIn("example note", self.file_parser.note_names)
        self.assertIn("invalid ending", self.file_parser.note_names)
        self.assertIn("valid ending no lightning links", self.file_parser.note_names)

        # check that the valid notes do not have the file extension
        self.assertNotIn("contains YAML.md", self.file_parser.note_names)
        self.assertNotIn("example note.md", self.file_parser.note_names)
        self.assertNotIn("invalid ending.md", self.file_parser.note_names)
        self.assertNotIn(
            "valid ending no lightning links.md", self.file_parser.note_names
        )

    def test_get_file_names(self):
        # file names are calculated during the __init__ process, so we are just checking validity

        # ensure that the non-valid notes are not part of the project
        self.assertNotIn(f"{self.test_vault}invalid.png", self.file_parser.file_names)
        self.assertNotIn(
            f"{self.test_vault}exampleDrawing.excalidraw.md",
            self.file_parser.file_names,
        )
        # .md would be removed if it is considered valid
        self.assertNotIn(
            f"{self.test_vault}exampleDrawing.excalidraw", self.file_parser.file_names
        )

        # check that the valid notes paths with the proper file extension
        self.assertIn(f"{self.test_vault}contains YAML.md", self.file_parser.file_names)
        self.assertIn(f"{self.test_vault}example note.md", self.file_parser.file_names)
        self.assertIn(
            f"{self.test_vault}invalid ending.md", self.file_parser.file_names
        )
        self.assertIn(
            f"{self.test_vault}valid ending no lightning links.md",
            self.file_parser.file_names,
        )

        # check that notes do not remove the file extension
        self.assertNotIn(f"{self.test_vault}contains YAML", self.file_parser.file_names)
        self.assertNotIn(f"{self.test_vault}example note", self.file_parser.file_names)
        self.assertNotIn(
            f"{self.test_vault}invalid ending", self.file_parser.file_names
        )
        self.assertNotIn(
            f"{self.test_vault}valid ending no lightning links",
            self.file_parser.file_names,
        )

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
        valid_files.remove(".obsidian/similar_notes.json")
        valid_files.remove("invalid ending.md")

        for file_name in valid_files:
            self.assertEqual(
                self.original_file_lines[file_name], self.current_file_lines[file_name]
            )

        # check to see if the invalid ending file was modified
        self.assertNotEqual(
            self.original_file_lines["invalid ending.md"],
            self.current_file_lines["invalid ending.md"],
        )

        # check to see if only the ending newline was added to the invalid ending file
        self.assertEqual(
            self.original_file_lines["invalid ending.md"][-1] + "\n",
            self.current_file_lines["invalid ending.md"][-1],
        )

    def _test_parse_note(self, file_name):
        """
        Helper method to test parse_note for a given file with expected values.

        If individual expected values are not provided, it will use the values from self.expected_values.
        """
        self.reset_file(file_name)
        contents = self.file_parser.parse_note(f"{self.test_vault}{file_name}")

        # If individual expected values are provided, use them
        # Otherwise, use the values from self.expected_values
        self.assertIn(file_name, self.expected_values.keys())

        expected = self.expected_values[file_name]
        expected_links = expected["links"]
        expected_tags = expected["tags"]
        expected_body = expected["body"]
        expected_smart_links = expected["smart_links"]
        expected_yaml = expected["yaml"]

        self.assertEqual(expected_links, contents["links"])
        self.assertEqual(expected_tags, contents["tags"])
        self.assertEqual(expected_body, contents["body"])
        self.assertEqual(expected_smart_links, contents["smart_links"])
        self.assertEqual(expected_yaml, contents["YAML"])

    def test_parse_all_notes(self):
        """Test parse_note for all note files except 'multiple sections note.md' and 'single link.md'."""
        # Exclude 'multiple sections note.md' and 'single link.md' as per requirements
        excluded_files = ["multiple sections note.md", "single link.md"]

        for file_name in self.expected_values.keys():
            if file_name not in excluded_files:
                with self.subTest(file_name=file_name):
                    self._test_parse_note(file_name)

    def test_valid_parse_note(self):
        # tests parse for the valid note
        self._test_parse_note("example note.md")

    def test_parse_note_contains_yaml(self):
        # tests parse for the note with YAML frontmatter
        self._test_parse_note("contains YAML.md")

    def test_parse_note_invalid_ending(self):
        # tests parse for the note with an invalid ending
        self._test_parse_note("invalid ending.md")

    def test_parse_note_no_headers(self):
        # tests parse for the note with no headers
        self._test_parse_note("no headers.md")

    def test_parse_note_no_tags_with_header(self):
        # tests parse for the note with no tags but with a header
        self._test_parse_note("no tags with header.md")

    def test_parse_note_valid_ending_no_lightning_links(self):
        # tests parse for the note with a valid ending but no lightning links
        self._test_parse_note("valid ending no lightning links.md")

    def test_format_inline_lightning_links(self):
        similar_notes = [
            "science.md",
            "electronics.md",
            "money.md",
            "mathematics.md",
            "horses.md",
            "pumpkins.md",
        ]

        one_link = "[[science]]"
        two_links = "[[science]]     [[electronics]]"
        three_links = "[[science]]     [[electronics]]     [[money]]"
        four_links = "[[science]]     [[electronics]]     [[money]]     [[mathematics]]"
        five_links = "[[science]]     [[electronics]]     [[money]]     [[mathematics]]     [[horses]]"
        six_links = "[[science]]     [[electronics]]     [[money]]     [[mathematics]]     [[horses]]     [[pumpkins]]"

        self.assertEqual(
            one_link, self.file_parser.format_inline_lighting_links(similar_notes, 1)
        )
        self.assertEqual(
            two_links, self.file_parser.format_inline_lighting_links(similar_notes, 2)
        )
        self.assertEqual(
            three_links, self.file_parser.format_inline_lighting_links(similar_notes, 3)
        )
        self.assertEqual(
            four_links, self.file_parser.format_inline_lighting_links(similar_notes, 4)
        )
        self.assertEqual(
            five_links, self.file_parser.format_inline_lighting_links(similar_notes, 5)
        )
        self.assertEqual(
            six_links, self.file_parser.format_inline_lighting_links(similar_notes, 6)
        )

    def test_parse_inline_lightning_links(self):
        expected = [
            "science.md",
            "electronics.md",
            "money.md",
            "mathematics.md",
            "big horses.md",
            "pumpkins.md",
        ]

        two_links = "[[science]]     [[electronics]]"
        self.assertEqual(
            expected[:2], self.file_parser.parse_inline_lightning_links(two_links)
        )

        three_links = "[[science]]     [[electronics]]     [[money]]"
        self.assertEqual(
            expected[:3], self.file_parser.parse_inline_lightning_links(three_links)
        )

        four_links = "[[science]]     [[electronics]]     [[money]]     [[mathematics]]"
        self.assertEqual(
            expected[:4], self.file_parser.parse_inline_lightning_links(four_links)
        )

        five_links = "[[science]]     [[electronics]]     [[money]]     [[mathematics]]     [[big horses]]"
        self.assertEqual(
            expected[:5], self.file_parser.parse_inline_lightning_links(five_links)
        )

        six_links = "[[science]]     [[electronics]]     [[money]]     [[mathematics]]     [[big horses]]     [[pumpkins]]"
        self.assertEqual(
            expected, self.file_parser.parse_inline_lightning_links(six_links)
        )

    def test_write_to_file_example_note(self):
        file_contents = {
            "file_name": f"{self.test_vault}temp example note.md",
            "YAML": self.empty_yaml,
            "links": self.example_links,
            "tags": self.example_tags,
            "body": self.example_body,
            "similar_notes": self.example_connections,
        }

        self.file_parser.write_to_file(file_contents, 5)

        self.compare_files("example note.md", f"{self.test_vault}temp example note.md")
        self.delete_file(f"{self.test_vault}temp example note.md")

    def test_write_to_file_contains_yaml(self):
        file_contents = {
            "file_name": f"{self.test_vault}temp contains YAML.md",
            "YAML": self.example_yaml,
            "links": self.example_links,
            "tags": self.example_tags,
            "body": self.example_body,
            "similar_notes": self.example_connections,
        }

        self.file_parser.write_to_file(file_contents, 5)

        self.compare_files(
            "contains YAML.md", f"{self.test_vault}temp contains YAML.md"
        )
        self.delete_file(f"{self.test_vault}temp contains YAML.md")

    def test_update_lighting_links_on_empty_file(self):
        # create an empty temp file
        temp_path = f"{self.test_vault}temp_empty.md"
        with open(temp_path, "w") as f:
            pass

        similar = ["science.md", "electronics.md", "money.md"]
        # should return True (file updated)
        updated = self.file_parser.update_lighting_links(temp_path, similar, 3)
        self.assertTrue(updated)

        # verify the file now contains header and formatted links
        with open(temp_path, "r") as f:
            contents = f.read()

        expected_links = self.file_parser.format_inline_lighting_links(similar, 3)
        self.assertIn("### Lightning Links", contents)
        self.assertIn(expected_links, contents)

        # cleanup
        if temp_path in self.file_parser.file_names:
            # write_to_file may register files; ensure deletion uses full path
            os.remove(temp_path)
        else:
            os.remove(temp_path)

    def test_update_lighting_links_no_change(self):
        # Create a file with an existing lightning links section matching the formatted links
        temp_path = f"{self.test_vault}temp_no_change.md"
        similar = ["science.md", "electronics.md"]
        formatted = self.file_parser.format_inline_lighting_links(similar, 2)
        with open(temp_path, "w") as f:
            f.write("Some body text\n")
            f.write("### Lightning Links\n")
            f.write(formatted + "\n")

        # calling update should detect no change and return False
        updated = self.file_parser.update_lighting_links(temp_path, similar, 2)
        self.assertFalse(updated)

        # cleanup
        os.remove(temp_path)

    def test_save_and_load_similar_notes(self):
        # write a mapping and verify load_similar_notes reads it back
        notes = [
            {"file_name": f"{self.test_vault}a.md", "similar_notes": ["b.md"]},
            {"file_name": f"{self.test_vault}b.md", "similar_notes": ["a.md"]},
        ]
        # save using FileParser method
        self.file_parser.save_similar_notes(notes)

        # ensure file exists and load_similar_notes returns mapping containing our entries
        loaded = self.file_parser.load_similar_notes()
        # keys in saved file are the full paths as used in save_similar_notes
        expected_key = f"{self.test_vault}a.md"
        self.assertIn(expected_key, loaded)

    def test_write_to_file_registers_filename(self):
        temp_path = f"{self.test_vault}temp_register.md"
        file_contents = {
            "file_name": temp_path,
            "YAML": self.empty_yaml,
            "links": "",
            "tags": "",
            "body": "Body text\n",
            "similar_notes": [],
        }
        # ensure not present initially
        if temp_path in self.file_parser.file_names:
            self.file_parser.file_names.remove(temp_path)

        self.file_parser.write_to_file(file_contents, 0)
        # after writing, should be recorded in file_names
        self.assertIn(temp_path, self.file_parser.file_names)

        # cleanup
        os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()
