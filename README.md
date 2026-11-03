# Scraper Exercise

Multithreaded CLI web scraper: crawl from a start URL, download HTML by depth, and follow links with a worker pool.

Built as a learning exercise for iterative crawling, online job queues, and thread synchronization (no busy-waiting).

## Prerequisites

- Python **3.10+**
- Network access to the sites you crawl

## Install

```bash
git clone https://github.com/danielnachumdev/scraper_ex.git
cd scraper_ex
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements/publish.txt
```

For lint/type stubs (optional):

```bash
pip install -r requirements/dev.txt
```

## Usage

### CLI

```bash
python -m scraper https://example.com/ 5 2 true
# or: python main.py https://example.com/ 5 2 true
```

| Arg | Meaning |
| --- | ------- |
| `base_url` | Start URL |
| `extract_amount` | Max links to follow from each page (positive int) |
| `max_depth` | Max crawl depth (positive int; depth `0` is the start page) |
| `unique` | Deduplicate URLs across the crawl (`true` / `false`) |

HTML is written under `./0/`, `./1/`, … by depth (gitignored). Filenames are sanitized from the URL.

### Library

```python
from scraper import Scraper, ScraperWorker, LinkExtractor

s = Scraper(
    4,  # worker threads
    ScraperWorker,
    dict(extractor_class=LinkExtractor),
)
s.scrape("https://example.com/", extract_amount=5, max_depth=2, unique=True)
```

## Notes

- Be polite: this hits live sites with retries; respect robots.txt and rate limits for any real use.
- Agent / contributor map: [`AGENTS.md`](AGENTS.md).
