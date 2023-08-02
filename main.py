from sys import argv
from src import LinkExtractor


def main() -> None:
    base_url, extract_amount, max_depth, unique = argv[1:]
    p = LinkExtractor(base_url)
    for link in p:
        print(link)


if __name__ == "__main__":
    main()
