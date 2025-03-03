# Lightning Links

Welcome to **Lightning Links**, a Python project designed to supercharge your Obsidian Zettelkasten system by providing intelligent note management and enhancement tools. This project automates processes to help you stay organized, connect ideas, and grow your knowledge base efficiently.

---

## Features

### 1. **Automatic Suggestion of Relevant Notes**
   - Lightning Links analyzes the bodies of all your notes and suggests connections (lightning links) between them.
   - Each note comes with a list of relevant notes, making it easier to visualize relationships within your Zettelkasten system.

### 2. **Gap-Filled Suggestions**
   - By examining your current focus or project, it identifies gaps in your Zettelkasten and suggests notes to fill those gaps.
   - Provides a methodical way of ensuring your knowledge is inter-connected and comprehensive.

### 3. **Automatic Note Creation**
   - Generates new notes based on related content from your existing notes.
   - These generated notes are **auto-linked** to every relevant note in your system, making them seamlessly integrated.

---

## Installation

Before starting, ensure you have Python installed on your system. Clone this repository and install the required dependencies:

```shell script
pip install -r requirements.txt
```

Dependencies include libraries like:
- **Huggingface Transformers**: For advanced natural language processing.
- **Scikit-Learn** and **NumPy**: For similarity computations.
- **OpenAI**: For note expansion based on existing content.
- Check the `requirements.txt` file for the full list of dependencies.

---

## How It Works

### Core Components:
1. **lightning_links_creator.py**:  
   - Handles the generation of links and suggestions between notes.  
   - Key functions include:
     - `find_similarities`: Finds similarities between notes' contents.
     - `extract_bodies`: Parses and extracts the main text from notes.
     - `update_notes_with_similarities`: Updates notes with computed "lightning links."

2. **note_handler.py**:  
   - Manages file handling, parsing, and formatting.  
   - Key functions include:
     - `get_all_note_names` & `load_all_markdown_files`: Manage your notes in the directory.
     - `format_inline_lighting_links`: Inserts links into the note body.
     - `save_similar_notes`: Saves generated links and suggestions into the appropriate notes.

3. **smart_assistant.py**:  
   - High-level orchestration for generating, suggesting, and expanding notes.  
   - Key functions include:
     - `create`: Automatically generates new notes based on related ones.
     - `suggest`: Provides recommendations to fill gaps in your Zettelkasten.
     - `clean_up_note_name`: Normalizes and ensures proper naming conventions for notes.

---

## Usage

1. **Prepare Your Notes**:  
   Place all your notes in the specified directory and ensure they're properly formatted in Markdown.

2. **Run Lightning Links**:
   - Use the main script to process all notes, generate suggestions, and create automatic links.
   - Suggestions and links will be embedded directly into the note bodies.

3. **Automatic Note Creation**:
   - Let the tool analyze and expand new ideas for you through its "create" function, enriching your Zettelkasten further.

---

## Example Workflow

1. **Connect Existing Notes**:
   - Lightning Links suggests:  
     `"Note A"` ↔ `"Note B"` based on the relevance of the content.

2. **Fill Gaps**:
   - When working on a research topic, Lightning Links might suggest that adding `"Note C"` could help connect `"Note X"` and `"Note Y"`.

3. **Generate New Notes**:
   - If gaps remain, Lightning Links can create `"Note D"` automatically, based on similar content from `"Note A, Note B, and Note C"`, and seamlessly link it everywhere.

---

## Contribution

Contributions are welcome! If you have an idea to improve **Lightning Links**, feel free to fork this repository, create a new branch, and submit a pull request.

### Roadmap:
- Expand note compatibility beyond Markdown.
- Integrate visualization tools for better management of Zettelkasten connections.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

Enjoy automated, smarter note management with **Lightning Links**! 🚀