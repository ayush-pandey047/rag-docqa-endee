import logging
from typing import List, Dict, Any

from endee import Endee, Precision
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("endee_client")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

INDEX_NAME = "documents"
DIMENSION  = 384

_client = None
_index  = None

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

# def get_index():
#     global _index
#     if _index is None:
#         try:
#             _index = get_client().get_index(INDEX_NAME)
#         except Exception:
#             create_index()
#             _index = get_client().get_index(INDEX_NAME)
#     return _index

def get_client():
    global _client
    if _client is None:
        _client = Endee()
        _client.set_base_url(
            os.getenv("ENDEE_BASE_URL", "http://endee:8080") + "/api/v1"
        )
    return _client


def get_index():
    global _index
    if _index is None:
        try:
            _index = get_client().get_index(INDEX_NAME)
        except Exception:
            create_index()
            _index = get_client().get_index(INDEX_NAME)
    return _index




def upsert_vectors(chunks_with_vectors: List[Dict[str, Any]]):
    """
    Upsert chunks_with_vectors: list of {"id": str, "vector": [...], "text": str, "source": str}
    Returns the underlying client's response or raises RuntimeError on failure.
    """
    if not isinstance(chunks_with_vectors, list) or len(chunks_with_vectors) == 0:
        raise ValueError("chunks_with_vectors must be a non-empty list")

    index = get_index()

    items = []
    for idx, item in enumerate(chunks_with_vectors):
        if not isinstance(item, dict):
            raise ValueError(f"Item at position {idx} is not a dict")
        try:
            item_id = item["id"]
            vector = item["vector"]
        except KeyError as ke:
            raise ValueError(f"Missing required key {ke} in item at position {idx}") from ke

        items.append({
            "id": item_id,
            "vector": vector,
            "meta": {
                "text": item.get("text", ""),
                "source": item.get("source", "")
            }
        })

    try:
        logger.info("Upserting %d vectors into index '%s'", len(items), INDEX_NAME)
        result = index.upsert(items)
        logger.info("Upsert successful")
        return result
    except Exception as e:
        logger.exception("Index upsert failed")
        raise RuntimeError(f"Endee upsert failed: {e}") from e


def health_check():
    """Simple connectivity check to help debug 500s."""
    try:
        client = get_client()
        # Prefer a non-destructive API call; adapt if your client has a specific ping method.
        # We'll try to fetch index metadata (does not modify data).
        _ = client.get_index(INDEX_NAME)
        return {"ok": True, "detail": f"Index '{INDEX_NAME}' reachable"}
    except Exception as e:
        logger.exception("Health check failed")
        return {"ok": False, "detail": str(e)}




# # app/endee_client.py

# from endee import Endee, Precision
# import os
# from dotenv import load_dotenv

# load_dotenv()

# INDEX_NAME = "documents"
# DIMENSION  = 384

# _client = None
# _index  = None


# def get_client():
#     global _client
#     if _client is None:
#         _client = Endee()
#         _client.set_base_url(
#             os.getenv("ENDEE_BASE_URL", "http://endee:8080") + "/api/v1"
#         )
#     return _client


# def create_index():
#     client = get_client()
#     try:
#         client.create_index(
#             name=INDEX_NAME,
#             dimension=DIMENSION,
#             space_type="cosine",
#             precision=Precision.INT8
#         )
#     except Exception as e:
#         if "already exists" in str(e).lower() or "409" in str(e):
#             pass
#         else:
#             raise e


# def get_index():
#     global _index
#     if _index is None:
#         try:
#             _index = get_client().get_index(INDEX_NAME)
#         except Exception:
#             create_index()
#             _index = get_client().get_index(INDEX_NAME)
#     return _index


# def upsert_vectors(chunks_with_vectors):
#     index = get_index()
#     items = []
#     for item in chunks_with_vectors:
#         items.append({
#             "id":     item["id"],
#             "vector": item["vector"],
#             "meta": {
#                 "text":   item["text"],
#                 "source": item["source"]
#             }
#         })
#     index.upsert(items)


def search(query_vector, top_k=5):
    index = get_index()
    results = index.query(vector=query_vector, top_k=top_k)
    return results