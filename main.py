from sys import argv
from src import Scraper, LinkExtractor


def main() -> None:
    if len(argv) != 5:
        print("Invalid usage")
        exit(1)
    base_url, extract_amount_, max_depth_, unique_ = argv[1:]
    extract_amount = int(extract_amount_)
    max_depth = int(max_depth_)
    unique = unique_ in {"true", "True"}
    Scraper(10).scrape(base_url, extract_amount, max_depth, unique)


if __name__ == "__main__":
    main()
