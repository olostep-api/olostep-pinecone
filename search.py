"""Semantic search over pages loaded by ingest.py.

Usage:
    python search.py "How do I crawl a website?"
"""

import argparse

from common import NAMESPACE, TEXT_FIELD, get_index, pinecone_client


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("query")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    index = get_index(pinecone_client())
    results = index.search(
        namespace=NAMESPACE,
        inputs={"text": args.query},
        top_k=args.top_k,
        fields=[TEXT_FIELD, "url"],
    )

    hits = results.result.hits
    if not hits:
        print("No results. Wait a few seconds after ingest.py for indexing, then retry.")
        return
    for rank, hit in enumerate(hits, 1):
        text = hit.fields[TEXT_FIELD].replace("\n", " ")
        print(f"{rank}. [{hit.score_:.3f}] {hit.fields['url']}\n   {text[:300]}...\n")


if __name__ == "__main__":
    main()
