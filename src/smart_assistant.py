from openai import OpenAI
import note_handler
import pydantic
import os
import torch


def parse_similar(notes_directory, similar_notes):
    """
    Parses a list of similar note files within a provided directory and generates
    a formatted string containing details such as the file name, links, tags, and
    body content of each note. This function processes the notes by leveraging
    a parsing utility from the `note_handler` module.

    :param notes_directory: Location of the directory containing the note files.
    :type notes_directory: str
    :param similar_notes: List of note file names to be parsed.
    :type similar_notes: list[str]
    :return: A formatted string containing details of the parsed similar notes.
    :rtype: str
    """
    similar_notes_parsed = ""

    for note in similar_notes:
        # print(note)
        current_similar = note_handler.parse_note(f"{notes_directory}{note}")
        similar_notes_parsed += "file_name: " + note + "\n"
        similar_notes_parsed += "links: " + current_similar['links'] + "\n"
        similar_notes_parsed += "tags: " + current_similar['tags'] + "\n"
        similar_notes_parsed += "body: " + current_similar['body'] + "\n"
        similar_notes_parsed += "\n"

    return similar_notes_parsed


def create(prompt, notes_directory):
    """
    Creates a new note based on the given user prompt pulling from relevant
    existing notes in the specified directory. This function uses OpenAI's
     model to generate a structured response that adheres to the `NewFile`
     class format. The note is then saved to the  specified directory upon
     successful creation.

    :param prompt: The main user input that specifies the content or context for
        the note to be created.
    :type prompt: str
    :param notes_directory: The directory path where the current and new notes are or
        will be stored, including any similar note references.
    :type notes_directory: str
    :return: None
    """
    print("Creating new note: \n")

    class NewFile(pydantic.BaseModel):
        file_name: str
        links: str
        tags: str
        body: str
        similar_notes: list[str]

    # get current note
    current_note = note_handler.get_current_note(notes_directory)

    # load similar
    similar_notes_dictionary = note_handler.load_similar_notes(notes_directory)

    similar_notes = similar_notes_dictionary[current_note]

    similar_notes.append(current_note)

    # parse similar

    similar_notes_parsed = parse_similar(notes_directory, similar_notes)

    # get all note names
    all_note_names = note_handler.get_all_note_names(notes_directory)

    # ask open AI for structured output that matches newFile
    model = "gpt-4o-mini"
    response_format = NewFile
    temperature = 0.5

    # set up prompts

    system_prompt = """
    You will be provided with the parsed contents of a note, as well as some similar notes that reference the same topic, as well as a list of links to select for the linking process.
    Your goal is to create a new note that is structured in a way that aligns with the parameters of the NewFile class, and covers the topic provided in the user prompt
    The parameters are as follows:
    - file_name: short title summarizing the main idea of the note
    - links: a string of links to other notes or resources related to the note seperated by newlines
    - tags: a string of keywords or tags associated with the note
    - body: a note on the topic provided in the user prompt that matches the styling of the other bodies provided
    - similar_notes: array of titles (or identifiers) of related notes or similar entries if present
    """

    user_prompt = f"""{prompt} \nSimilar Notes: \n{similar_notes_parsed} \n All Available Links\n {all_note_names}"""

    # request
    client = OpenAI(api_key=os.getenv("open_ai_key"))
    completion = client.beta.chat.completions.parse(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format=response_format,
    )

    # set up return for note creation
    parsed_return = completion.choices[0].message.parsed

    new_note = {
        "file_name": f"{parsed_return.file_name}.md",
        "links": f'{parsed_return.links}\n',
        "tags": f'{parsed_return.tags}\n',
        "body": f'{parsed_return.body}\n',
        "similar_notes": parsed_return.similar_notes
    }

    # save note using note_handler.write_note
    note_handler.write_to_file(notes_directory, new_note, 3)
    print(f"Successfully created note: {new_note['file_name']}")


