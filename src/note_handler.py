import json
import os
import re
from pathlib import Path

# final variables
NOTE_EXTENSION = ".md"
EXCLUSIVE_EXTENSION = ".excalidraw.md"
LIGHTNING_LINKS_HEADER = "### Lightning Links"
ENCODING = "utf-8"
LINK_START = "[["
LINK_END = "]]"
YAML_INDICATOR = "---\n"
TAG_INDICATOR = "#"


class FileParser:
    def __init__(self, notes_directory: str):
        """
        Represents a class that initializes and manages note-related attributes like file names,
        note names, and similar notes from a specified directory. It supports loading and maintaining
        these data sets for further processing and usage.

        Attributes:
            notes_directory (str): The directory path where note-related files are stored.
            similar_notes: A list or data structure containing similar notes, initialized and
                populated using the `load_similar_notes` method.
            file_names: A list containing names of note-related files from the directory,
                populated using the `load_file_names` method.
            note_names: A list of note names intended for uses like embeddings, populated using
                the `load_note_names` method.

        Args:
            notes_directory: The directory path where note-related files are stored.

        """
        self.notes_directory = Path(notes_directory).as_posix().rstrip("/") + "/"
        self.similar_notes = self.load_similar_notes()

        # these are useful for cases when file data needs to be loaded
        self.file_names = []
        self.load_file_names()

        # Note names are more useful LLM functionality as they are better for embeddings
        self.note_names = []
        self.load_note_names()

    def load_file_names(self):
        """
        Loads file names from the specified notes directory. Filters files based on specific
        extensions, ensuring that only relevant Markdown files are included.

        The method clears the existing list of file names, iterates through the content of
        the directory, and populates the list with eligible file names. Additionally, it
        supports returning the list of file names directly.

        Returns:
            list: A list of file names that match the specified criteria.
        """
        # clear the file names just in case
        self.file_names = []
        # loop through the directory and find all notes
        for filename in os.listdir(self.notes_directory):
            # Process Markdown files only and exclude similar files that also end with '.md'
            if filename.endswith(NOTE_EXTENSION) and not filename.endswith(
                EXCLUSIVE_EXTENSION
            ):
                # create a stable posix-style relative path string
                joined = f"{self.notes_directory}{filename}"
                self.file_names.append(joined)

        # if called by an outside program, it may be nice to immediately return the file_names
        return self.file_names

    def load_note_names(self):
        """
        Loads all note names from the specified notes directory into the instance.

        This method iterates through the directory specified by `self.notes_directory`
        and extracts the names of files with a specific extension defined by
        `NOTE_EXTENSION`. If a file also ends with `EXCLUSIVE_EXTENSION`, it will
        be ignored. The extracted note names are added to the `note_names`
        attribute of the instance. This method also returns the list of
        note names, enabling its use by external programs.

        Returns:
            list: A list of note names derived from the valid file names in the
            notes directory.
        """
        # clear the note names just in case
        self.note_names = []

        # loop through the notes directory and get all note names
        for filename in os.listdir(self.notes_directory):
            # Process Markdown files only and exclude similar files that also end with '.md'
            if filename.endswith(NOTE_EXTENSION) and not filename.endswith(
                EXCLUSIVE_EXTENSION
            ):
                filename = filename.replace(NOTE_EXTENSION, "")
                self.note_names.append(filename)

        # return note names for a case when it's called by an outside program
        return self.note_names

    def ensure_proper_endings(self):
        """
        Ensures proper formatting of Markdown files in the specified notes_directory. This function checks if the Markdown
        files in the notes_directory end properly with an empty line so that if they don't have existing lightning links
        sections in the notes, there will be a proper place for them. If the formatting conditions are not met, it appends a
        trailing empty line to the file.


        :return: None
        """

        def check_last_two_lines(lines):
            # helper function that checks the last two lines of a file for proper formatting and returns a boolean
            # indicating whether they need to be changed.

            # has header in the first line
            if lines[0].strip() == LIGHTNING_LINKS_HEADER:
                return False

            # has new line at the end
            elif lines[1][-1] == "\n":
                return False

            return True

        # loop through all note files
        for file_path in self.file_names:
            # Read the file's contents
            with open(file_path, "r", encoding=ENCODING) as file:
                lines = file.readlines()

            # Check if the file is not empty and does not end with an empty line, or if it's already formatted
            if len(lines) != 0 and check_last_two_lines(lines[-2:]):
                # Append an empty line
                with open(file_path, "a", encoding=ENCODING) as file:
                    file.write("\n")

    @staticmethod
    def parse_note(file_path: str):
        """
        Parses the contents of a Markdown file to extract specific sections: links, tags, body, and smart links.

        Args:
            file_path (str): Path to the Markdown file to be parsed.

        Returns:
            dict: A dictionary containing the following keys:
                - 'links': Links extracted from the header (as a newline-separated string).
                - 'tags': Tags extracted (prefixed with '#', as a single string).
                - 'body': Main content of the file (excluding a smart links section).
                - 'Smart_links': Smart Links section content (if any, otherwise empty string).
        """

        def is_tag(line):
            # checks to see if a given line is a tag, this a more complex check, so it is broken into it's function
            if line.startswith("#"):
                # check to see if it's a header (which would have a space between the word andor multiple hashtags)
                if line.startswith(TAG_INDICATOR + " "):  # H1 Header
                    return False
                elif line.startswith("##"):
                    return False

                # all tests have been passed.
                return True
            else:
                return False

        # Dictionary to store the parsed note content
        note_info = {"links": "", "tags": "", "body": "", "smart_links": "", "YAML": ""}

        # Open the file and iterate through its contents
        with open(file_path, "r", encoding=ENCODING) as file:
            current_line = file.readline()
            # check for YAML and parse YAML if found

            has_yaml = current_line.startswith(YAML_INDICATOR)
            if has_yaml:
                note_info["YAML"] += current_line
                current_line = file.readline()
                while current_line:
                    # add line
                    note_info["YAML"] += current_line
                    # YAML is ended by a second YAML indicator
                    if current_line.startswith(YAML_INDICATOR):
                        # move to the next line now that YAML has been extracted
                        current_line = file.readline()
                        break

                    # move to the next line
                    current_line = file.readline()

            # Parse links (header section)
            # check for a links section and add to contents
            has_links = current_line.startswith(LINK_START) and current_line.endswith(
                LINK_END + "\n"
            )

            if has_links:
                while current_line:
                    if current_line.startswith(LINK_START) and current_line.endswith(
                        LINK_END + "\n"
                    ):
                        note_info["links"] += current_line
                    else:
                        break  # Exit loop when we encounter a non-link line
                    current_line = file.readline()

            # if it has top links, skip the blank line kept between the top links and the tags
            if has_links:
                current_line = file.readline()

            # Parse Tags
            if is_tag(current_line):
                while current_line:
                    if is_tag(current_line):
                        note_info["tags"] += current_line
                    else:
                        break
                    current_line = file.readline()

            # Parse body (main content)
            while current_line:
                # Stop if we reach the optional Smart Links section
                if current_line.strip() == LIGHTNING_LINKS_HEADER:
                    current_line = file.readline()
                    break
                note_info["body"] += current_line
                current_line = file.readline()

            # Parse smart links (optional section at the end)
            while current_line:
                if not current_line.strip():  # Stop at the first empty line
                    break
                note_info["smart_links"] += current_line
                current_line = file.readline()

        return note_info

    def load_all_note_files(self):
        """
        Iterates through all Markdown (.md) files in a specified notes_directory and parses their contents.


        Returns:
            dict: A dictionary where each key is a Markdown file name, and its value is a parsed content
                  dictionary (output of parse_note) extended with a 'file_name' key.
        """

        all_files = []

        for file_name in self.file_names:
            file_content = self.parse_note(file_name)
            file_content["file_name"] = file_name
            all_files.append(file_content)

        return all_files

    @staticmethod
    def parse_inline_lightning_links(line: str) -> list[str]:
        """
        Parses a formatted line containing lightning links taken from a note into a list of associated files.

        This static method takes a single line of text that contains formatted lightning links
        (e.g., [[note_name]]) and identifies all embedded notes. It processes the input line
        using regular expressions to extract these notes and appends a standard file extension
        to each extracted note name, returning the final list of file names.

        Args:
            line (str): A single line of text containing lightning link patterns enclosed within
                double square brackets (e.g., [[note_name]]).

        Returns:
            list[str]: A list of file names generated by appending the predefined note extension
                to each extracted note name.
        """
        # takes a formatted line of lightning links and returns the list of files

        # remove the new line character
        line = line.strip()

        # uses regex to find all notes
        pattern = r"\[\[([^\]]+)\]\]"
        matches = re.findall(pattern, line)

        # Adds the note extension to each match
        links = [match + NOTE_EXTENSION for match in matches]

        return links

    def format_inline_lighting_links(
        self, similar_notes: list[str], num_lightning_links: int
    ):
        """
        Formats a specified number of similar notes into a single inline lightning link. The
        method concatenates the links, adds necessary bookends, and ensures that unnecessary
        paths and extensions are removed for better readability and utility.

        Args:
            similar_notes (list): A collection of similar note names that need to be
                combined into an inline link.
            num_lightning_links (int): The number of lightning links to include from the
                `similar_notes` list.

        Returns:
            str: A formatted string of inline lightning links created based on the input
                parameters.
        """
        # join a specified number of similar notes into a line
        # format middle
        formatted_links = f"{LINK_END}     {LINK_START}".join(
            similar_notes[:num_lightning_links]
        )
        formatted_links = f"{LINK_START}{formatted_links}{LINK_END}"  # add bookends

        # remove the note extensions from links
        formatted_links = formatted_links.replace(NOTE_EXTENSION, "")

        # remove any vault paths just in case
        formatted_links = formatted_links.replace(self.notes_directory, "")

        return formatted_links

    def write_to_file(self, file_content: dict, num_lightning_links: int):
        """
        Writes content to a specified file in the given notes_directory, appending formatted
        links and tags, and incorporating a specified number of "lightning links"
        based on a list of similar notes.

        :param file_content: A dictionary containing the content to be written to the file.
            It is expected to have the following keys:
                - "note_name" (str): Name of the target file.
                - "YAML" (str): YAML header to be written in the file.
                - "links" (str): Links to be written in the file.
                - "tags" (str): Tags to be written in the file.
                - "body" (str): Body content to be written in the file.
                - "Similar_notes" (list[str]): A list of similar note file names
                  used to generate lightning links.
        :type file_content: Dict
        :param num_lightning_links: The number of similar notes to include as lightning links in
            the file's content.
        :type num_lightning_links: Int
        :return: None
        """

        # Set default values for missing keys in file_content
        defaults = {
            "note_name": "",
            "YAML": "",
            "links": "",
            "tags": "",
            "body": "",
            "similar_notes": [],
        }

        # Ensure all keys exist
        for key, value in defaults.items():
            if key not in file_content:
                file_content[key] = value

        with open(f"{file_content['file_name']}", "w", encoding=ENCODING) as file:
            if file_content["YAML"] != "":
                file.write(file_content["YAML"])
            file.write(file_content["links"])
            file.write("\n")
            file.write(file_content["tags"])
            file.write(file_content["body"])

            # remove self if there
            if file_content["file_name"] in file_content["similar_notes"]:
                file_content["similar_notes"].remove(file_content["file_name"])

            # add header
            file.write(LIGHTNING_LINKS_HEADER + "\n")

            # add all notes in one line
            file.write(
                self.format_inline_lighting_links(
                    file_content["similar_notes"], num_lightning_links
                )
            )

        # If a new file was created by this write operation, track it so helper methods
        # (like tests' delete_file) can properly detect it. Store the exact path used.
        if (
            file_content.get("file_name")
            and file_content["file_name"] not in self.file_names
        ):
            p = Path(file_content["file_name"])
            try:
                if p.is_absolute():
                    self.file_names.append(p.as_posix())
                else:
                    # if the provided name is already rooted in the notes directory posix base
                    if str(file_content["file_name"]).startswith(self.notes_directory):
                        self.file_names.append(file_content["file_name"])
                    else:
                        self.file_names.append(
                            (Path(self.notes_directory) / p.as_posix()).as_posix()
                        )
            except Exception:
                # fallback to the provided string
                self.file_names.append(file_content["file_name"])

    def update_lighting_links(
        self, file_path: str, similar_notes: list[str], num_lightning_links: int
    ) -> bool:
        """
        Updates or adds lightning links in the provided file.

        This function takes a file path and updates the list of lightning links if there are any
        changes required. If the `LIGHTNING_LINKS_HEADER` is not found in the file, it appends
        the header along with the appropriate lightning links section at the end of the file. The
        function overwrites the file when updates are made.

        Args:
            file_path (str): Path to the file that contains the notes and lightning links.
            similar_notes (list[str]): A list of similar notes that will be formatted as lightning
                links.
            num_lightning_links (int): The number of formatted lightning links to include.

        Returns:
            bool: True if the file was updated, False if no updates were required.
        """
        # takes in a note path and lightning link and adds/updates lightning links if changes have been made.

        formatted_links = self.format_inline_lighting_links(
            similar_notes, num_lightning_links
        )

        # If the file doesn't exist, create it so subsequent operations succeed
        p = Path(file_path)
        if not p.exists():
            parent_dir = p.parent
            if parent_dir and not parent_dir.exists():
                parent_dir.mkdir(parents=True, exist_ok=True)
            # create empty file
            p.write_text("", encoding=ENCODING)

        with open(file_path, "r+", encoding=ENCODING) as file:
            # Read the entire content to work with in-memory
            lines = file.readlines()
            # If file is empty, write header + links and return
            if not lines:
                file.seek(0)
                file.writelines([LIGHTNING_LINKS_HEADER + "\n", formatted_links + "\n"])
                file.truncate()
                return True

            found_section = False

            # Locate the Lightning Links header
            for i, line in enumerate(lines):
                if line.strip() == LIGHTNING_LINKS_HEADER:
                    found_section = True
                    if i + 1 < len(lines):  # Check for the next line
                        existing_links = lines[i + 1].strip()
                        if existing_links == formatted_links:
                            return False  # No updates required
                        else:
                            # Replace the existing line and truncate properly
                            lines[i + 1] = formatted_links + "\n"
                    else:
                        # If the Lightning Links header exists but no links line is found
                        lines.append(formatted_links + "\n")
                    break

            if not found_section:
                # Append a Lightning Links section at the end of the file
                if not lines[-1].endswith("\n"):
                    lines[-1] += "\n"  # Ensure a new line before appending
                lines.append(LIGHTNING_LINKS_HEADER + "\n")
                lines.append(formatted_links + "\n")

            # Rewind the file pointer, overwrite the content, and truncate the file
            file.seek(0)
            file.writelines(lines)
            file.truncate()  # Ensure the file is truncated to remove leftover content

            return True  # Indicates content was updated

    def save_similar_notes(self, notes):
        """
        Saves the mapping of similar notes to a JSON file in the specified notes notes_directory.
        This function takes a list of notes where each note is expected to have a file name
        and its corresponding list of similar notes. It then creates a dictionary mapping
        each note's file name to its similar notes and writes this dictionary into a JSON
        file named `similar_notes.json` inside a specified notes_directory.

        :param notes: A list of dictionaries, where each dictionary represents a note and
                      should contain `file_name` (str) and `similar_notes` (list) fields.
        :type notes: List[dict]

        """
        similar_notes_dict = {
            note["file_name"]: note["similar_notes"] for note in notes
        }
        obsidian_dir = Path(self.notes_directory) / ".obsidian"
        obsidian_dir.mkdir(parents=True, exist_ok=True)
        with open(
            (obsidian_dir / "similar_notes.json").as_posix(), "w", encoding=ENCODING
        ) as file:
            json.dump(similar_notes_dict, file, indent=4)

    def load_similar_notes(self):
        """
        Loads a JSON file containing similar notes from the given notes notes_directory and
        returns its content as a dictionary. The file is expected to be located
        within the `.obsidian` subfolder of the specified notes_directory and named
        `similar_notes.json`.

        :return: A dictionary representing the contents of the `similar_notes.json` file.
        :rtype: Dict
        """
        with open(
            (
                Path(self.notes_directory) / ".obsidian" / "similar_notes.json"
            ).as_posix(),
            "r",
            encoding=ENCODING,
        ) as file:
            similar_notes_dict = json.load(file)
        return similar_notes_dict

    def get_current_note(self):
        """
        Fetches the most recently opened note file in an Obsidian workspace.

        This function reads the `workspace.json` file within the specified notes notes_directory
        to determine the most recently accessed note in the Obsidian workspace. It
        parses the JSON data to extract the value from the "lastOpenFiles" key.

        :return: The path to the most recently opened note.
        :rtype: Str
        :raises FileNotFoundError: If the `workspace.json` file does not exist at
            the specified path.
        :raises json.JSONDecodeError: If the `workspace.json` file content cannot
            be parsed as valid JSON.
        :raises KeyError: If the "lastOpenFiles" key is not found in the loaded JSON
            data.
        """
        with open(
            (Path(self.notes_directory) / ".obsidian" / "workspace.json").as_posix(),
            "r",
            encoding=ENCODING,
        ) as file:
            last_open = json.load(file)

        return last_open["lastOpenFiles"][0]
