"""
    @file explorer.py
    @author Alex Nguyen

    This file contains the classes and methods for the courses api communication

    Catalog Engine for Gettysburg College (catalog_engine) is the engine which extracts 
        content from Gettysburg website, together with Gettysburg website policies and courses api,
        and generate the appropriate courses content catalog for an academic year. More documentations
        can be viewed at `../../doc/` folder.
"""

from typing import List, Dict
import re
import pandas as pd
import bs4
import requests
import json

class CourseExplorer:
    """
    Class for handling 'https://www.gettysburg.edu/api/funnelback/courses/'
        api specifically.
    """
    def __init__(self, data: Dict):
        self.data = data['data']
        self.attrs = ["catalogNumber", "subjectAreaAbbrv", "id", \
        "deparmentName", "title", "officialCourseDesc", "academicDepartmentId","url"]

    def get_description(self, course_code: str) -> str:
        """Given a course code, return the description of the course from the api
        Args:
            course_code (str): The course code is of the form "ABC-123". I.E, "AFS-132", "CS-216"

        Returns:
            str: Description of the course
        """

        key_data = course_code.split("-")
        if (len(key_data) != 2):
            print(f"Error in extracting description of {course_code}!")
            return ""

        abbr = key_data[0]
        num = key_data[1]

        for course in self.data:
            if str(course["subjectAreaAbbrv"]) == abbr and str(course["catalogNumber"]) == num:
                return course["officialCourseDesc"]

        print("Unexpected error! No course code matched!")
        return ""


class ProgramExplorer:
    """
    Class for handling only 'https://www.gettysburg.edu/api/funnelback/programs/' api
        communication.
    """

    def __init__(self, data: Dict):
        self.data = data['data']
        pass