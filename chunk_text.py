# Stage 2: chunk_text - splits raw text into overlapping pieces.
# Pipeline order: document.py -> chunk_text.py -> embed.py -> ingest.py -> retrieval.py

def chunk_text(text, chunk_size, overlap):
    start = 0
    chunks = []
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        # Step forward by less than a full chunk_size so the last
        # `overlap` characters repeat in the next chunk. Without this,
        # a sentence sitting on a boundary gets split and loses meaning.
        start = start + chunk_size - overlap
    return chunks


if __name__ == "__main__":
    result = chunk_text("abcdefghijklmnopqrstuvwxyz", 10, 3)
    print(result)
