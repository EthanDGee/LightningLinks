import note_handler
from sentence_transformers import SentenceTransformer


def find_similar_sentences(model, sentences):
    embedding = model.encode(sentences)

    similarities = model.similarity(embedding, embedding)
    return similarities

def extract_sentences(notes_list):





if __name__ == "__main__":
    # get files
    note_directory = "../demoData/"
    notes = note_handler.get_all_markdown_files(note_directory)
    # get sentences



    # load model
    # source https://huggingface.co/BAAI/bge-m3
    model = SentenceTransformer('BAAI/bge-m3')

    # encode sentences

    # rerank

    # append to file ends
