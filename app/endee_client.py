# app/endee_client.py

from endee import Endee, Precision
import os
from dotenv import load_dotenv

load_dotenv()

INDEX_NAME  = "documents"
DIMENSION   = 384

_client = None
_index  = None


def get_client():
    global _client
    if _client is None:
        _client = Endee()
        _client.set_base_url(
            os.getenv("ENDEE_BASE_URL", "http://endee:8080") + "/api/v1"
        )
    return _client


def create_index():
    client = get_client()
    try:
        client.create_index(
            name=INDEX_NAME,
            dimension=DIMENSION,
            space_type="cosine",
            precision=Precision.INT8
        )
    except Exception as e:
        if "already exists" in str(e).lower() or "409" in str(e):
            pass
        else:
            raise e


def get_index():
    global _index
    if _index is None:
        _index = get_client().get_index(INDEX_NAME)
    return _index


def upsert_vectors(chunks_with_vectors):
    index = get_index()
    items = []
    for item in chunks_with_vectors:
        items.append({
            "id":     item["id"],
            "vector": item["vector"],
            "meta": {
                "text":   item["text"],
                "source": item["source"]
            }
        })
    index.upsert(items)


def search(query_vector, top_k=5):
    index = get_index()
    results = index.query(vector=query_vector, top_k=top_k)
    return results