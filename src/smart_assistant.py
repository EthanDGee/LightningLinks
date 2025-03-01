from openai import OpenAI
from torch.onnx.symbolic_opset9 import new_full

import note_handler
import pydantic



def create(prompt, directory):
    class NewFile(pydantic.BaseModel):
        links: str
        tags: str
        body: str
        similar_notes : str

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

    # ask open ai for structured output that matches newFile
    model = 'gpt-4o'
    response_format = NewFile
    temperature = 0.5

    system_prompt


    # save note using note_handler.write_note

    similar_notes = note_handler.load_similar_notes(directory)


