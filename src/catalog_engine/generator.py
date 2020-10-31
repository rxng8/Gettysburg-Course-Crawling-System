"""
    @file generator.py
    @author Alex Nguyen and Ben Durham

    This file contains every Generator classes and methods.

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
from extractor import PolicyExtractor, CourseExtractor
from explorer import CourseExplorer

class Generator:
    """
    Generator class
    """
    def __init__(self, courseExtractor: CourseExtractor,\
            policyExtractor: PolicyExtractor,\
            coursesExplorer: CourseExplorer):
        """
        Args:
            courseExtractor (CourseExtractor): [description]
            policyExtractor (PolicyExtractor, optional): [description]. Defaults to None.
        """
        # self.scraper = scraper
        self.pE = policyExtractor
        self.cE = courseExtractor
        self.c_explore = coursesExplorer
    
    def gen_subject(self, subject: Dict):
        """ Generate a single subject
        Args:
            subject (Dict): the dictionary of the subject to be generated
        Returns:
            (str): html string
        """
        if "Subject" not in subject.keys():
            print("No subject to be found!")
            return ""

        elem_id = self.gen_id_from_title(subject["Subject"])

        string = f"""
<h3 id="{elem_id}">
    {subject["Subject"]}
</h3>
        """

        if "Description" in subject.keys() and "None" not in subject["Description"]:
            string += f"""
<h4 id="">
Program Description 
</h4>
<div>
    {subject["Description"]}
</div>
            """
        else:
            print("No description for this subject: {}".format(subject["Subject"]))

        if "Major-minor" in subject.keys() and "None" not in subject["Major-minor"]:
            string += f"""
<h4 id="">
    Program Requirements 
</h4>
<div>
    {subject["Major-minor"]}
</div>
            """
        else:
            print("No major (minor) program requirements for this subject: {}".format(subject["Subject"]))

        if "Courses" in subject.keys() and "None" not in subject["Courses"]:
            string += f"""
<h4 id="">
    Courses 
</h4>
<div>
    {self.gen_all_courses(subject["Courses"])}
</div>
            """
        else: 
            print("No major (minor) program requirements for this subject: {}".format(subject["Subject"]))
        return string

    def gen_all_subjects(self):
        """
        Return:
            (str): The whole html string of every subjects
        """
        string = """"""
        for subject in self.cE.data:
            string += self.gen_subject(subject)
        return string

    def gen_course(self, info: Dict) -> str:
        """
        Args:
            info (Dict): a dictionary of a single course
        Returns:
            str: the html string of that single course
        """
        des = ""
        if self.c_explore:
            des = self.c_explore.get_description(info["Code"])
        if des != "":
            string = f"""
            <li>
                <span id="" > {info["Code"]} </span>
                <span id="" > {info["Course"]} </span>
                <div id=""> {des} </div>
            </li>
            <br>
                """
        else:
            string = f"""
            <li>
                <span id="" > {info["Code"]} </span>
                <span id="" > {info["Course"]} </span>
                <div id=""> {info["Content"]} </div>
            </li>
            <br>
                """
        return string

    def gen_all_courses(self, course_list: List) -> str:
        """
        Args:
            course_list (List): list of course, each course is a dictionary
        Returns:
            str: html string of all courses in one subject
        """
        string = """"""
        for course in course_list:
            string += self.gen_course(course)
        return string
    
    def gen_id_from_title(self, title):
        elem_id_no_spec_chars = title.replace("&", "").replace(",", "")
        elem_id = " ".join(elem_id_no_spec_chars.split()).lower().replace(" ", "-")
        return elem_id


    def gen_policy(self, info: Dict):
        """
        Args:
            info (Dict): the dictionary containing policy information
        Return:
            (str): The html string for a single policy
        """
        elem_id = self.gen_id_from_title(info['Title'])
        string = f"""
          <div id="{elem_id}">
            <h2>{info['Title']}</h2>
            {info['Content']}
          </div>
        """
        return string

    def gen_all_policies(self):
        """
        Return:
            (str): The html string of all policies
        """
        academic_policies = ""
        admissions_policies = ""
        financial_policies = ""
        for policy in self.pE.data:
            if policy['Policy_Type'] == "Academic":
                academic_policies += self.gen_policy(policy)
            elif policy['Policy_Type'] == "Admissions":
                admissions_policies += self.gen_policy(policy)
            elif policy['Policy_Type'] == "Financial":
                financial_policies += self.gen_policy(policy)
            else:
                print('Invalid policy type!')
        content = f"""<div id="policies">
            <div id="academic-policies">{academic_policies}</div>
            <div id="admissions-policies">{admissions_policies}</div>
            <div id="financial-policies">{financial_policies}</div>
        </div>
        """
        return content

    def gen_policies_of_type_toc(self, type):
        """
        Given a type of policy (i.e. Academic, Financial, Admissions)
        generates the TOC for that type
        
        Return:
            (str): The html toc of the given policy type
        """
        content = ''
        for policy in self.pE.data:
            if policy['Policy_Type'] == type:
                elem_id = self.gen_id_from_title(policy['Title'])
                content += f'<li><a href="#{elem_id}">{policy["Title"]}</a></li>'
        return content

    def gen_dept_toc(self):
        content = ''
        for subject in self.cE.data:
            elem_id = self.gen_id_from_title(subject["Subject"])
            content += f'<li><a href="#{elem_id}">{subject["Subject"]}</a></li>'
        return content

    def generate_toc(self):
        """
        Generates the table of contents

        Return:
            (str): The html table of contents
        """
        content = """
            <h2 id="toc">Table of Contents</h2>
            <ol>
                <li><a href="#academic-policies">Academic Policies</a>
                    <ol>
        """
        content += self.gen_policies_of_type_toc("Academic")
        content += """
                    </ol>
                </li>
                <li><a href="#admissions-policies">Admissions Policies</a>
                    <ol>
        """
        content += self.gen_policies_of_type_toc("Admissions")
        content += """
                    </ol>
                </li>
                <li><a href="#financial-policies">Financial Policies</a>
                    <ol>
        """
        content += self.gen_policies_of_type_toc("Financial")
        content += """
                    </ol>
                </li>
                <li><a href="#degree-requirements">Degree Requirements</a></li>
                <li><a href="#programs-of-study">Programs of Study</a>
                    <ol>
        """
        content += self.gen_dept_toc()
        content += """
                    </ol>
                </li>
            </ol>
        """
        return content

    def generate_json_from_data(self, output_directory: str, filename: str, cont=False):
        """ Write a JSON file
        Args:
            filename (str): file_path
            cont (bool, optional): Whether to concatenate or not. Defaults to False.
        """
        data = {}
        data['Policies'] = self.pE.data
        data['Programs'] = self.cE.data
        output_dir = output_directory
        if not output_directory.endswith("/"):
            output_dir += "/"
        if cont:
            with open(f"{output_dir}{filename}.json", "a") as f:
                json.dump(data, f)
        else:
            with open(f"{output_dir}{filename}.json", "w") as f:
                json.dump(data, f)
        
    def generate_html_from_data(self, output_directory: str, filename: str):
        """ Write html file
        Args:
            filename (str): file_path
        """
        output_dir = output_directory
        if not output_directory.endswith("/"):
            output_dir += "/"
        with open(f"{output_dir}{filename}.html", "wb") as f:
            if self.pE:
                f.write(self.generate_toc().encode("utf8"))
            if self.pE:
                f.write(self.gen_all_policies().encode("utf8"))
            if self.cE:
                f.write(self.gen_all_subjects().encode("utf8"))
