from openai import OpenAI
from note_handler import FileParser
from typing import Type
import pydantic
import os
import torch

NOTE_EXTENSION = ".md"


class SmartAssistant:
    def __init__(self, notes_directory):
        self.file_handler = FileParser(notes_directory)
        self.similar_notes = self.file_handler.load_similar_notes()

        self.model = "gpt-4o-mini"
        self.client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

    def get_core_similar_notes(self, notes):
        # a much simpler version of parse_similar() that only gets the body and file name for each note.
        similar_bodies = ""

        for note in notes:
            current_similar = self.file_handler.parse_note(f"{self.notes_directory}{note}")
            similar_bodies += f"{note}\n"
            similar_bodies += current_similar['body'] + "\n"

        return similar_bodies

    def make_open_ai_request(self, system : str, user : str, temp: float, structure: Type[pydantic.BaseModel] = None):
        """
        Makes a request to OpenAI's API for generating a completion based on the provided
        prompts, model, temperature, and desired response format.

        This method utilizes OpenAI's chat completion endpoint to process a conversation-style
        request. It constructs the message payload with the system and user prompts, specifies
        the temperature for randomness, and defines how the response should be formatted.

        Args:
            system: Text provided to set the system context or behavior for the
                AI assistant. This is typically a guideline or instruction for how the
                AI should respond.
            user: Text representing the user's input or question that the AI
                should respond to.
            temp: A float value controlling the randomness of the output. Lower values
                result in more deterministic outputs, while higher values increase
                randomness.
            structure: Specifies how the response from the AI should be
                structured or parsed.

        Returns:
            The parsed content of the AI's response message.
        """


        # check for a structured response
        if structure is None:
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                temperature=temp,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ]
            )

            return completion.choices[0].message.content
        else:
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                temperature=temp,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                response_format=structure,
            )

            return completion.choices[0].message.parsed

    def recommend_note(self, prompt):
        """
        Suggests the most relevant file for a given user prompt based on the provided files list.
        Utilizes OpenAI to infer the best match by analyzing the given system prompt, user prompt,
        and available file names. Returns the name of the most relevant file.

        Args:
            prompt: A string containing the user's input or query for which the most relevant file
                needs to be identified.

        Returns:
            str: The name of the suggested file from the available list of file names.
        """

        class FileName(pydantic.BaseModel):
            file_name: str

        system_prompt = (
            "You are a research assistant who's job is to suggest the most relevant file for a given prompt."
            " and return its name making sure to select one from list of files provided. ")

        all_note_names = ""

        for note_name in self.file_handler.note_names:
            all_note_names += note_name + "\n"

        # remove the links
        user_prompt = prompt + "\n\n\nFiles:\n" + all_note_names
        temperature = 0.1

        print("Looking for relevant file...")

        suggestion = self.make_open_ai_request(system_prompt, user_prompt, temperature, FileName)

        return suggestion.file_name

    def get_similar_notes_contents(self, note_name):
        """
        Retrieves and formats the contents of similar notes to the specified note.

        This method first adds the file extension to the note name to ensure it can be properly
        located, even if not included in the note listing. It then retrieves a list of similar
        notes to the specified note, appending the specified note itself to the list. The contents
        of each similar note are parsed and formatted, including file name, links, tags,
        and body content.

        Args:
            note_name (str): The name of the note (without file extension) for which similar notes
            need to be retrieved.

        Returns:
            str: A formatted string containing details of all similar notes, including their file
            names, links, tags, and body content.
        """

        # load similar

        print(f"Getting notes related to {note_name}")

        note_name = f"{self.file_handler.notes_directory}{note_name}"
        similar_notes = self.similar_notes[note_name]
        similar_notes.append(note_name)

        similar_notes_parsed = ""

        for note in similar_notes:
            current_similar = self.file_handler.parse_note(f"{note}")
            similar_notes_parsed += "file_name: " + note + "\n"
            similar_notes_parsed += "links: " + current_similar['links'] + "\n"
            similar_notes_parsed += "tags: " + current_similar['tags'] + "\n"
            similar_notes_parsed += "body: " + current_similar['body'] + "\n"
            similar_notes_parsed += "\n"

        return similar_notes_parsed

    def create(self, prompt):
        """
        Creates a new note based on the provided user prompt and related contextual data.

        This method generates a structured note that adheres to a predefined format
        using data provided by user input and supplementary resources, such as parsed
        similar notes and available links. The note is structured according to the NewFile
        class, including attributes like file name, links, tags, body, and related notes.
        The method uses an external service (e.g., OpenAI API) to create the structured
        content, then saves the result using the file handler.

        Args:
            prompt (str): The user-provided topic or description for which the new note
                should be created.
        """
        print("Creating new note: \n")

        class NewFile(pydantic.BaseModel):
            file_name: str
            links: str
            tags: str
            body: str
            similar_notes: list[str]

        # get a suggested file that matches the user suggest topic
        file_name = self.recommend_note(prompt)
        similar_notes_parsed = self.get_similar_notes_contents(file_name)

        # get all note names
        all_note_names = self.file_handler.note_names

        # ask open AI for structured output that matches newFile

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
        request = self.make_open_ai_request(system_prompt, user_prompt, 0.5, NewFile)

        new_note = {
            "file_name": self.clean_up_note_name(request.file_name),
            "links": f'{request.links}\n',
            "tags": f'{request.tags}\n',
            "body": f'{request.body}\n',
            "similar_notes": request.similar_notes
        }

        # save note using note_handler.write_note
        self.file_handler.write_to_file(new_note, 3)

        print(f"Successfully created note: {new_note['file_name']}")

    def suggest(self):
        """
        Suggests a new note topic based on analysis of current and similar notes, and provides reasoning for the suggestion.

        This method interacts with the user's notes to propose a new topic not yet covered.
        The suggestion is derived by analyzing the contents of the current note, as well as
        similar notes, and comparing them against all available note topics. The generated
        suggestion is returned with reasoning. The method also prompts the user for confirmation
        to create a new note based on the suggested topic.

        Attributes:
            ExpectedResponse: A pydantic model representing the structure of the response
                provided by the OpenAI request. It contains 'suggestion' for the proposed
                topic and 'reasoning' for the rationale behind the suggestion.

        Raises:
            None
        """

        class ExpectedResponse(pydantic.BaseModel):
            suggestion: str
            reasoning: str

        current_note = self.file_handler.get_current_note()

        # load similar

        similar_notes_parsed = self.get_similar_notes_contents(current_note)
        all_note_names = self.file_handler.note_names

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

        response = self.make_open_ai_request(system_prompt, user_prompt, 0.5, ExpectedResponse)

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
            self.create(prompt)

    def ask_yourself(self, prompt):
        """
        Generates a response by leveraging research notes relevant to the input prompt, in accordance
        with the context and style of the reference material. This function utilizes a specified
        recommendation mechanism to identify the most relevant notes, extracts their contents, and
        employs an external AI service to produce the final response.

        The process involves:
        1. Recommending the most relevant note based on the user's input prompt.
        2. Extracting content from notes deemed similar to the recommended note.
        3. Formulating a system and user prompt for the external AI service.
        4. Requesting and printing a response formatted in alignment with the extracted research notes.

        Args:
            prompt (str): The user's input prompt, which serves to guide the note recommendation
                and response generation processes.
        """

        recommended_note = self.recommend_note(prompt)
        # add a file extension so it can't be looked up, its not in list_all_note_name to prevent embedding errors.
        recommended_note = recommended_note + ".md"

        # now we get the similar files and ask for a response based on their inputs

        system_prompt = (
            "You are a research assistant who's job is to provide a response based on the user's "
            "input using their research notes as the basis for your response. While also making "
            "sure to respond in accordance with the style of the notes you have been given."
        )
        # get the source material

        extracted_references = self.get_similar_notes_contents(recommended_note)

        user_prompt = prompt + "\n\n\nNotes:\n" + extracted_references

        response = self.make_open_ai_request(system_prompt, user_prompt, 0.4)

        print(response)

    @staticmethod
    def clean_up_note_name(note_name):
        # returns a cleaned-up note name that matches the styling convention of obsidian

        # swap out space alternatives for spaces
        note_name = note_name.replace("_", " ")
        note_name = note_name.replace("-", " ")

        # add extension if it's missing
        if NOTE_EXTENSION not in note_name:
            note_name += NOTE_EXTENSION

        return note_name


if __name__ == "__main__":

    arguments = os.sys.argv

    if len(arguments) > 1:
        directory = arguments[1]
    else:
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
    # initiate smart assistant

    smart_assistant = SmartAssistant(directory)

    print("Excellent! Now let's get started with introducing you to our tools:")
    print("Currently, we have three tools:")
    print(
        "1. Suggest: This looks at the notes you've been looking at recently and suggests a topic that you might want "
        "to add to your notes.")
    print("2. Create: This creates a new note based on the topic you suggest.")
    print("3. Ask yourself a question about your notes: This allows you to ask questions about your notes and get a "
          "response back.")
    print("\nTo get started, please enter the command you would like to use:")
    while True:
        print("\n\nAvailable commands:")
        print("s: Suggest")
        print("c: Create")
        print("a: Ask yourself a question about your notes")
        print("q: Quit")
        command = input("Enter your choice (s/c/a/q): ").lower()
        if command == 's':
            smart_assistant.suggest()
        if command == 'c':
            smart_assistant.create(input("Enter the topic you would like to create: "))
        if command == 'a':
            smart_assistant.ask_yourself(input("Enter your question: "))
        if command == 'q':
            break

        if command not in ["s", "c", "q"]:
            print("Invalid command. Please enter a valid command.")
