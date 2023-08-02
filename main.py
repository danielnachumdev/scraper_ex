# sneaky way to access "module as main"'s logic without reimplementing it again
# as I envision this being used as a module that can also be called directly
from Scraper.__main__ import main

if __name__ == "__main__":
    main()
