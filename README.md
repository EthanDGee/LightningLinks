# Lightning Links

Welcome to **Lightning Links**, a Python project crafted to enhance and assist your Obsidian Zettelkasten system by
intelligently managing your notes. This tool automates the connection of similar ideas, helps fill gaps in your
knowledge base, and even generates new notes that are based on your notes—all while keeping your Zettelkasten clean and
efficient.

---

## Features

### 1. **Automatic Addition of Relevant Notes**

- For every note in your system, Lightning Links analyzes its content and automatically appends a section of relevant
  notes to the bottom of every note.
- No manual effort needed in connecting ideas—it’s all done for you.
- Feel like the links are a bit out of date? Simply re-run the linker, and it will readjust to reflect your changes

### 2. **Gap-Filled Suggestions**

- Considers what you're currently working on and suggests additional notes that may fill important gaps in your
  Zettelkasten.
- All based on what you're currently working on, and what you've already done.
- Helps to ensure your ideas and knowledge are as comprehensive as possible.
- Don't want to waste your time manually writing the note it suggested? No problem, the smart assistant can create the
  note for you, all based upon your other notes, it will even link up the note for you.

### 3. **Smart Note Creation**

- To lazy to right a note on a topic you've already have covered too many times, but are just too busy to get around to
  writing it? Have the smart assistant write that note for you, it will even do all the connections for you.

    - **Automatically appended** with links to related notes.
    - **Based on you**, created with your notes in mind.
    - **Written like you**, it already knows your writing tendencies, and matches them effortlessly, saving you the
      hassle of having to go back and change things.
    - **Expanded upon intelligently**, forging connections and helping grow your Zettelkasten repository.

---

## Set Up

To get started, ensure you have Python installed. Follow these steps:

1. Clone the repository to your local machine:

```shell script
git clone https://github.com/your-repo/lightning-links.git
   cd lightning-links
```

2. Install the project dependencies:

```shell script
pip install -r requirements.txt
```

