"""
    @file main.py
    @author Alex Nguyen

    This is the main file to handle every execution

    Catalog Engine for Gettysburg College (catalog_engine) is the engine which extracts 
        content from Gettysburg website, together with Gettysburg website policies and courses api,
        and generate the appropriate courses content catalog for an academic year. More documentations
        can be viewed at `../../doc/` folder.
"""

from explorer import CourseExplorer
from generator import Generator
from scraper import Scraper
from extractor import CourseExtractor, PolicyExtractor

if __name__ == '__main__':
    # csv_path = '../data/pages.csv'
    # s = Scraper(csv_path)
    # ce = CourseExtractor(s)
    # pe = PolicyExtractor(s)
    # api = 'https://www.gettysburg.edu/api/funnelback/courses/'
    # c_explore = CourseExplorer(s.request_json_from_api(api))
    # gen = Generator(ce, pe, c_explore)
    # gen.generate_json_from_data("../../output","output_official")
    # gen.generate_html_from_data("../../output", "output_official")

    csv_path = '../data/courseLinks.csv'
    s = Scraper(csv_path)
    # print (s.mapper[0].find('h1', {"class": "gb-c-hero__title"}))
    ce = CourseExtractor(s)
    print("Extracted: " + str(ce.data.keys()))
    print("Extracted: " + str(ce.data['africana-studies'].keys()))
    # api = 'https://www.gettysburg.edu/api/funnelback/courses/'
    # c_explore = CourseExplorer(s.request_json_from_api(api))
    # gen = Generator(ce, None, c_explore)
    # gen.generate_html_from_data("../../output", "test_new_course")