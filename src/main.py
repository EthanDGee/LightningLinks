import note_handler
from sentence_transformers import SentenceTransformer
from time import time


def find_similarities(model, sentences):
    """
    Computes the similarity scores between all pairs of given sentences using the provided model.

    Args:
        model: A pre-trained SentenceTransformer model used for encoding sentences.
        sentences (list): A list of strings representing the sentences to be compared.

    Returns:
        ndarray: A similarity matrix where each element represents the similarity between two sentences.
    """
    embedding = model.encode(sentences, max_length=256, show_progress_bar=True)

    similarities = model.similarity(embedding, embedding)
    return similarities


def find_cross_code_values():
    pass

def extract_sentences(notes_list):
    """
    Extracts the body content (sentences) from a list of notes.

    Args:
        notes_list (list): A list of dictionaries where each dictionary contains a "body" key.

    Returns:
        list: A list of strings, each representing the body content of an individual note.
    """
    notes_sentences = []

    for individual_note in notes_list:
        notes_sentences.append(individual_note["body"])

    return notes_sentences


def find_min_from_indexes(indexes, row):
    """
    given a set of indexes, find the index of the smallest value in the row

    """
    min_index = indexes[0]
    min_value = row[min_index]

    for i in range(1, len(indexes)):
        current = row[indexes[i]]
        if current < min_value:
            min_index = indexes[i]
            min_value = current

    return min_index

def get_top_n_similarities_from_row(row, num_similarities: int = 10):
    """
    Retrieves the indexes of the top n highest values in a given row.

    Args:
        row (list): A list of numeric values.
        num_similarities (int, optional): The number of top values to retrieve. Defaults to 10.

    Returns:
        list: A list of indexes corresponding to the top n highest values in the row.
    """
    # create initial top_n from 0 to n-1
    top_n_indexes = list(range(num_similarities))
    smallest_index = find_min_from_indexes(row[0:num_similarities])
    smallest_value = row[smallest_index]

    # now we iterate through the remaining entries and continually swap out the smallest entry when we find a bigger entry
    for index in range(num_similarities, len(row)):
        if row[index] > smallest_value:
            # swap out for the higher value
            top_n_indexes[smallest_index] = index
            # find new smallest
            smallest_index = find_min(row)
            smallest_value = row[smallest_index]

    return top_n_indexes


def get_all_top_n_similarities(similarities, n: int = 10):
    """
    Retrieves the top n similarity indexes for each row in a similarity matrix.

    Args:
        similarities (ndarray): A 2D array or matrix where each element represents a similarity score.
        n (int, optional): The number of top values to retrieve for each row. Defaults to 10.

    Returns:
        list: A list of lists where each sublist contains the indexes of the top n similarities for a row.
    """

    top_n_indexes_table = []

    for row in similarities:
        # find the rows top n indexes
        top_n_indexes = get_top_n_similarities_from_row(row, n)
        # add to the table
        top_n_indexes_table.append(top_n_indexes)

    return top_n_indexes_table


if __name__ == "__main__":
    start_time = time()

    print("Loading Files...", end="")
    # get files
    note_directory = "../demoData/"
    notes = note_handler.load_all_markdown_files(note_directory)
    print(f"\rFiles Loaded! {time() - start_time}")

    # get sentences
    print("Extracting Sentences...", end="")
    sentences = extract_sentences(notes)
    print(f"\rSentences Extracted! {time() - start_time}")

    # load model Source: https://huggingface.co/sentence-transformers/all-mpnet-base-v2
    print("Loading Model...", )
    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    print(f"Model Loaded! {time() - start_time}")

    # encode sentences
    print("Encoding Sentences...", end="")
    encoded_sentences = find_similarities(model, sentences)
    print(encoded_sentences)
    print(encoded_sentences.shape)
    print(type(encoded_sentences))
    print(f"\rSentences Encoded! {time() - start_time}")
    # find top n for each note
    top_n_similarities_indexes = get_all_top_n_similarities(encoded_sentences, 10)
    print(top_n_similarities_indexes)
    # rerank

    # append to file ends
