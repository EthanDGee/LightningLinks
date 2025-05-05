from openai import OpenAI
from note_handler import FileParser
import pydantic
import os
import torch

NOTE_EXTENSION = ".md"


class SmartAssistant:
    def __init__(self, notes_directory):
        self.file_handler = FileParser(notes_directory)
        self.similar_notes = self.file_handler.load_similar_notes()

        self.model = "gpt-4o-mini"
        self.client = OpenAI(api_key=os.getenv("open_ai_key"))

    def get_core_similar_notes(self, notes):
        # a much simpler version of parse_similar() that only gets the body and file name for each note.
        similar_bodies = ""

        for note in notes:
            current_similar = self.file_handler.parse_note(f"{self.notes_directory}{note}")
            similar_bodies += f"{note}\n"
            similar_bodies += current_similar['body'] + "\n"

        return similar_bodies

    def make_open_ai_request(self, system_prompt, user_prompt, temp, response_format):
        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            temperature=temp,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=response_format,
        )

        return completion.choices[0].message.parsed

    def recommend_note(self, prompt):

        class FileName(pydantic.BaseModel):
            file_name: str

        system_prompt = (
            "You are a research assistant who's job is to suggest the most relevant file for a given prompt."
            " and return its name making sure to select one from list of files provided. ")

        all_note_names = self.file_handler.note_names
        # remove the links
        user_prompt = prompt + "\n\n\nFiles:\n" + all_note_names
        temperature = 0.1

        suggestion = self.make_open_ai_request(system_prompt, user_prompt, temperature, FileName)

        return suggestion.file_name

    def get_similar_notes_contents(self, note_name):
        """
        Parses a list of similar note files within a provided directory and generates
        a formatted string containing details such as the file name, links, tags, and
        body content of each note. This function processes the notes by leveraging
        a parsing utility from the `note_handler` module.

        :param notes: List of note file names to be parsed.
        :type notes: list[str]
        :return: A formatted string containing details of the parsed similar notes.
        :rtype: str
        """

        # add file extension so it can't be looked up, its not in list_all_note_name to prevent embedding errors.
        file_name = note_name + ".md"

        # load similar
        similar_notes = self.similar_notes[file_name]
        similar_notes.append(file_name)

        similar_notes_parsed = ""

        for note_name in similar_notes:
            current_similar = self.file_handler.parse_note(
                f"{self.file_handler.notes_directory}{note_name}{NOTE_EXTENSION}")
            similar_notes_parsed += "file_name: " + note_name + "\n"
            similar_notes_parsed += "links: " + current_similar['links'] + "\n"
            similar_notes_parsed += "tags: " + current_similar['tags'] + "\n"
            similar_notes_parsed += "body: " + current_similar['body'] + "\n"
            similar_notes_parsed += "\n"

        return similar_notes_parsed

    def create(self, prompt):
        """
        Creates a new note based on the given user prompt pulling from relevant
        existing notes in the specified directory. This function uses OpenAI's
         model to generate a structured response that adheres to the `NewFile`
         class format. The note is then saved to the  specified directory upon
         successful creation.

        :param prompt: The main user input that specifies the content or context for
            the note to be created.
        :type prompt: str
        :return: None
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
        Suggests a new note topic based on the provided directory containing existing notes and their
        metadata. The suggestion is derived by analyzing similar notes, parsed content, and the overall
        list of available notes to try and find gaps in the users obsidian zettlekasten system. Utilizes
        open AIs structured output to generate a structured response that adheres to the `ExpectedResponse`
        with data about the suggested topic and a reasoning for the suggestion.


        :return: None
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
        Provides a response to a user's query based on there notes directory by analyzing the prompt getting the most
        relevant file, and then using the similar files and the content of that file to generate a response.


        Args:
            prompt (str): The user's input or query based on which a file and response need to be suggested and
                generated.

        Raises:
            Various exceptions from OpenAI API calls if inputs or API calls fail.

        """

        reccomended_note = self.recommend_note(prompt)
        # add a file extension so it can't be looked up, its not in list_all_note_name to prevent embedding errors.
        reccomended_note = reccomended_note + ".md"

        # now we get the similar files and ask for a response based on their inputs

        system_prompt = (
            "You are a research assistant who's job is to provide a response based on the user's "
            "input using there research notes as the basis for your response. While also making "
            "sure to respond in accordance with the style of the notes you have been given. "
        )
        # get the source material

        extracted_references = self.get_similar_notes_contents(reccomended_note)

        user_prompt = prompt + "\n\n\nNotes:\n" + extracted_references

        response = self.make_open_ai_request(system_prompt, user_prompt, 0.4, "text")

        print(response)

    @staticmethod
    def clean_up_note_name(note_name):
        # returns a cleaned up note name that matches the styling convention of obsidian

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
