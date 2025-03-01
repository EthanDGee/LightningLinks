import os


def parse_note(file_path: str):
    smart_links_header = "[//]: # (Smart Links)"

    # set up dictionary
    note_info = {"links": "", "body": "", "smart_links": ""}

    # read through the file and place into seperate categories
    with open(file_path, 'r') as file:
        in_headers = True

        # parse header links

        while in_headers:

            line = file.readline()

            # if the link follows the conventional link format
            if line[0:1] == '[[' and line[-3:] == "]]\n":
                note_info["links"] += line[2:-3] + "\n"

            if line == "":
                # if the end of the file is reached return parsed information

                in_headers = False
                return note_info

        # parse body
        in_body = True

        while in_body:
            line = file.readline()



            if line.strip("\n") == smart_links_header:
                in_body = False
            else:
                note_info["body"] += line.strip("\n")

        # parse smart_links (optional)
        end_of_note = False
        while not end_of_note:
            line = file.readline()
            if line.strip("\n") == "":
                end_of_note = True
            else:
                note_info["smart_links"] += line.strip("\n")


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


    loaded_files = load_all_markdown_files("../demoData")

    for file in loaded_files.keys():
        print(f"{'-----'*6}{file}{'------'*6}")
        print(loaded_files[file])
