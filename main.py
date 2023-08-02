# sneaky way to access "module as main"'s logic without reimplementing it again
# as I envision this being used as a module that can also be called directly
from scraper.__main__ import main  # pylint: disable=import-error

if __name__ == "__main__":
    main()
