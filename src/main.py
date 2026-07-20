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
    # --- Claude-generated fix ---
    # The original loop reassigned `text` on every page, so only the
    # LAST page's text survived the loop. Using a list + join keeps
    # the text from every page instead of throwing away all but one.
    pages_text = []
    for page in doc:
        pages_text.append(page.get_text())
    text = "\n".join(pages_text)
    # --- end fix ---
    return text

# --- Claude-generated function (was the TODO) ---
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
    # Basic validation so bad arguments fail loudly instead of
    # silently looping forever or returning nonsense.
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

        # Move the window forward, stepping back by `overlap`
        # characters so each new chunk repeats a bit of the
        # previous one.
        start += chunk_size - overlap

    return chunks
# --- end Claude-generated function ---

def load_model(model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
    model = SentenceTransformer(model_name, device="cpu")
    return model

def generate_embeddings(text_chunks: list[str], model: SentenceTransformer):
    embeddings = model.encode(text_chunks)

    return embeddings.tolist()

def embed_query(user_question: str, model: SentenceTransformer):
    embedding = model.encode(user_question)

    return embedding.tolist()

# --- Claude-generated function ---
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
    # Split the (chunk, vector) pairs apart: cos_sim needs a plain list
    # of vectors to compare against, and we need to keep the matching
    # chunk texts around so we can pair scores back to their chunk after.
    chunk_texts   = [chunk for chunk, _ in chunks_with_vectors]
    chunk_vectors = [vector for _, vector in chunks_with_vectors]

    # cos_sim(a, b) compares every vector in `a` against every vector in
    # `b`. Since query_vector is a single vector, the result is one row
    # containing one similarity score per chunk vector, in the same
    # order as chunk_vectors.
    similarity_scores = util.cos_sim(query_vector, chunk_vectors)[0]

    # Re-attach each chunk's text to its own score so sorting keeps
    # them together.
    chunks_with_scores = list(zip(chunk_texts, similarity_scores))

    # Highest similarity first.
    chunks_with_scores.sort(key=lambda pair: pair[1], reverse=True)

    # Keep only the top_k chunks, and drop the scores since the next
    # step (building the prompt) only needs the text itself.
    top_chunks = [chunk for chunk, _ in chunks_with_scores[:top_k]]

    return top_chunks
# --- end Claude-generated function ---

def main():
    """call other functions and make program work"""

    # load LLM model
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
        # --- Claude-generated: wire up similarity search ---
        relevant_chunks = find_relevant_chunks(query_vector, chunks_with_vectors)
        for i, chunk in enumerate(relevant_chunks, start=1):
            print(f"\n[Match {i}]\n{chunk}")
        # --- end wiring ---

if __name__ == "__main__":
    main()

