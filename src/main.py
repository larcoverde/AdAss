# src/main.py

import pymupdf
from sentence_transformers import SentenceTransformer

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
        # similarity search

if __name__ == "__main__":
    main()

