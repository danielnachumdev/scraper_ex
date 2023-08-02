# Scraper Exercise

This code provides an example of a Command Line Interface (CLI) tool for web scraping with input validation. The program uses Python and allows users to provide input arguments through the command line to control the web scraping process. It employs the argparse module to parse and validate the input arguments.
## Implementation Notes
* Iterative algorithm
* Online algorithm
* multithreading with worker pool execution
* Wrapper classes to create abstraction for end user
* additional extra arguments inside the code for more control over the scalability
* dynamic resource usage scaling based on usage
## Prerequisites

- Python 3.10 or later installed on your system.

## Getting Started

1. Clone the repository or copy the code to your local machine.
2. (Recommended) create a virtual environment (for example conda or local) 
```bash 
python -m venv venv
```
3. Ensure you have the required Python dependencies by running the following command:

```bash
pip install -r ./requirements/publish.txt
```
## Usage
```python
from scraper import Scraper
NUM_THREADS=4
Scraper(NUM_THREADS).scrape(base_url, extract_amount, max_depth, unique)
```
or
```bash
python .\scraper\ https://www.ynetnews.com/ 5 2 true 
```
### Arguments:

* __base_url__ (string): The URL of the website to be scraped.

* __extract_amount__ (positive integer): The number of items to be extracted during the scraping process. It must be a positive integer.

* __max_depth__ (positive integer): The maximum depth of pages to be scraped. It must be a positive integer.

* __unique__ (boolean): A boolean value indicating whether the scraper should only extract unique items. Accepted values are "True" or "False".
