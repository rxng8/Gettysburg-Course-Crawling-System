"""
    @file main.py
    @author Alex Nguyen

    This is the main file to handle every execution

    Catalog Engine for Gettysburg College (catalog_engine) is the engine which extracts 
        content from Gettysburg website, together with Gettysburg website policies and courses api,
        and generate the appropriate courses content catalog for an academic year. More documentations
        can be viewed at `../../doc/` folder.
"""

from catalog_engine.explorer import CourseExplorer
from catalog_engine.generator import Generator
from catalog_engine.scraper import Scraper
from catalog_engine.extractor import CourseExtractor, PolicyExtractor, FacultyExtractor

import argparse

if __name__ == '__main__':

    csv_course_path = './data/courseLinks.csv'
    csv_policies_path = './data/pages.csv'
    csv_faculty_path = './data/faculty.csv'
    s_c = Scraper(csv_course_path, flag='courses')
    s_p = Scraper(csv_policies_path, flag='policies')
    s_f = Scraper(csv_faculty_path, flag='faculty')
    ce = CourseExtractor(s_c)
    pe = PolicyExtractor(s_p)
    fe = FacultyExtractor(s_f)

    api = 'https://www.gettysburg.edu/api/funnelback/courses/'
    c_explore = CourseExplorer(s_c.request_json_from_api(api))
    gen = Generator(ce, pe, fe, c_explore)
    gen.generate_html_from_data("../output", "new_official")
    gen.generate_json_from_data("../output","output_official")
