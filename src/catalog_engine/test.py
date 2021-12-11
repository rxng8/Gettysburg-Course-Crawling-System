"""
    @file main.py
    @author Alex Nguyen

    This is the test file to handle every execution

    Catalog Engine for Gettysburg College (catalog_engine) is the engine which extracts 
        content from Gettysburg website, together with Gettysburg website policies and courses api,
        and generate the appropriate courses content catalog for an academic year. More documentations
        can be viewed at `../../doc/` folder.
"""

# from .test.scraper_test import test_course_URL_scraper
from .scraper import *

if __name__ == '__main__':
    # test_course_URL_scraper()
    # sc = CourseURLScraper()
    # sc.to_csv("../data/courseLinks.csv")
    print("abc")