import os
import json

from torchgen.gen_functionalization_type import return_from_mutable_noop_redispatch

# final variables
NOTE_EXTENSION = ".md"
EXCLUSIVE_EXTENSION = ".excalidraw.md"
LIGHTNING_LINKS_HEADER = "### Lightning Links"
ENCODING = 'utf-8'
LINK_START = "[["
LINK_END = "]]"


class FileParser:
    def __init__(self, notes_directory):
        self.notes_directory = notes_directory
        self.similar_notes = self.load_similar_notes(notes_directory)

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
            # Process Markdown files only, and exclude similar files that also end with '.md'
            if filename.endswith(NOTE_EXTENSION) and not filename.endswith(EXCLUSIVE_EXTENSION):
                file_path = os.path.join(self.notes_directory, filename)
                self.file_names.append(filename)

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
            if filename.endswith(NOTE_EXTENSION) and not filename.endswith(EXCLUSIVE_EXTENSION):
                note_name = filename.replace(NOTE_EXTENSION, "")
                self.note_names.append(filename)

        # return note names for a case when it's called by an outside program
        return self.note_names

    def ensure_proper_endings(self):
        """
        Ensures proper formatting of Markdown files in the specified notes_directory. This function checks if the Markdown
        files in the notes_directory end properly with an empty line so that if they don't have existing lightning links
        sections in the notes there will be a proper place for them. If the formatting conditions are not met, it appends a
        trailing empty line to the file.


        :return: None
        """

        # loop through all note files
        for file_path in self.file_names:
            # Read the file's contents
            with open(file_path, 'r', encoding=ENCODING) as file:
                lines = file.readlines()

            # Check if the file is not empty and does not end with an empty line, or if its already formatted
            if len(lines) != 0 and not lines[-1].strip() == "" and lines[-2].strip() != LIGHTNING_LINKS_HEADER:
                # Append an empty line
                with open(file_path, 'a', encoding=ENCODING) as file:
                    file.write("\n")

    def parse_note(file_path: str):
        """
        Parses the contents of a Markdown file to extract specific sections: links, tags, body, and smart links.

        Args:
            file_path (str): Path to the Markdown file to be parsed.

        Returns:
            dict: A dictionary containing the following keys:
                - 'links': Links extracted from the header (as a newline-separated string).
                - 'tags': Tags extracted (prefixed with '#', as a single string).
                - 'body': Main content of the file (excluding smart links section).
                - 'smart_links': Smart Links section content (if any, otherwise empty string).
        """

        # Dictionary to store the parsed note content
        note_info = {"links": "", "tags": "", "body": "", "smart_links": ""}

        # Open the file and iterate through its contents
        with open(file_path, 'r', encoding=ENCODING) as file:
            current_line = file.readline()

            # Parse links (header section)
            while current_line:
                if current_line.startswith(LINK_START) and current_line.endswith(LINK_END + "\n"):
                    note_info["links"] += current_line
                else:
                    break  # Exit loop when we encounter a non-link line
                current_line = file.readline()

            # skip the blank line
            current_line = file.readline()
            # Parse Tags

            while current_line:
                if current_line.startswith("#") and not current_line.startswith("# "):
                    note_info["tags"] += current_line
                else:
                    break
                current_line = file.readline()

            # Parse body (main content)
            while current_line:
                if current_line.strip() == LIGHTNING_LINKS_HEADER:  # Stop when we reach the Smart Links section
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

    def get_all_note_names(notes_directory):
        """
        Retrieve all note names from a notes_directory containing Markdown (.md) files.

        This function iterates over all files in the specified notes_directory, identifies
        Markdown files by their extension, and appends the names of these files
        (without the NOTE_EXTENSION extension) to a string. Each note name is formatted and
        separated by a newline in the returned string.

        :param notes_directory: The path to the notes_directory containing the note files.
            Expected to be a string representing a valid notes_directory path.
        :type notes_directory: str

        :return: A string containing formatted names of all Markdown note files in
            the notes_directory. Each name is enclosed in double brackets `[[ ]]` and
            separated by a newline.
        :rtype: str
        """
        all_notes = ""

        for file_name in os.listdir(notes_directory):

            file_path = os.path.join(notes_directory, file_name)
            if os.path.isfile(file_path) and file_name.endswith(NOTE_EXTENSION):
                all_notes += f'{LINK_START}{file_name.replace(NOTE_EXTENSION, "")}{LINK_END}\n'

        return all_notes

    def load_all_markdown_files(notes_directory):
        """
        Iterates through all Markdown (.md) files in a specified notes_directory and parses their contents.

        Args:
            notes_directory (str): Path to the notes_directory containing Markdown files.

        Returns:
            dict: A dictionary where each key is a Markdown file name, and its value is a parsed content
                  dictionary (output of parse_note) extended with a 'file_name' key .
        """

        all_files = []

        for file_name in os.listdir(notes_directory):

            file_path = os.path.join(notes_directory, file_name)
            if os.path.isfile(file_path) and file_name.endswith(NOTE_EXTENSION) and not file_name.endswith(
                    EXCLUSIVE_EXTENSION):
                # with open(file_path, 'r', encoding=ENCODING) as file:
                file_content = parse_note(file_path)
                file_content["file_name"] = file_name
                all_files.append(file_content)

        return all_files

    def format_inline_lighting_links(file_content, num_lightning_links):
        # join a specified number of similar notes into a line
        # format middle
        formatted_links = f"{LINK_END}     {LINK_START}".join(file_content["similar_notes"][:num_lightning_links])
        formatted_links = f"{LINK_START}{formatted_links}{LINK_END}"  # add bookends

        # remove the note extensions from links
        formatted_links.replace(NOTE_EXTENSION, "")

        return formatted_links

    def write_to_file(notes_directory, file_content, num_lightning_links):
        """
        Writes content to a specified file in the given notes_directory, appending formatted
        links and tags, and incorporating a specified number of "lightning links"
        based on a list of similar notes.

        :param notes_directory: The notes_directory path where the file will be created or overwritten.
        :type notes_directory: str
        :param file_content: A dictionary containing the content to be written to the file.
            It is expected to have the following keys:
                - "file_name" (str): Name of the target file.
                - "links" (str): Links to be written in the file.
                - "tags" (str): Tags to be written in the file.
                - "body" (str): Body content to be written in the file.
                - "similar_notes" (list[str]): A list of similar note file names
                  used to generate lightning links.
        :type file_content: dict
        :param num_lightning_links: The number of similar notes to include as lightning links in
            the file's content.
        :type num_lightning_links: int
        :return: None
        """
        with open(f"{notes_directory}{file_content['file_name']}", 'w', encoding=ENCODING) as file:
            file.write(file_content["links"])
            file.write("\n")
            file.write(file_content["tags"])
            file.write(file_content["body"])

            # remove self if there
            if file_content['file_name'] in file_content["similar_notes"]:
                file_content["similar_notes"].remove(file_content['file_name'])

            # add header
            file.write(LIGHTNING_LINKS_HEADER + "\n")

            # add all notes in one line
            file.write(format_inline_lighting_links(file_content, num_lightning_links))

    def save_similar_notes(notes_directory, notes):
        """
        Saves the mapping of similar notes to a JSON file in the specified notes notes_directory.
        This function takes a list of notes where each note is expected to have a file name
        and its corresponding list of similar notes. It then creates a dictionary mapping
        each note's file name to its similar notes and writes this dictionary into a JSON
        file named `similar_notes.json` inside a specified notes_directory.

        :param notes_directory: The path to the notes_directory where the JSON file should be saved.
        :type notes_directory: str

        :param notes: A list of dictionaries, where each dictionary represents a note and
                      should contain `file_name` (str) and `similar_notes` (list) fields.
        :type notes: list[dict]

        """
        similar_notes_dict = {note["file_name"]: note["similar_notes"] for note in notes}
        with open(f"{notes_directory}.obsidian/similar_notes.json", 'w', encoding=ENCODING) as file:
            json.dump(similar_notes_dict, file, indent=4)

    def load_similar_notes(notes_directory):
        """
        Loads a JSON file containing similar notes from the given notes notes_directory and
        returns its content as a dictionary. The file is expected to be located
        within the `.obsidian` subfolder of the specified notes_directory and named
        `similar_notes.json`.

        :param notes_directory: The path to the notes_directory containing the `.obsidian` folder
            with the `similar_notes.json` file.
        :type notes_directory: str
        :return: A dictionary representing the contents of the `similar_notes.json` file.
        :rtype: dict
        """
        with open(f"{notes_directory}.obsidian/similar_notes.json", 'r', encoding=ENCODING) as file:
            similar_notes_dict = json.load(file)
        return similar_notes_dict

    def get_current_note(notes_directory):
        """
        Fetches the most recently opened note file in an Obsidian workspace.

        This function reads the `workspace.json` file within the specified notes notes_directory
        to determine the most recently accessed note in the Obsidian workspace. It
        parses the JSON data to extract the value from the "lastOpenFiles" key.

        :param notes_directory: The notes_directory path containing the Obsidian `.obsidian`
            folder.
        :type notes_directory: str
        :return: The path to the most recently opened note.
        :rtype: str
        :raises FileNotFoundError: If the `workspace.json` file does not exist at
            the specified path.
        :raises json.JSONDecodeError: If the `workspace.json` file content cannot
            be parsed as valid JSON.
        :raises KeyError: If the "lastOpenFiles" key is not found in the loaded JSON
            data.
        """
        with open(f"{notes_directory}.obsidian/workspace.json", 'r', encoding=ENCODING) as file:
            last_open = json.load(file)

        return last_open["lastOpenFiles"][0]