def suggest(notes_directory):
    """
    Suggests a new note topic based on the provided directory containing existing notes and their
    metadata. The suggestion is derived by analyzing similar notes, parsed content, and the overall
    list of available notes to try and find gaps in the users obsidian zettlekasten system. Utilizes
    open AIs structured output to generate a structured response that adheres to the `ExpectedResponse`
    with data about the suggested topic and a reasoning for the suggestion.

    :param notes_directory: The directory containing the existing notes and metadata.
    :type notes_directory: str

    :return: None
    """
    class ExpectedResponse(pydantic.BaseModel):
        suggestion: str
        reasoning: str

    current_note = note_handler.get_current_note(notes_directory)

    # load similar
    similar_notes_dictionary = note_handler.load_similar_notes(notes_directory)

    similar_notes = similar_notes_dictionary[current_note]

    similar_notes.append(current_note)

    # parse similar
    similar_notes_parsed = parse_similar(notes_directory, similar_notes)

    all_note_names = note_handler.get_all_note_names(notes_directory)
    temperature = 0.5

    system_prompt = """
        You will be provided with the parsed contents of a note, as well as some similar notes that reference the same topic, as well as a list of links to select for the linking process.
        Your goal is to suggest a topic for a note that is not covered by the overall list of files provided and that covers a similar topic to the example notes
        Your out put should be structured in a way that aligns with the parameters of the Response class, and provides a reasoning for the suggestion provided
        - suggestion: a topic that is related to the fields provided, but is not covered in the overall list of all available notes
        - reasoning: a short reasoning for the suggestion provided
        
        The example notes will be structured in this format:
        - file_name: short title summarizing the main idea of the note
        - links: a string of links to other notes or resources related to the note seperated by newlines
        - tags: a string of keywords or tags associated with the note
        - body: a note on the topic provided in the user prompt that matches the styling of the other bodies provided
        - similar_notes: array of titles (or identifiers) of related notes or similar entries if present
        """

    user_prompt = f"""\nSimilar Notes: \n{similar_notes_parsed} \n All Available Notes\n {all_note_names}"""
    response_format = ExpectedResponse

    # request
    client = OpenAI(api_key=os.getenv("open_ai_key"))
    model = "gpt-4o-mini"
    completion = client.beta.chat.completions.parse(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format=response_format,
    )

    response = completion.choices[0].message.parsed

    print(f"Looking at your notes it seems best to create a note about {response.suggestion}")
    print("Here's why I think you should: \n" + response.reasoning + "\n")

    question = "Would you like to create this note? (y/n)"
    while True:
        print(question)
        user_input = input().lower()
        if user_input == "y" or user_input == "n":
            break
        print("Please enter y or n")

    if user_input == "y":
        prompt = f"create a note about {response.suggestion}"
        create(prompt, notes_directory)


if __name__ == "__main__":

    print(torch.cuda.is_available())

    print("Welcome to the Lightning Notes Assistant!")
    print("The best way to find holes in your notes, and automagically create plugs to fill them")
    print("To get started, please enter the directory where your notes are stored")
    while True:
        directory = input("Enter the directory path: ")
        if not os.path.isdir(directory):
            print("Error: The provided path is not a valid directory. Please try again.")
        else:
            break

    print("\nExcellent! Now let's get started with introducing you to our tools:")
    print("Currently, we have two tools:")
    print(
        "1. Suggest: This looks at the notes you've been looking at recently and suggests a topic that you might want to add to your notes.")
    print("2. Create: This creates a new note based on the topic you suggest.")
    print("\nTo get started, please enter the command you would like to use:")
    while True:
        print("\n\nAvailable commands:")
        print("s: Suggest")
        print("c: Create")
        print("q: Quit")
        command = input("Enter your choice (s/c/q): ").lower()
        if command == 's':
            suggest(directory)
        if command == 'c':
            create(input("Enter the topic you would like to create: "), directory)
        if command == 'q':
            break

        if command not in ["s", "c", "q"]:
            print("Invalid command. Please enter a valid command.")
