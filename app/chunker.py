def chunk_text(text, source_name="document", chunk_size=300, overlap=50):
    words = text.split()
    chunks = []
    start = 0
    index = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)

        chunks.append({
            "id": f"{source_name}_chunk_{index}",
            "text": chunk_text,
            "source": source_name
        })

        index += 1
        start += chunk_size - overlap

    return chunks