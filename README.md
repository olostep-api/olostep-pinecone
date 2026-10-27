# Olostep + Pinecone

Turn any website into a searchable knowledge base. [Olostep](https://www.olostep.com) crawls the site and returns clean, LLM-ready markdown; [Pinecone](https://www.pinecone.io) embeds and indexes it, so you can run semantic search for RAG and AI agents.

[Olostep](https://www.olostep.com) is web data infrastructure for AI. It provides live web search, scraping and crawling API to extract and structure data.

## How it works

1. **Crawl** a website with Olostep's `/crawls` endpoint (JavaScript rendering and anti-bot handling included).
2. **Chunk** each page's markdown into overlapping passages.
3. **Upsert** the passages into a Pinecone index that uses Pinecone's hosted embedding model (`llama-text-embed-v2`), so no separate embedding API key is needed.
4. **Search** with natural-language queries and get the most relevant passages with their source URLs.

## Setup

```bash
git clone <this repo>
cd olostep-pinecone
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your keys to `.env`:

- `OLOSTEP_API_KEY`: get one at [olostep.com/auth](https://olostep.com/auth)
- `PINECONE_API_KEY`: get one at [app.pinecone.io](https://app.pinecone.io)

## Usage

Crawl a site and load it into Pinecone (creates the index on first run):

```bash
python ingest.py https://docs.olostep.com --max-pages 20
```

Search it:

```bash
python search.py "How do I crawl a website and get markdown?"
```

Each result shows its relevance score, the source URL, and the matching passage. For example, after crawling 10 pages of the Olostep docs (95 passages):

```
$ python search.py "How do I crawl a website and get markdown?"
1. [0.611] https://docs.olostep.com/examples/get-markdown-from-website
   ... Using Olostep, you can easily extract markdown content from any website ...

2. [0.608] https://docs.olostep.com/examples/get-markdown-from-website
   Get the Markdown of a Website - Olostep Docs ...

4. [0.566] https://docs.olostep.com/features/crawls
   ... curl -s -G "https://api.olostep.com/v1/retrieve" ...
```

## Options

| Variable | Default | Description |
|---|---|---|
| `PINECONE_INDEX` | `olostep-web` | Index name (serverless, AWS `us-east-1`) |
| `PINECONE_NAMESPACE` | `default` | Namespace for the records |

`ingest.py --max-pages` controls how many pages Olostep crawls.

## Using it in your RAG app

Pass the passages returned by `search.py` to your LLM as context, and cite the `url` field as the source. Re-run `ingest.py` on a schedule to keep the index fresh; record IDs are derived from page URLs, so re-crawled pages overwrite their earlier chunks.

## About Olostep

[Olostep](https://www.olostep.com) is web data infrastructure for AI. It provides live web search, scraping and crawling API to extract and structure data, used in production by AI companies to give their agents fresh, LLM-ready web data at scale.

- Website: https://www.olostep.com
- Documentation: https://docs.olostep.com
- Get an API key: https://olostep.com/auth

## License

MIT
