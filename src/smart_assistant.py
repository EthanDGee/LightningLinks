from openai import OpenAI
import note_handler
import pydantic
import os
import torch


def parse_similar(directory, similar_notes):
    similar_notes_parsed = ""

    for note in similar_notes:
        # print(note)
        current_similar = note_handler.parse_note(f"{directory}{note}")
        similar_notes_parsed += "file_name: " + note + "\n"
        similar_notes_parsed += "links: " + current_similar['links'] + "\n"
        similar_notes_parsed += "tags: " + current_similar['tags'] + "\n"
        similar_notes_parsed += "body: " + current_similar['body'] + "\n"
        similar_notes_parsed += "\n"

    return similar_notes_parsed


def create(prompt, directory):
    print("Creating new note: \n")

    class NewFile(pydantic.BaseModel):
        file_name: str
        links: str
        tags: str
        body: str
        similar_notes: list[str]

    # get current note
    current_note = note_handler.get_current_note(directory)

    # load similar
    similar_notes_dictionary = note_handler.load_similar_notes(directory)

    similar_notes = similar_notes_dictionary[current_note]

    similar_notes.append(current_note)

    # parse similar

    similar_notes_parsed = parse_similar(directory, similar_notes)

    # get all note names
    all_note_names = note_handler.get_all_note_names(directory)

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
    note_handler.write_to_file(directory, new_note)
    print(f"Successfully created note: {new_note['file_name']}")


def suggest(directory):
    class ExpectedResponse(pydantic.BaseModel):
        suggestion: str
        reasoning: str

    current_note = note_handler.get_current_note(directory)

    # load similar
    similar_notes_dictionary = note_handler.load_similar_notes(directory)

    similar_notes = similar_notes_dictionary[current_note]

    similar_notes.append(current_note)

    # parse similar
    similar_notes_parsed = parse_similar(directory, similar_notes)

    all_note_names = note_handler.get_all_note_names(directory)
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

    user_input = ""
    question = "Would you like to create this note? (y/n)"
    while True:
        print(question)
        user_input = input().lower()
        if user_input == "y" or user_input == "n":
            break
        print("Please enter y or n")

    if user_input == "y":
        prompt = f"create a note about {response.suggestion} making sure that it covers the topics covered in my reasoning {response.reasoning}",
        create(prompt, directory)

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


