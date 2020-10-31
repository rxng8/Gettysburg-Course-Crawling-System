# How to execute the package

## The codebase

1. The codebase of the package is located in [`src/catalog_engine/`](../src/catalog_engine).
2. The codebase consists of the following files:
    * [`scraper.py`](../src/catalog_engine/scraper.py): Scraper class which only crawl all sites from page.csv, and put them into data structures, i.e, list of soup, and mapper from each line to the soup. This class have been finished and does not need more change (for now)
    
    * [`extractor.py`](../src/catalog_engine/extractor.py): Extractor classes which only focus on taking those data structures we have from the Crawler, and organize and extract to build a kind of key, value dictionary, list according to the template model that Adrian gave us. (We can easily generate json file from this data structure, too!).

    * [`generator.py`](../src/catalog_engine/generator.py): Generator class which only focus on generating the output html file. So far I just have the generators that output every subjects (subjects, major-minor, courses, program) but not the curriculum and policies.

    * [`explorer.py`](../src/catalog_engine/explorer.py): Code for courses api communication.


## How to run

1. Requirements:
    * [Python](https://www.python.org/)

2. Run this in bash
```
# First change directory to the folder
cd .

# Install related python library
pip install -r ./src/requirements.txt

# Run the main file from the package
python3 ./src/catalog_engine/main.py
```

### Note that after executing the main file, 2 output will be produced in the folder [`output`](../output/): `output_official.json` and `output_official.html`.