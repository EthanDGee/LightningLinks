import note_handler
from sentence_transformers import SentenceTransformer
from time import time
import os

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


def find_min_of_indexes(indexes, row):
    """
    given a set of indexes, find the index of the smallest value in the row, as well as the index of the index in the indexes array

    """
    min_index = indexes[0]
    index_of_min_index = 0
    min_value = row[min_index]

    for i in range(1, len(indexes)):
        current = row[indexes[i]]
        if current < min_value:
            min_index = indexes[i]
            index_of_min_index = i
            min_value = current

    return min_index, index_of_min_index


def get_top_n_similarities_from_row(row, num_similarities: int = 10):
    """
    Retrieves the indexes of the top n highest values in a given row.

    Args:
        row (list): A list of numeric values.
        num_similarities (int, optional): The number of top values to retrieve. Defaults to 10.

    Returns:
        list: A list of indexes corresponding to the top n highest values in the row.
    """

    if num_similarities >= len(row):
        return list(range(0, len(row)))

    if num_similarities == 0:
        return []

    # create initial top_n from 0 to n-1
    top_n_indexes = list(range(num_similarities))
    # we need both indexes, so we can find the smallest index in the row array, and the index of smallest index so we know which of the top_n to swap

    smallest_index, index_of_smallest_index = find_min_of_indexes(top_n_indexes, row)
    smallest_value = row[smallest_index]

    # now we iterate through the remaining entries and continually swap out the smallest entry when we find a bigger entry
    for index in range(num_similarities, len(row)):
        if row[index] > smallest_value:
            # swap out for the higher value
            top_n_indexes[index_of_smallest_index] = index
            # find new smallest
            smallest_index, index_of_smallest_index = find_min_of_indexes(top_n_indexes, row)
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

    for row_id in range(len(similarities)):
        # find the rows top n indexes
        row = similarities[row_id]
        top_n_indexes = get_top_n_similarities_from_row(row, n)
        # add to the table
        top_n_indexes_table.append(top_n_indexes)

    return top_n_indexes_table


if __name__ == "__main__":

    arguments = os.sys.argv

    # get directory

    # argument mode
    if len(arguments) > 1:
        # arguments are to be passed in as
        # python lightning_links_creator.py [dir]
        note_directory = arguments[1]

    else:
        # get directory from user manually
        while True:
            note_directory = input("Enter the directory path: ")
            if not os.path.isdir(note_directory):
                print("Error: The provided path is not a valid directory. Please try again.")
            else:
                break

    # number of similar notes

    if len(arguments) > 2:
        similar_count = int(arguments[2])
    else:
        similar_count = 10

    # count lightning links

    if len(arguments) > 3:
        lightning_links_count = int(arguments[3])
    else:
        lightning_links_count = 3


    # Ensure correct formatting
    note_handler.ensure_trailing_empty_line(note_directory)


    start_time = time()
    print("Loading Files...", end="")
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
    print(f"\rSentences Encoded! {time() - start_time}")
    # find top n for each note
    print("Finding Top N Similarities...", end="")
    top_n_similarities_indexes = get_all_top_n_similarities(encoded_sentences, similar_count)
    print(f"\rTop N Similarities Found! {time() - start_time}")
    print("Updating Lighting Links...", end="")
    # append to file ends
    for i in range(len(top_n_similarities_indexes)):
        file_names = []
        notes[i]["similar_notes"] = []

        for similarity_index in top_n_similarities_indexes[i]:
            notes[i]["similar_notes"].append(notes[similarity_index]["file_name"])


        note_handler.write_to_file(note_directory, notes[i], lightning_links_count)

    print(f"\rLightning Links Updated! {time() - start_time}")
    print("Saving Similarities...", end="")
    notes = note_handler.save_similar_notes(note_directory, notes)
    print(f"\rSimilarities Saved! { time() - start_time}")
    print(f"Files Updated! {time() - start_time}")

