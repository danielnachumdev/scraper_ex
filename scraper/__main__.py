import argparse
if __name__ == "__main__":
    from scraper import Scraper  # type:ignore # pylint: disable=import-error # noqa
    from link_extractor import LinkExtractor  # type:ignore # pylint: disable=import-error # noqa
else:
    from .scraper import Scraper
    from .link_extractor import LinkExtractor

# arbitrary chosen values that can be added to CLI but it is not in the definitions
NUM_THREADS: int = 10
LinkExtractor.RETRIES = 5
LinkExtractor.TIMEOUT = 1


def positive_integer(value: str) -> int:
    """a function that will parse a value into a positive integer
    """
    try:
        num = int(value)
        if num <= 0:
            raise argparse.ArgumentTypeError(
                f"{value} is not a positive integer")
        return num
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value} is not a valid integer")  # pylint: disable=raise-missing-from # noqa


def string(value: str) -> str:
    """a function that will parse value to string
    """
    return value


def boolean(value: str) -> bool:
    """a function that will parse a value to boolean
    """
    return value in {"True", "true", "T", "t"}


def main() -> None:
    """main entry point for program logic
    """

    parser = argparse.ArgumentParser(
        description="CLI Input Validation Example")
    # base_url, extract_amount_, max_depth_, unique_
    parser.add_argument("base_url", type=string, help="string help")
    parser.add_argument("extract_amount", type=positive_integer,
                        help="A positive integer input")
    parser.add_argument("max_depth", type=positive_integer,
                        help="A positive integer input")
    parser.add_argument("unique", type=boolean,
                        help="A boolean")

    args = parser.parse_args()
    Scraper(NUM_THREADS).scrape(args.base_url,
                                args.extract_amount, args.max_depth, args.unique)


if __name__ == "__main__":
    main()