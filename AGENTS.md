# Scraper Exercise – Agent Context

Implementation guide for coding agents changing **scraper_ex**. Product pitch and user-facing install/run: [`README.md`](README.md).

---

## Orientation

| Question | Answer |
| -------- | ------ |
| What is this? | Multithreaded **CLI / library** web-scraper exercise (BFS-style crawl by depth) |
| Importable code | `scraper/` — also runnable via `python -m scraper` / root `main.py` |
| Toolchain | pip + `requirements/publish.txt` (runtime) · `requirements/dev.txt` (pylint, mypy, stubs) |
| Python | **3.10+** (README); no `pyproject.toml` / lockfile yet |
| Tests | No `tests/` tree today — **do not invent a delete policy**; add tests under `tests/` if introducing them |
| Secrets | Never commit API keys, cookies, or live credentials; do not scrape behind auth in committed examples |

```text
.
├── main.py                 # Thin shim → scraper.__main__.main
├── scraper/
│   ├── __main__.py         # argparse CLI; sets NUM_THREADS / Extractor.RETRIES / TIMEOUT
│   ├── scraper.py          # Scraper facade: depth dirs + WorkerPool + shared unique set
│   ├── extractors/         # Extractor ABC + LinkExtractor (requests + BeautifulSoup)
│   ├── workers/            # Worker ABC, WorkerPool, ScraperWorker
│   └── utils/              # LinkWrapper, URL helpers, timeout helper
├── requirements/
│   ├── publish.txt         # requests, beautifulsoup4, validators
│   └── dev.txt             # pylint, mypy, stubs + runtime deps
├── Makefile                # `clean` removes ./0 .. ./3 scrape output dirs
├── mypy.ini / .pylintrc
├── README.md               # Marketing / user docs
└── AGENTS.md               # This file
```

No `.github/workflows` in-tree yet. Shared CI templates live in [`danielnachumdev/actions`](https://github.com/danielnachumdev/actions) ([`HOW-TO-USE.md`](https://github.com/danielnachumdev/actions/blob/v1/HOW-TO-USE.md)). Prefer adopting thin CI there over vendoring workflow bodies. Repo already has semver labels (`noBump` / `bumpPatch` / …).

---

## Develop

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements/publish.txt
# optional:
pip install -r requirements/dev.txt
```

| Task | Command |
| ---- | ------- |
| Run CLI | `python -m scraper <base_url> <extract_amount> <max_depth> <unique>` |
| Alt entry | `python main.py …` (re-exports `__main__.main`) |
| Types | `mypy` (see `mypy.ini`; `files = *.py` is narrow — package may need path tweaks) |
| Lint | `pylint` per `.pylintrc` |
| Clean scrape dirs | `make clean` (removes `0/`–`3/` only) |

### Dependencies

- **Runtime (`requirements/publish.txt`):** `requests`, `beautifulsoup4`, `validators`
- **Dev (`requirements/dev.txt`):** above + `pylint`, `mypy`, `types-requests`, `types-beautifulsoup4`
- Prefer editing the requirements files; there is no lockfile — pin carefully if tightening versions.

---

## Code style & domain notes

- **Dual import style:** many modules branch on `len(__name__.split("."))` so they work both as package imports and when run with path hacks. Preserve that pattern unless you deliberately normalize to package-only imports and update `__main__` / docs together.
- **Public surface** (`scraper/__init__.py`): `Scraper`, `ScraperWorker`, `Worker`, `WorkerPool`, `LinkExtractor`, `Extractor`.
- **Architecture:** `Scraper.scrape` creates `./{depth}/` dirs, builds a `WorkerPool` with shared `unique_set` + `Lock`, submits `LinkWrapper(base_url, 0)`, then `pool.start()`. Workers pull via `Semaphore` + `Queue` (no busy-wait).
- **`ScraperWorker`:** downloads via `extractor_class`, writes `./{depth}/{encode_url_to_filename(url)}.html`, then enqueues child links up to `extract_amount` / `max_depth`, optionally under `unique_set_lock`.
- **`encode_url_to_filename`:** strips the first **8** characters (assumes `https://`). HTTP or other schemes can produce odd filenames — fix carefully if generalizing.
- **CLI knobs not on argparse:** `NUM_THREADS` (default `10`), `Extractor.RETRIES` (`5`), `Extractor.TIMEOUT` (`1`) are module-level in `__main__.py`.
- **`boolean` CLI parser:** only `"True"`, `"true"`, `"T"`, `"t"` count as true; anything else is false.
- Output dirs `0/`–`N/` are gitignored for `0/`–`3/`; deeper crawls may leave unignored folders — prefer extending ignore patterns if raising default depths.
- Typo in `utils/__init__.py`: `__alL__` (capital L) — fix if touching exports; do not “fix” unrelated modules in the same PR unless asked.

---

## PRs, CI, and releases

1. Branch off `main`; open a PR into `main`.
2. Attach **exactly one** semver label: `noBump` | `bumpPatch` | `bumpMinor` | `bumpMajor`.
3. Docs-only / chore PRs use **`noBump`**.
4. No thin CI/CD workflows in this repo yet — do not invent a full release/PyPI pipeline unless requested; change shared behavior in **`danielnachumdev/actions`**.
5. Prefer check names **`CI / CI`** and **`Semver / Semver`** once thin workflows are adopted.

---

## Sensitive / ignored

Do not commit: `.venv/`, `venv/`, scrape output dirs (`0/`…), `__pycache__/`, secrets, or real auth cookies. Respect `.gitignore`.
