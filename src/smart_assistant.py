from openai import OpenAI
from torch.onnx.symbolic_opset9 import new_full

import note_handler
import pydantic
import os


def create(prompt, directory):
    class NewFile(pydantic.BaseModel):
        file_name: str
        links: str
        tags: str
        body: str
        similar_notes: list[str]

    client = OpenAI(api_key=os.getenv("open_ai_key"))

    # get current note
    current_note = note_handler.get_current_note(directory)

    # get all available notes

    available_note_names = note_handler.get_all_note_names(directory)

    # load similar
    similar_notes = note_handler.load_similar_notes(directory)

    # parse similar
    similar_notes_parsed = ""


    for note in similar_notes:
        # print(note)
        current_similar = note_handler.parse_note(f"{directory}{note}")
        similar_notes_parsed +="file_name: "  + note+ "\n"
        similar_notes_parsed +="links: "  + current_similar['links'] + "\n"
        similar_notes_parsed +="tags: "  + current_similar['tags'] + "\n"
        similar_notes_parsed +="body: "  + current_similar['body'] + "\n"
        similar_notes_parsed +="\n"


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



    user_prompt = f"""{prompt} \nSimilar Notes: \n{similar_notes_parsed} \n All Available Links\n {all_note_names}"""


    completion = client.beta.chat.completions.parse(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format=response_format,
    )

    parsed_return = completion.choices[0].message.parsed

    new_note = {
        "file_name": parsed_return.file_name,
        "links": parsed_return.links,
        "tags": parsed_return.tags,
        "body": parsed_return.body,
        "similar_notes": parsed_return.similar_notes
    }

    #
    note_handler.write_to_file(directory, new_note)
    print(f"Successfully created note: {new_note['file_name']}")

if __name__ == "__main__":
    # openai.api_key = os.getenv("open_ai_key")
    create("create a note about user accessability", '../demoData/')