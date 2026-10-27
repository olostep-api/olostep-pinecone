"""Crawl a website with Olostep and load it into Pinecone.

Usage:
    python ingest.py https://docs.olostep.com --max-pages 20
"""

import argparse
import hashlib

from olostep import Olostep

from common import NAMESPACE, TEXT_FIELD, get_index, pinecone_client, require_env

# Pinecone accepts up to 96 records per upsert when it embeds the text itself.
UPSERT_BATCH = 90


def chunk_markdown(text: str, max_chars: int = 1500, overlap: int = 200) -> list[str]:
    """Split markdown into overlapping chunks, preferring paragraph boundaries."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks, current = [], ""
    for para in paragraphs:
        if current and len(current) + len(para) + 2 > max_chars:
            chunks.append(current)
            current = current[-overlap:] + "\n\n" + para
        else:
            current = f"{current}\n\n{para}" if current else para
        while len(current) > max_chars:
            chunks.append(current[:max_chars])
            current = current[max_chars - overlap:]
    if current:
        chunks.append(current)
    return chunks


def crawl(url: str, max_pages: int) -> list[tuple[str, str]]:
    """Crawl `url` with Olostep and return (page_url, markdown) pairs."""
    client = Olostep(api_key=require_env("OLOSTEP_API_KEY"))
    print(f"Crawling {url} (up to {max_pages} pages)...")
    job = client.crawls.create(url, max_pages=max_pages)

    pages = []
    for page in job.pages():
        result = page.retrieve(["markdown"])
        if result.markdown_content:
            pages.append((page.url, result.markdown_content))
            print(f"  {page.url}")
    return pages


def to_records(pages: list[tuple[str, str]]) -> list[dict]:
    records = []
    for url, markdown in pages:
        url_id = hashlib.sha1(url.encode()).hexdigest()[:16]
        for i, chunk in enumerate(chunk_markdown(markdown)):
            records.append({"_id": f"{url_id}#{i}", TEXT_FIELD: chunk, "url": url})
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("url", help="Website to crawl, e.g. https://docs.olostep.com")
    parser.add_argument("--max-pages", type=int, default=20)
    args = parser.parse_args()

    pages = crawl(args.url, args.max_pages)
    if not pages:
        raise SystemExit("No pages with content were returned.")

    records = to_records(pages)
    index = get_index(pinecone_client(), create=True)
    for start in range(0, len(records), UPSERT_BATCH):
        index.upsert_records(namespace=NAMESPACE, records=records[start:start + UPSERT_BATCH])

    print(f"Upserted {len(records)} chunks from {len(pages)} pages into namespace '{NAMESPACE}'.")


if __name__ == "__main__":
    main()
