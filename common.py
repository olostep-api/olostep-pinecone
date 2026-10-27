"""Shared setup for the Olostep + Pinecone example."""

import os
import sys

from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

# Identifies traffic from this integration to Pinecone.
# https://docs.pinecone.io/integrations/build-integration/attribute-usage-to-your-integration
SOURCE_TAG = "olostep"

INDEX_NAME = os.getenv("PINECONE_INDEX", "olostep-web")
NAMESPACE = os.getenv("PINECONE_NAMESPACE", "default")

# Pinecone hosts the embedding model, so no separate embedding API key is needed.
EMBED_MODEL = "llama-text-embed-v2"
TEXT_FIELD = "chunk_text"


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        sys.exit(f"Missing {name}. Copy .env.example to .env and set it.")
    return value


def pinecone_client() -> Pinecone:
    return Pinecone(api_key=require_env("PINECONE_API_KEY"), source_tag=SOURCE_TAG)


def get_index(pc: Pinecone, create: bool = False):
    """Return the index, creating it with Pinecone's hosted embedding model if asked."""
    if not pc.has_index(INDEX_NAME):
        if not create:
            sys.exit(f"Index '{INDEX_NAME}' not found. Run ingest.py first.")
        pc.create_index_for_model(
            name=INDEX_NAME,
            cloud="aws",
            region="us-east-1",
            embed={"model": EMBED_MODEL, "field_map": {"text": TEXT_FIELD}},
        )
    return pc.Index(host=pc.describe_index(INDEX_NAME).host)
