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


def extract_bodies(notes_list):
    """
    Extracts the "body" content from each individual note in the provided list.

    This function processes a list of notes, each represented as a dictionary,
    and retrieves the value associated with the "body" key. It compiles and
    returns a list of all these "body" contents. The function assumes that
    every dictionary in the list contains a "body" key.

    :param notes_list: List of dictionaries where each dictionary represents a note
        and contains a "body" key with its associated content.
    :type notes_list: list[dict]
    :return: List of "body" contents extracted from the input dictionaries.
    :rtype: list[str]
    """
    notes_sentences = []

    for individual_note in notes_list:
        notes_sentences.append(individual_note["body"])

    return notes_sentences


def find_min_of_indexes(indexes, row):
    """
    Finds the minimum value among specified indexes in a given row and returns the
    index corresponding to the minimum value, along with its position in the
    indexes list.

    The function iterates through the provided indexes, compares their corresponding
    values in the row, and identifies the index with the smallest value. Additionally,
    it identifies the position in the original `indexes` list of this minimum index.

    :param indexes: A list of integers representing the indices to check in the row.
    :param row: A list of numerical values representing the row to search within.
    :return: A tuple containing:
        - The index in the row corresponding to the minimum value (first element),
        - The position of the minimum index in the input `indexes` list (second element).
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
    Retrieves the indexes of the top 'num_similarities' of highest values in a given row.

    Args:
        row (list): A list of numeric values.
        num_similarities (int, optional): The number of top values to retrieve. Defaults to 10.

    Returns:
        list: A list of indexes corresponding to the top 'num_similarities' of the highest values in the row.
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
    note_handler.ensure_proper_endings(note_directory)


    start_time = time()
    print("Loading Files...", end="")
    notes = note_handler.load_all_markdown_files(note_directory)
    print(f"\rFiles Loaded! {time() - start_time}")



    # get sentences
    print("Extracting Sentences...", end="")
    sentences = extract_bodies(notes)
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

