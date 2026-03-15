# app/embedder.py

import requests
import os
import hashlib
import numpy as np
from dotenv import load_dotenv

load_dotenv()


def embed(text):
    # Use a simple but effective TF-IDF style embedding
    # that does not require any heavy ML libraries
    words = text.lower().split()
    vector = np.zeros(384)
    for i, word in enumerate(words):
        hash_val = int(hashlib.md5(word.encode()).hexdigest(), 16)
        idx = hash_val % 384
        vector[idx] += 1.0

    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = vector / norm

    return vector.tolist()