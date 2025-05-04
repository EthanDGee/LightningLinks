import numpy as np
from note_handler import FileParser
from sentence_transformers import SentenceTransformer
from time import time
import os


class LightningLinksCreator:
    def __init__(self, vault_path, num_lightning_links: int = 3, num_similar_notes: int = 10):
        self.model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
        self.file_handler = FileParser(vault_path)
        self.num_lightning_links = num_lightning_links
        self.num_similar_notes = num_similar_notes

    def find_similarities(self, sentences):
        """
        Computes the similarity scores between all pairs of given sentences using the provided model.

        Args:
            sentences (list): A list of strings representing the sentences to be compared.

        Returns:
            ndarray: A similarity matrix where each element represents the similarity between two sentences.
        """
        embedding = self.model.encode(sentences, show_progress_bar=True)

        similarities = self.model.similarity(embedding, embedding)
        return similarities

    def extract_bodies(self, notes_list):
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

    def get_top_n_similarities_from_row(self, row):
        """
        Retrieves the indexes of the top 'num_similarities' of highest values in a given row.

        Args:
            row (list): A list of numeric values.

        Returns:
            list: A list of indexes corresponding to the top 'num_similarities' of the highest values in the row.
        """

        if self.num_similar_notes >= len(row):
            return list(range(0, len(row)))

        if self.num_similar_notes == 0:
            return []
        #
        # # create initial top_n from 0 to n-1
        # top_n_indexes = list(range(num_similarities))
        # # we need both indexes, so we can find the smallest index in the row array, and the index of smallest index so we know which of the top_n to swap
        #
        # smallest_index, index_of_smallest_index = find_min_of_indexes(top_n_indexes, row)
        # smallest_value = row[smallest_index]
        #
        # # now we iterate through the remaining entries and continually swap out the smallest entry when we find a bigger entry
        # for index in range(num_similarities, len(row)):
        #     if row[index] > smallest_value:
        #         # swap out for the higher value
        #         top_n_indexes[index_of_smallest_index] = index
        #         # find new smallest
        #         smallest_index, index_of_smallest_index = find_min_of_indexes(top_n_indexes, row)
        #         smallest_value = row[smallest_index]

        top_n_indexes = np.argsort(row)[::-1][1:self.num_similar_notes + 1]

        return top_n_indexes

    def get_all_top_n_similarities(self, similarities):
        """
        Retrieves the top n similarity indexes for each row in a similarity matrix.

        Args:
            similarities (ndarray): A 2D array or matrix where each element represents a similarity score.

        Returns:
            list: A list of lists where each sublist contains the indexes of the top n similarities for a row.
        """

        top_n_indexes_table = []

        for row_id in range(len(similarities)):
            # find the rows top n indexes
            row = similarities[row_id]
            top_n_indexes = self.get_top_n_similarities_from_row(row.numpy())
            # add to the table
            top_n_indexes_table.append(top_n_indexes)

        return top_n_indexes_table

    def update_notes_with_similarities(self, notes, top_n_similarities_indexes):
        """Update notes with top N similarities and save them."""
        for i, similarity_indexes in enumerate(top_n_similarities_indexes):
            notes[i]["similar_notes"] = [notes[sim_idx]["file_name"] for sim_idx in similarity_indexes]
            self.file_handler.write_to_file(notes[i], self.num_lightning_links)

    def refresh_similarities(self):
        """Re-compute similarities and update notes."""
        # Ensure correct formatting
        self.file_handler.ensure_proper_endings()

        start_time = time()
        print("Loading Files...", end="")
        notes = self.file_handler.load_all_note_files()
        print(f"\rFiles Loaded! {time() - start_time}")

        # get sentences
        print("Extracting Sentences...", end="")
        bodies = self.extract_bodies(notes)
        print(f"\rSentences Extracted! {time() - start_time}")

        # load model Source: https://huggingface.co/sentence-transformers/all-mpnet-base-v2
        print("Loading Model...", )
        model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
        print(f"Model Loaded! {time() - start_time}")

        # encode sentences
        print("Encoding Sentences...", end="")
        encoded_sentences = self.find_similarities(bodies)
        print(f"\rSentences Encoded! {time() - start_time}")
        # find top n for each note
        print("Finding Top N Similarities...", end="")
        top_n_similarities_indexes = self.get_all_top_n_similarities(encoded_sentences)
        print(f"\rTop N Similarities Found! {time() - start_time}")
        print("Updating Lighting Links...", end="")
        # append to file ends

        self.update_notes_with_similarities(notes, top_n_similarities_indexes)

        print(f"\rLightning Links Updated! {time() - start_time}")
        print("Saving Similarities...", end="")
        self.file_handler.save_similar_notes(notes)
        print(f"\rSimilarities Saved! {time() - start_time}")
        print(f"Files Updated! {time() - start_time}")


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

    file_handler = FileParser(note_directory)
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

    creator = LightningLinksCreator(note_directory, num_lightning_links=lightning_links_count,
                                    num_similar_notes=similar_count)
    creator.refresh_similarities()
