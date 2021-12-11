# Course Catalog Web Scraper System

This script grabs all of the relevant content for the course catalog from the gettysburg.edu
website and compiles into a single HTML file. It extracts all of the urls from a csv of the with
the given format (NEED TO ADD).

When grabbing the content from each page, this script assigns the section a new id created from its
url path for the sake of linking to it throughout the document. Additionally, all non-external
links re-created to link to the aforementioned id.

Pages are added to the final HTML file in the order they are listed in the csv.

# About Gettysburg Course Catalog Project

Snapshot script to crawl the relevant pages of the Gettysburg College website to fetch the Course Catalog content and generate a single HTML file with structured headings.

Main sections:
- Title and date generated
- Table of contents
- 1 - Academic Policies
- 2 - Admissions Policies
- 3 - Financial Policies
- 4 - Degree Requirements
- 5 - Programs of Study (54 programs, including majors and minors)
- 6 - Faculty Registry

The output is designed to be used as source for a Word or InDesign document to generate an accessible PDF.

Reference documents:
- [`model-document.pdf`](./src/model/model-document.pdf): Year 2019 PDF as an example of what the finished document should look like
- [`model-output.html`](./src/model/model-output.html): HTML markup template that the crawl script should render

# Getting started

## The codebase

1. The codebase of the package is located in [`src/catalog_engine/`](../src/catalog_engine).
2. The codebase consists of the following files:
    * [`scraper.py`](../src/catalog_engine/scraper.py): Scraper class which only crawl all sites from page.csv, and put them into data structures, i.e, list of soup, and mapper from each line to the soup. This class have been finished and does not need more change (for now)
    
    * [`extractor.py`](../src/catalog_engine/extractor.py): Extractor classes which only focus on taking those data structures we have from the Crawler, and organize and extract to build a kind of key, value dictionary, list according to the template model that Adrian gave us. (We can easily generate json file from this data structure, too!).

    * [`generator.py`](../src/catalog_engine/generator.py): Generator class which only focus on generating the output html file. So far I just have the generators that output every subjects (subjects, major-minor, courses, program) but not the curriculum and policies.

    * [`explorer.py`](../src/catalog_engine/explorer.py): Code for courses api communication.

## Data Structure

1. Courses JSON Data

(To be implemented)

2. Policies JSON Data

(To be implemented)


## How to run the package

1. Requirements:
    * [Python](https://www.python.org/)
    * [Doxygen](https://www.doxygen.nl/download.html) (if you want to generate the doc.)

2. Run this in bash
```
# First change directory to the src folder
cd src

# Install related python library
pip3 install -r ./requirements.txt

# Run the main file from the package
python3 ./mainv2.py
```

* Note: You can change `pip3` to `pip` and `python3` to `python` if possible

3. Generate the docs if you want to:
```
doxygen Doxyfile
```

### Note that after executing the main file, 2 output will be produced in the folder [`output`](../output/): `output_official.json` and `output_official.html`.