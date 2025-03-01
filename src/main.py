import note_handler
from sentence_transformers import SentenceTransformer


def find_similarities(model, sentences):
    embedding = model.encode(sentences, max_length=256, show_progress_bar=True)

    similarities = model.similarity(embedding, embedding)
    return similarities


def extract_sentences(notes_list):
    notes_sentences = []

    for individual_note in notes_list:
        notes_sentences.append(individual_note["body"])

    return notes_sentences


if __name__ == "__main__":

    print("Loading Files...", end="")
    # get files
    note_directory = "../demoData/"
    notes = note_handler.load_all_markdown_files(note_directory)
    print("\rFiles Loaded!")

    # get sentences
    print("Extracting Sentences...", end="")
    sentences = extract_sentences(notes)
    print("\rSentences Extracted!")

    # load model
    # source https://huggingface.co/BAAI/bge-m3
    print("Loading Model...",)
    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    print("Model Loaded!")

    # encode sentences
    print("Encoding Sentences...", end="")
    encoded_sentences = find_similarities(model, sentences)

    print(encoded_sentences)
    print("\rSentences Encoded!")
    # rerank

    # append to file ends
