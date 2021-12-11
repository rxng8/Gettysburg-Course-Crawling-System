""" @file explorer.py
    @author Alex Nguyen

    This file contains the classes and methods for the courses api communication

    Catalog Engine for Gettysburg College (catalog_engine) is the engine which extracts 
        content from Gettysburg website, together with Gettysburg website policies and courses api,
        and generate the appropriate courses content catalog for an academic year. More documentations
        can be viewed at `../../doc/` folder.
"""

from typing import Collection, List, Dict
import re
import pandas as pd
import bs4
import requests
import json
import collections

class CourseExplorer:
    """ Class for handling 'https://www.gettysburg.edu/api/funnelback/courses/' api specifically.
    """
    
    def __init__(self, data: Dict):
        """ Description

        Args:
            data (Dict): [description]
        """
        self.data = data['data']
        self.attrs = ["catalogNumber", "subjectAreaAbbrv", "id", \
        "deparmentName", "title", "officialCourseDesc", "academicDepartmentId","url"]
        self.subjects_dict: Dict = self.__populate_subject_dict()

    def __populate_subject_dict(self):
        result: collections.Counter = collections.Counter()
        for course in self.data:
            result[course["deparmentName"]] += 1
        return result

    def get_description(self, course_code: str) -> str:
        """ Given a course code, return the description of the course from the api
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
    """ Class for handling only 'https://www.gettysburg.edu/api/funnelback/programs/' api communication.
    """

    def __init__(self, data: Dict):
        self.data = data['data']
        pass

class CoursePage:
    def __init__(self, subject_name: str, data: Dict) -> None:
        """ Init

        Args:
            subject (str): Name of the subject. E.g. Africana Studies
            data (Dict): The data from the Course Explorer
        """
        self.subject_name = subject_name
        self.data = data

    @staticmethod
    def gen_course(code: str, course_name: str, description: str) -> bs4.BeautifulSoup:
        """ Given a code, course, and description, build a course block with bs4 object
        Args:
            code (str): 
            course_name (str):
            description (str):
        Returns:
            bs4.BeautifulSoup: the bs4 html object of that single course
        """

        # https://stackoverflow.com/a/21356230
        # `li` has the form <div><li></li></div>? I guess so?
        li = bs4.BeautifulSoup("<li></li>", "html.parser")

        # The acutal li tag inside the div of `li`
        original_li = li.li
        
        code_tag = li.new_tag("span")
        code_tag.string = code + " " # Need a space here to seperate between code and title
        original_li.append(code_tag)

        title_tag = li.new_tag("span")
        title_tag.string = course_name
        original_li.append(title_tag)

        description_tag = li.new_tag("div")
        description_tag.string = description
        original_li.append(description_tag)

        br_tag = li.new_tag("br")
        original_li.append(br_tag)
        
        # string = f"""
        # <li>
        #     <span id="" > {code} </span>
        #     <span id="" > {course_name} </span>
        #     <div id=""> {description} </div>
        # </li>
        # <br>
        #     """
        # return string

        return li

    def gen_all_courses_for_this_subject(self) -> bs4.BeautifulSoup:
        
        # Read this reference: https://www.geeksforgeeks.org/how-to-insert-a-new-tag-into-a-beautifulsoup-object/
        
        # `div` have the form <div><div></div></div>
        div = bs4.BeautifulSoup("<div></div>", "html.parser")

        # the actual div tag inside the div of `div`
        original_div = div.div

        for course in self.data:
            if course["deparmentName"] == self.subject_name:
                code: str = course["subjectAreaAbbrv"] + "-" + course["catalogNumber"]
                title: str = course["title"]
                description: str = course["officialCourseDesc"]
                original_div.append(CoursePage.gen_course(code, title, description))
        return original_div

    def __str__(self) -> str:
        return str(self.gen_all_courses_for_this_subject())


class CoursePage_v2:
    def __init__(self, subject_abbrs: List[str], data: Dict) -> None:
        """ Init

        Args:
            subject (str): Name of the subject. E.g. Africana Studies
            data (Dict): The data from the Course Explorer
        """
        self.subject_abbrs = subject_abbrs
        self.data = data

    @staticmethod
    def gen_course(code: str, course_name: str, description: str) -> bs4.BeautifulSoup:
        """ Given a code, course, and description, build a course block with bs4 object
        Args:
            code (str): 
            course_name (str):
            description (str):
        Returns:
            bs4.BeautifulSoup: the bs4 html object of that single course
        """

        # https://stackoverflow.com/a/21356230
        # `li` has the form <div><li></li></div>? I guess so?
        li = bs4.BeautifulSoup("<li></li>", "html.parser")

        # The acutal li tag inside the div of `li`
        original_li = li.li
        
        code_tag = li.new_tag("span")
        code_tag.string = code + " " # Need a space here to seperate between code and title
        original_li.append(code_tag)

        title_tag = li.new_tag("span")
        title_tag.string = course_name
        original_li.append(title_tag)

        description_tag = li.new_tag("div")
        description_tag.string = description
        original_li.append(description_tag)

        br_tag = li.new_tag("br")
        original_li.append(br_tag)
        
        # string = f"""
        # <li>
        #     <span id="" > {code} </span>
        #     <span id="" > {course_name} </span>
        #     <div id=""> {description} </div>
        # </li>
        # <br>
        #     """
        # return string

        return li

    def gen_all_courses_for_this_subject(self) -> bs4.BeautifulSoup:
        
        # Read this reference: https://www.geeksforgeeks.org/how-to-insert-a-new-tag-into-a-beautifulsoup-object/
        
        # `div` have the form <div><div></div></div>
        div = bs4.BeautifulSoup("<div></div>", "html.parser")

        # the actual div tag inside the div of `div`
        original_div = div.div

        for subjectAbbr in self.subject_abbrs:
            for course in self.data:
                if course["subjectAreaAbbrv"] == subjectAbbr:
                    code: str = course["subjectAreaAbbrv"] + "-" + course["catalogNumber"]
                    title: str = course["title"]
                    description: str = course["officialCourseDesc"]
                    original_div.append(CoursePage_v2.gen_course(code, title, description))
        return original_div

    def __str__(self) -> str:
        return str(self.gen_all_courses_for_this_subject())