3. Set up Hugging Face:
    - Create an account on [Hugging Face](https://huggingface.co/) if you don't already have one.
    - Obtain your API token by navigating to your account settings -> Access Tokens and clicking "New Token".
    - Copy the token and save it for later use.
    - Configure your system to use the token by running the following command in the terminal:
      ```shell
      huggingface-cli login
      ```
    - Paste your API token when prompted. If the login is successful, the CLI will confirm that your token has been
      saved locally. This allows the application to leverage Hugging Face's models and APIs seamlessly.

4. Add the OpenAI API key (optional):
    - If you want to use OpenAI for note generation, and suggestion, obtain an API key from [OpenAI](https://platform.openai.com/).
    - Once you have the key, create a `.env` file in the project directory and add the following line:
      ```
      OPENAI_API_KEY=your_openai_api_key
      ```
    - Replace `your_openai_api_key` with the key you received from OpenAI.

---

## How It Works

### Lightning Link Connector:

1. **Parse notes**:
    - Looks through all your notes and only grabs the most important data.

2. **Analyze Similarities**:
    - Embeds your notes using sentence transformers to find out what you're really talking about.
    - Using algorithms based on Natural Language Processing (NLP), Lightning Links then determines the most relevant
      notes
      for each file, and saves it to your `.obsidian` folder so the smart assistant doesn't need to reindex them. By default this is set to 10, but you can do more, for higher accuracy at the cost of higher api usage fees. To customize look at Advanced Use

3. **Append Relevant Links**:
    - A "Lightning links section" section is then appended at the **bottom** of every note, making it easy to see which
      ideas connect.
    - It only appends the most 3 relevant links to the end of your notes.
    - Are three notes just not enough? Look at advanced use to customize it.
    - 

---

#### This is an example note, I'm sure yours are far better.

Lorem exampleum noteum, craftedum to exemplify the greatness of your own brilliantum ideas. Althoughum this ipsum serves its purposum here, your notes undoubtedlyus surpass this one in insightum, creativitatis, and relevanceum. Humanus ingenuity shall triumphet always.

### Lightning Links
[[ZettleKasten Explained]]    [[Too many notes not enough time]]     [[Second Brain, Second Life]]

---

### Smart Assistant

1. **Suggest Missing Links**:  The system identifies knowledge gaps and surfaces notes you may not have thought to connect with your current
      work.
   1. Looks at your current workspace and pulls relevant notes.
   2. Those notes are then parsed, and there main ideas are extracted so that open AI can see what you've been writing about.
   3. Takes a snapshot of your overall zettlekasten notes.
   4. Ships it off to open ai to look for gaps in your system.
   5. Suggests a relevant note, as well as the reasoning as to why it might be helpful to add to your zettle kasten.
   6. Asks you if you want the smart assistant to automagically add it to your notes for you.

2. **Generate Notes**: Based on the content of existing notes, Lightning Links can automatically generate fully linked, expanded notes.
      1. Asks you for what you want
      2. Pulls the relevant data from what you're working on.
      3. Ships it off to open ai to generate the content based on your notes, styling, and more.
      4. Formats the data, links it to your other notes, and adds it to your zettlekasten.
---

## Usage

### Lightning Links Creator

The **Lightning Links Creator** can be run quickly and easily. Just follow these steps:

1. **Ensure Setup is Complete**

- Make sure you've followed all steps in the **Set Up** section (e.g., installed dependencies, configured API keys).

2. Navigate to the `src/` directory within the project directory in your terminal

``` bash
  cd src/
```

3. **Run the Creator Script**

- Use the following command to run the script in its simplest form:

``` bash
   python lightning_links_creator.py
```

4. **Enter in your notes directory**

- You will be prompted to enter a directory, this will be directory with in which you have all `.md` files in your
  obsidian project
- Hit enter, and sit back and relax as all your notes, are automagically connected.
- By default, it will add the 3 most relevant notes to each file, as well as save the top 10 most relevant for smart
  assistant usage.

5: Advanced Usage (Optional)

- For advanced users you can cut away the prompting sections, and customize your smart links by adding arguments in the
  following order
- The more top connections you have the more accurate your assistant usage will be, but it will also be more expensive,
  and can lead to slower response times in the extreme cases.

```bash 
 python lightning_links_creator.py [directory] [number of top connections to save] [number of links to add]
```

Example

```bash 
 python lightning_links_creator.py myNotes/ 25 10
```

### Smart Assistant (Zeus)

1. **Ensure Setup is Complete**

- Make sure you've followed all steps in the **Set Up** section (e.g., installed dependencies, configured API keys).
- This does require lightning links to have been created, as it does pull from the relevant notes section to have
  accurate data.

2. **Check Your Notes**:

- After processing, each note will have a "Lighting Links" section appended to its bottom, listing links to other
  related notes.

3. Navigate to the `src/` directory within the project directory in your terminal

``` bash
  cd src/
```

4. **Run the Creator Script**

- Use the following command to run the script in its simplest form:

``` bash
   python smart_assistant.py
```

4. **Enter in your notes directory**

- You will be prompted to enter a directory, this will be directory with in which you have all `.md` files in your
  obsidian project
- Hit enter, and sit back and wait for the assistant to load. It is just fetching the reference list of all top
  connections for each note

5. **Available Commands**
   Once the program starts, you can choose one of the following commands:
    - **`s: Suggest`**
      This analyzes your recent notes and suggests a new topic you might want to consider adding to your collection.
    With the option to automatically add a note on the topic to your notes. 
    - **`c: Create`**
      This creates a new note based on a topic you specify. Simply follow the prompt to enter your desired topic, and
      the tool will intelligently generate a new note for you.
    - **`q: Quit`**
      Use this to exit the tool

---


## Contribution

Contributions are welcome! If you'd like to enhance Lightning Links, feel free to fork the repository, create your
branch, and open a pull request.

### Roadmap:

- Port the Project to an Obsidian Plugin for ease of use. 
- Expand notes compatibility (e.g., plain text files or other formats beyond Markdown).
- Allowing for people that use the folder system within obsidian for advanced organization
- 
---

### HACKUSU

This project was made over the course of 18 hours for the [HackUSU 25](https://huntsman.usu.edu/hackusu/)
## License

This project is licensed under the MIT License. Please refer to the `LICENSE` file for more details.

---

Take your note-taking to the next level with **Lightning Links**! Let the automation connect your ideas, suggest new
ones, and grow your Zettelkasten seamlessly! 🚀

--- 

Let me know if you'd like further refinements! 😊