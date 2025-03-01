import os


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
    SMART_LINKS_HEADER = "[//]: # (Smart Links)"
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
                note_info["links"] += current_line[len(LINK_START):-len(LINK_END + "\n")] + "\n"
            else:
                break  # Exit loop when we encounter a non-link line
            current_line = file.readline()

        # skip the blank line
        current_line = file.readline()
        # Parse Tags

        while current_line:
            if current_line.startswith("#") and not current_line.startswith("# "):
                note_info["tags"] += current_line.strip("\n")
            else:
                break
            current_line = file.readline()

        # Parse body (main content)
        while current_line:
            if current_line.strip() == SMART_LINKS_HEADER:  # Stop when we reach the Smart Links section
                current_line = file.readline()
                break
            note_info["body"] += current_line.strip("\n")
            current_line = file.readline()

        # Parse smart links (optional section at the end)
        while current_line:
            if not current_line.strip():  # Stop at the first empty line
                break
            note_info["smart_links"] += current_line.strip("\n")
            current_line = file.readline()

    return note_info


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
        if os.path.isfile(file_path) and file_name.endswith(".md"):
            # with open(file_path, 'r', encoding='utf-8') as file:
            file_content = parse_note(file_path)
            file_content["file_name"] = file_name
            all_files.append(file_content)

    return all_files

def append_to_file(file_path, file_names):
    with open(file_path, 'rw', encoding='utf-8') as file:

        SMART_LINKS_HEADER = "[//]: # (Smart Links)"

        # go until SMART LINKS HEADER IS HIT

        current_line = file.readline()
        found_header = False
        while current_line:
            if current_line == SMART_LINKS_HEADER:
                found_header = True
                break
            current_line = file.readline()

        # now we are going to append the contents to the file
        if not found_header:
            file.write(SMART_LINKS_HEADER + "\n")

        for file_name in file_names:
            file.write(f"[[{file_name}]]\n")





