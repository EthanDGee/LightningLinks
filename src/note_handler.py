import os
import json

def ensure_trailing_empty_line(directory):
    """
    Ensures proper formatting of Markdown files in the specified directory. This function checks if the Markdown
    files in the directory end properly with an empty line so that if they don't have existing lightning links
    sections in the notes there will be a proper place for them. If the formatting conditions are not met, it appends a
    trailing empty line to the file.

    :param directory: The directory path where the Markdown files are located.
    :type directory: str

    :return: None
    """
    print("Ensuring formatting of files...")

    LIGHTNING_LINKS_HEADER = "### Lightning Links"

    files_updated = 0
    for filename in os.listdir(directory):
        if filename.endswith(".md") and not filename.endswith(".excalidraw.md"):  # Process Markdown files only
            file_path = os.path.join(directory, filename)

            # Read the file's contents
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            # Check if the file is not empty and does not end with an empty line, or if its already formatted
            if len(lines) != 0 and not lines[-1].strip() == "" and lines[-2].strip() != LIGHTNING_LINKS_HEADER:
                print(f"Updated {filename}")
                files_updated += 1
                # Append an empty line
                with open(file_path, 'a', encoding='utf-8') as file:
                    file.write("\n")


    print(f"Updated {files_updated} files to fit conventions.")

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
    # Constants for better readability
    LIGHTNING_LINKS_HEADER = "### Lightning Links"
    LINK_START = "[["
    LINK_END = "]]"

    # Dictionary to store the parsed note content
    note_info = {"links": "", "tags": "", "body": "", "smart_links": ""}

    # Open the file and iterate through its contents
    with open(file_path, 'r', encoding='utf-8') as file:
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


def get_all_note_names(directory):
    """
    Retrieve all note names from a directory containing Markdown (.md) files.

    This function iterates over all files in the specified directory, identifies
    Markdown files by their extension, and appends the names of these files
    (without the ".md" extension) to a string. Each note name is formatted and
    separated by a newline in the returned string.

    :param directory: The path to the directory containing the note files.
        Expected to be a string representing a valid directory path.
    :type directory: str

    :return: A string containing formatted names of all Markdown note files in
        the directory. Each name is enclosed in double brackets `[[ ]]` and
        separated by a newline.
    :rtype: str
    """
    all_notes = ""

    for file_name in os.listdir(directory):

        file_path = os.path.join(directory, file_name)
        if os.path.isfile(file_path) and file_name.endswith(".md"):
            all_notes += f'[[{file_name.replace(".md", "")}]]\n'

    return all_notes


def load_all_markdown_files(directory):
    """
    Iterates through all Markdown (.md) files in a specified directory and parses their contents.

    Args:
        directory (str): Path to the directory containing Markdown files.

    Returns:
        dict: A dictionary where each key is a Markdown file name, and its value is a parsed content
              dictionary (output of parse_note) extended with a 'file_name' key .
    """

    all_files = []

    for file_name in os.listdir(directory):

        file_path = os.path.join(directory, file_name)
        if os.path.isfile(file_path) and file_name.endswith(".md") and not file_name.endswith(".excalidraw.md"):
            # with open(file_path, 'r', encoding='utf-8') as file:
            file_content = parse_note(file_path)
            file_content["file_name"] = file_name
            all_files.append(file_content)

    return all_files



def write_to_file(directory, file_content, num_lightning_links):
    """
    Writes content to a specified file in the given directory, appending formatted
    links and tags, and incorporating a specified number of "lightning links"
    based on a list of similar notes.

    :param directory: The directory path where the file will be created or overwritten.
    :type directory: str
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
    with open(f"{directory}{file_content['file_name']}", 'w', encoding='utf-8') as file:
        file.write(file_content["links"])
        file.write("\n")
        file.write(file_content["tags"])
        file.write(file_content["body"])

        smart_links_header = "### Lightning Links"

        # remove self if there
        if file_content['file_name'] in file_content["similar_notes"]:
            file_content["similar_notes"].remove(file_content['file_name'])

        # add header
        file.write(smart_links_header + "\n")

        # add all notes in one line
        file.write(f"[[{"]]     [[".join(file_content["similar_notes"][:num_lightning_links])}]]".replace(".md", ""))


def save_similar_notes(directory, notes):
    """
    Saves the mapping of similar notes to a JSON file in the specified notes directory.
    This function takes a list of notes where each note is expected to have a file name
    and its corresponding list of similar notes. It then creates a dictionary mapping
    each note's file name to its similar notes and writes this dictionary into a JSON
    file named `similar_notes.json` inside a specified directory.

    :param directory: The path to the directory where the JSON file should be saved.
    :type directory: str

    :param notes: A list of dictionaries, where each dictionary represents a note and
                  should contain `file_name` (str) and `similar_notes` (list) fields.
    :type notes: list[dict]

    :return: None
    :rtype: None
    """
    similar_notes_dict = {note["file_name"]: note["similar_notes"] for note in notes}
    with open(f"{directory}.obsidian/similar_notes.json", 'w', encoding='utf-8') as file:
        json.dump(similar_notes_dict, file, indent=4)


def load_similar_notes(directory):
    """
    Loads a JSON file containing similar notes from the given notes directory and
    returns its content as a dictionary. The file is expected to be located
    within the `.obsidian` subfolder of the specified directory and named
    `similar_notes.json`.

    :param directory: The path to the directory containing the `.obsidian` folder
        with the `similar_notes.json` file.
    :type directory: str
    :return: A dictionary representing the contents of the `similar_notes.json` file.
    :rtype: dict
    """
    with open(f"{directory}.obsidian/similar_notes.json", 'r', encoding='utf-8') as file:
        similar_notes_dict = json.load(file)
    return similar_notes_dict


def get_current_note(directory):
    """
    Fetches the most recently opened note file in an Obsidian workspace.

    This function reads the `workspace.json` file within the specified notes directory
    to determine the most recently accessed note in the Obsidian workspace. It
    parses the JSON data to extract the value from the "lastOpenFiles" key.

    :param directory: The directory path containing the Obsidian `.obsidian`
        folder.
    :type directory: str
    :return: The path to the most recently opened note.
    :rtype: str
    :raises FileNotFoundError: If the `workspace.json` file does not exist at
        the specified path.
    :raises json.JSONDecodeError: If the `workspace.json` file content cannot
        be parsed as valid JSON.
    :raises KeyError: If the "lastOpenFiles" key is not found in the loaded JSON
        data.
    """
    with open(f"{directory}.obsidian/workspace.json", 'r', encoding='utf-8') as file:
        last_open = json.load(file)

    return last_open["lastOpenFiles"][0]


if __name__ == "__main__":
    directory = "C:/Users/ethan/SecondBrain/SecondBrain/"
    ensure_trailing_empty_line(directory)

