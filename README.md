# Scraper Exercise

This code provides an example of a Command Line Interface (CLI) tool for web scraping with input validation. The program uses Python and allows users to provide input arguments through the command line to control the web scraping process. It employs the argparse module to parse and validate the input arguments.
## Implementation Notes
* __Iterative algorithm__ - uses less system resources over recursion and the upper bound limit for memory usage is significantly higher
* __Online algorithm__ - ability to support dynamically growing or shrinking queue of jobs to perform as we don't know the whole working set in advance
* __multithreading with worker pool execution__ - Using multithreading to speed up the execution as there are significant slowdown during the downloading of the HTML which is equivalent here to external IO
* __using synchronization mechanisms for multithreading (no busy-waiting)__ - As we are dealing with multithreading we need to synchronize non-atomic operations above our data structures and communication between the threads
* __Wrapper classes to create abstraction for end user__ - Easy use, Abstraction, Facade
* __additional extra arguments inside the code for more control over the scalability__ - Allowing additional fine-tuning for specific requirements
* __dynamic resource usage scaling based on usage__ - Because the algorithm is an Online algorithm we want the system usage to scale based on the available workload up to an upper bound
* __CLI usage__ - Nice CLI usage and integration
* __import vs run module as main__ - This code can be used both with an import and both as running as the main module straight from the command line with no imports required

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
s = Scraper(
    NUM_THREADS,
    ScraperWorker,
    dict(extractor_class=LinkExtractor)
)
s.scrape(
    base_url,
    extract_amount,
    max_depth,
    unique
)
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
