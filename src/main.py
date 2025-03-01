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


if __name__ == "__main__":
    note_info = parse_note("../demoData/classification.md")
    print(note_info)
