"""
    @file main.py
    @author Alex Nguyen

    This is the main file to handle every execution

    Catalog Engine for Gettysburg College (catalog_engine) is the engine which extracts 
        content from Gettysburg website, together with Gettysburg website policies and courses api,
        and generate the appropriate courses content catalog for an academic year. More documentations
        can be viewed at `../../doc/` folder.
"""

from catalog_engine_v2.explorer import CourseExplorer
from catalog_engine_v2.const import COURSE_CRAWLING_MODE, FUNNELBACK_COURSE_API
from catalog_engine_v2.template_v2 import Template
from catalog_engine_v2.utils import request_json_from_api

import argparse
# import sys
# import resource

if __name__ == '__main__':
    
    # template_path = "./data/template.html"
    template_2022_path = "./model/model-output-2022.html"
    locators_path = "./data/locators.json"
    exported_content_path = "../output/tmp_v2.html"
    data_path = "./data/page_objects"

    # https://stackoverflow.com/a/41916266
    # max_rec = 0x100000
    # # May segfault without this line. 0x100 is a guess at the size of each stack frame.
    # resource.setrlimit(resource.RLIMIT_STACK, [0x100 * max_rec, resource.RLIM_INFINITY])
    # sys.setrecursionlimit(max_rec)

    # First of all, process the code from the api
    explorer = CourseExplorer(request_json_from_api(FUNNELBACK_COURSE_API))
    # print(explorer.subjects_dict)

    # Second, process the catalog generation
    T = Template(
        # template_path=template_path, 
        template_path=template_2022_path,
        locators_path=locators_path, 
        course_crawling_mode=COURSE_CRAWLING_MODE.api, 
        course_explorer=explorer, 
        data_path=data_path,
        verbose=True)
    T.insight()
    exported_content = T.generate()
    with open(exported_content_path, "wb") as f:
        f.write(exported_content.encode("utf8"))
    