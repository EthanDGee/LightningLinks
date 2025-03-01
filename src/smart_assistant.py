from openai import OpenAI
import note_handler
import pydantic

def format_similar_notes()


def create(prompt, directory):
    class NewFile(pydantic.BaseModel):
        links: str
        tags: str
        body: str
        similar_notes: list

    client = OpenAI()

    # get current note
    current_note = note_handler.get_current_note()

    # load similar
    similar_notes = note_handler.load_similar_notes(directory)

    # parse similar
    similar_notes_parsed = []

    for note in similar_notes:
        similar_notes_parsed.append(note_handler.parse_note(f"{directory}{note}"))

    # get all note names
    all_note_names = note_handler.get_all_note_names(directory)

    # ask open AI for structured output that matches newFile
    model = 'gpt-4o'
    response_format = NewFile
    temperature = 0.5

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

    # save note using note_handler.write_note



    user_prompt = f""""""


    completion = client.beta.chat.completions.parse(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": note_content}
        ],
        response_format=response_format,
    )

    note_handler.write_to_file(directory, new_note)


