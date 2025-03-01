import os


def parse_note(file_path: str):
    # Constants for better readability
    SMART_LINKS_HEADER = "[//]: # (Smart Links)"
    LINK_START = "[["
    LINK_END = "]]"

    # Dictionary to store the parsed note content
    note_info = {"links": "", "body": "", "smart_links": ""}

    # Open the file and iterate through its contents
    with open(file_path, 'r') as file:
        current_line = file.readline()

        # Parse links (header section)
        while current_line:
            if current_line.startswith(LINK_START) and current_line.endswith(LINK_END + "\n"):
                note_info["links"] += current_line[len(LINK_START):-len(LINK_END + "\n")] + "\n"
            else:
                break  # Exit loop when we encounter a non-link line
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
    all_files = {}


    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)

        if os.path.isfile(file_path) and file_name.endswith(".md"):
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
                all_files[file_name] = file_content

    return all_files

if __name__ == "__main__":
    # note_info = parse_note("../demoData/regularization.md")
    # print(note_info)
    #
    # with open("../demoData/regularization.md", 'r') as file:
    #     while file.readline() != "":
    #
    #         print(file.readline())


    parse_file = parse_note("../demoData/regularization.md")
    print(parse_file)


    loaded_files = load_all_markdown_files("../demoData")

    # for file in loaded_files.keys():
    #     print(f"{'-----'*6}{file}{'------'*6}")
    #     print(loaded_files[file])
