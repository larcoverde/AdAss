# src/main.py

import pymupdf
from sentence_transformers import SentenceTransformer, util

def open_file():
    """Request a PDF file from user and open it."""
    filename = input("Enter file: ")
    doc = pymupdf.open(filename)
    return doc

def get_text_from_page(doc):
    """Extract text from provided PDF file."""
    pages_text = []
    for page in doc:
        pages_text.append(page.get_text())
    text = "\n".join(pages_text)
    return text

def chunk_text(text, chunk_size=500, overlap=50):
    """
    Split text into overlapping chunks.

    Args:
        text (str): the full text to split.
        chunk_size (int): number of characters per chunk.
        overlap (int): number of characters shared between
            consecutive chunks (so context isn't lost at the
            edges of a chunk when it's later fed to an AI model).

    Returns:
        list[str]: the text split into overlapping chunks.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if overlap < 0:
        raise ValueError("overlap must be 0 or greater")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)

        # Step back by `overlap` so each new chunk repeats a bit of the
        # previous one.
        start += chunk_size - overlap

    return chunks

def load_model(model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
    model = SentenceTransformer(model_name, device="cpu")
    return model

def generate_embeddings(text_chunks: list[str], model: SentenceTransformer):
    embeddings = model.encode(text_chunks)

    return embeddings.tolist()

def embed_query(user_question: str, model: SentenceTransformer):
    embedding = model.encode(user_question)

    return embedding.tolist()

def find_relevant_chunks(query_vector: list[float], chunks_with_vectors: list[tuple[str, list[float]]], top_k: int = 3):
    """
    Find the chunks most similar to the query using cosine similarity.

    Args:
        query_vector (list[float]): embedding of the user's question.
        chunks_with_vectors (list[tuple[str, list[float]]]): pairs of
            (chunk_text, chunk_embedding), as produced in main().
        top_k (int): how many top-matching chunks to return.

    Returns:
        list[str]: the top_k chunk texts, ordered from most to least
            relevant.
    """
    chunk_texts   = [chunk for chunk, _ in chunks_with_vectors]
    chunk_vectors = [vector for _, vector in chunks_with_vectors]

    # cos_sim returns a matrix; [0] grabs the one row of scores since
    # there's only a single query vector.
    similarity_scores = util.cos_sim(query_vector, chunk_vectors)[0]

    chunks_with_scores = list(zip(chunk_texts, similarity_scores))
    chunks_with_scores.sort(key=lambda pair: pair[1], reverse=True)
    top_chunks = [chunk for chunk, _ in chunks_with_scores[:top_k]]

    return top_chunks

def main():
    """call other functions and make program work"""

    # load embedding model
    model               = load_model()

    # get pdf and chunk its text
    doc                 = open_file()
    text                = get_text_from_page(doc)
    chunks              = chunk_text(text)
    vectors             = generate_embeddings(chunks, model)
    chunks_with_vectors = list(zip(chunks, vectors))

    # user question loop
    while True:
        user_question = input("-> ")
        if user_question.lower().strip() == "exit":
            print("Exiting...")
            break
        query_vector = embed_query(user_question, model)
        relevant_chunks = find_relevant_chunks(query_vector, chunks_with_vectors)
        for i, chunk in enumerate(relevant_chunks, start=1):
            print(f"\n[Match {i}]\n{chunk}")

if __name__ == "__main__":
    main()

