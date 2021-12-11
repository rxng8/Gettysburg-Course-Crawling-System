""" @file extractor.py
    @author Alex Nguyen and Ben Durham

    This file contains classes and methods for policies and courses extractor

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
from .scraper import *

class Extractor:
    """ Super class of extractor
    """
    def __init__(self, n_url: int):
        """ description
        Args:
            n_url (int): number of total page have been crawled.
        """
        self.extracted: List[bool] = [False] * n_url

    def extract_all_source(self):
        """ Extract all sources
        """
        pass

    def extract_subjects(self):
        """ Extract all subject pages
        """
        pass

    def extract_policy(self):
        """ Extract all policy pages
        """
        pass

class FacultyExtractor (Extractor):
    """ This class extracts faculty pages
    """
    def __init__(self, scraper: Scraper):
        """ description
        Args:
            scraper (Scraper): [description]
        """
        print("Extracting Faculty Info")
        self.VERBOSE = False
        super().__init__(len(scraper.df))
        self.scraper = scraper
        self.base_uri = 'https://www.gettysburg.edu/academic-programs/curriculum/catalog/faculty-registry/'
        self.data = self.extract_all_soup()

    def extract_all_soup(self):
        """ Extracts faculty information and places it in the data structure

        Returns:
            [type]: [description]
        """
        data = []
        for i, line in self.scraper.df.iterrows():
            soup = self.scraper.mapper[i]
            if self.base_uri in str(line["URL"]):
                page : Dict = {}
                page['Title'] = str(line["URL"].split('/')[-1])
                page['Content'] = str(soup.select('div.gb-c-longform')[0])
                data.append(page)
        return data

class PolicyExtractor (Extractor):
    """ This class extracts policy pages
    """
    def __init__(self, scraper: Scraper):
        """ description
        Args:
            scraper (Scraper): [description]
        """
        self.VERBOSE = False
        super().__init__(len(scraper.df))
        print(len(self.extracted))
        self.scraper = scraper
        self.base_uri = 'https://www.gettysburg.edu/academic-programs/curriculum/catalog/policies/policy-details'
        self.data = self.extract_all_soup()

    def get_policy_ids(self):
        """ Gets a list of all links of the type "Policy Details"

        Returns:
            List[Tuple]: List of (index in df, link) of core links for policies
        """
        policy_ids = []
        for i, line in self.scraper.df.iterrows():
            if self.base_uri in str(line["URL"]):
                policy_id = str(line["URL"].split('?')[1])[3:]
                policy_ids.append((i, policy_id))
        return policy_ids

    def get_policy_type(self, title):
        """[summary]

        Args:
            title ([type]): [description]

        Returns:
            [type]: [description]
        """
        if "Admission" in title or "Application" in title or "Advanced Placement" in title:
            return "Admissions"

        financial_policies = [
          "Semester Tuition, Room and Meals (Comprehensive Fee)",
          "Payment of Bills and Billing Statements",
          "Enrollment Deposit",
          "Payment Plans",
          "Withdrawal and Leave of Absence Refund Policy",
          "College Store",
          "Credit Balance Refund Policy",
          "Insurance",
          "Meal Plan Policy",
          "Merit-Based Scholarships",
          "Need-Based Financial Aid",
          "Veterans Benefits"
        ]
        if title in financial_policies:
            return "Financial"
        return "Academic"

    def extract_soup(self, soup_id, policy_id):
        """ Extract policy information for a specific policy

        Args:
            soup_id (BeautifulSoup) : The BeautifulSoup object to extract data from
            policy_id (string) : The id of the policy from the url parameter

        Return:
            (Dict): The policy object for that specific page
        """
        data: Dict = {}
        soup = self.scraper.mapper[soup_id]
        data['Title'] = str(soup.find('h1', {'class': 'gb-c-hero__title'}).get_text())
        data['Content'] = str(soup.select('div.gb-c-longform.column')[0])
        data['Policy_ID'] = policy_id
        data['Policy_Type'] = self.get_policy_type(data['Title'])
        return data
        
    def extract_all_soup(self):
        """ Extract every policy in the soup list

        Returns:
            List[Dict]: List of policy Dicts (each policy is represented by a dictionary)
        """
        print("Extracting Policies...")
        data = []
        policy_ids = self.get_policy_ids()
        for i, policy_id in policy_ids:
          data.append(self.extract_soup(i, policy_id))
        
        return data
    
    def toString(self):
        """ From crawl data, generate the html string to be written to file.
        
        Returns: 
            (str): String of the data
        """
        pass

class CourseExtractor (Extractor):
    """ This class extracts subject pages
    """

    def __init__(self, scraper: Scraper): 
        """ description
        Args:
            scraper (Scraper): [description]
        """

        self.VERBOSE = False
        super().__init__(len(scraper.df))
        # Take only the core links (the link with no programs, courses, major or minor in the sub): 
        # https://www.gettysburg.edu/academic-programs/sdds/ => academic-programs/sdds
        self.r_c = r"academic-programs\/[^\/]+\/$"
        # Take only the core link with the program sublink: 
        self.r_p = r"\/academic-programs\/.+\/programs\/$"
        # Take only the links with program requirements(I.e. major, minor)
        self.r_m = r"\/academic-programs\/.+\/programs\/.+$"
        # Take the course link
        self.r_co = r"\/academic-programs\/.+\/courses\/$"
        # print(len(self.extracted))
        self.scraper = scraper
        self.course_index = self.extract_course_index()
        self.data = self.extract_all_soup()
        
    def get_core_link(self):
        """ Summary

        Returns:
            List[Tuple]: List of (index in df, link) of core links courses
        """
        core_links = []
        # Take only the core links (the link with no programs, courses, major or minor in the sub): 
        r_c = r"\/academic-programs\/.+\/$"

        for i, line in self.scraper.df.iterrows():
            if len(re.findall(r_c, str(line["URL"]))) > 0 or "Until Featured course header"\
                in str(line["Notes"]):
                core_links.append((i, str(line["URL"])))
        print (f"Number of core links (Main Subject): {len(core_links)}")
        return core_links

    def extract_course_index_deprecated(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        core_links = self.get_core_link()
        base_uri = []
        
        # Index of course link in the scraper data
        course_index = []
        # Go to the next link whenever the pattern stop
        for i, link in core_links:
            ptr = i

            # Core link index tracking
            base_uri.append(ptr)


            while ptr < len(self.scraper.df) and link in str(self.scraper.df.loc[ptr]["URL"]):
                if self.VERBOSE:
                    print(self.scraper.df.loc[ptr]["URL"])
                course_index.append(ptr)
                ptr += 1
        return course_index, base_uri

    def extract_course_index(self):
        """ Take all line indices of the links that have pattern `r"\/academic-programs\/.+\/.*"`
        in the scraper.df and put all those indices in an array `course_index` 

        Returns:
            [type]: [description]
        """
        # Index of course link in the scraper data
        course_index = []
        r_s = r"\/academic-programs\/.+\/.*"
        for i in range(len(self.scraper.df)):
            if (len(re.findall(r_s ,self.scraper.df.loc[i]['URL'])) > 0):
                course_index.append(i)

        return course_index

    def extract_soup(self, id, base_uri, uri, soup, title=None, notes=None):
        """Extract one page of html in the list of soup

        Args:
            id (int): id in the mapper which map from row containing 
                url, title, notes to the soup list
            base_uri (str): the base url of the subject.
                i.e: "http://gettysburg.edu/economics/", ...
            uri (str): the full url of the page.
                i.e: "http://gettysburg.edu/economics/courses/"
            title (str): title in the csv file
            notes (str): notes in the csv file
            soup (BeautifulSoup): the soup in the list of soup that
                correspond to this row (link, etc)

        Returns:
            dict: One dictionary data for a page
        """
        p = r"programs\/.+\/"

        if len(re.findall(self.r_m, uri)) > 0:
            print(f"Extracting {uri} as Major-minor template")
            dict_attr = ['Major-minor']
            data: Dict = {}
            soup = self.scraper.mapper[id]
            # content = soup.find('main', {'class': 'gb-u-spacing-quad-top'})
            content = soup.find('div', {'class': 'gb-c-longform'})
            if content:
                # Remove image tag
                # content_copy = content.copy()
                # imgs = content_copy.find_all('img')
                imgs = content.find_all('img')
                for img in imgs:
                    img.decompose()
                # data['Major-minor'] = str(content.text)
                data['Major-minor'] = str(content)
            else:
                data['Major-minor'] = "None"
            if self.VERBOSE:
                print(data)
            return data
        elif len(re.findall(self.r_p, uri)) > 0:
            print(f"Extracting {uri} as Program template")
        # elif regex_program.findall(string):
            dict_attr = ['Description']
            # data : List[Dict] = []
            data: Dict = {}

            soup = self.scraper.mapper[id]
            # if "Program" in soup.find('h1', {'class': 'gb-c-hero__title'}).text or \
            #     "The BMB Major" in soup.find('h1', {'class': 'gb-c-hero__title'}).text:

            content = soup.find('div', {'class': 'gb-u-spacing-quad-top'})
            if content:
                # data['Description'] = str(content.text)
                # Remove image tag
                # content_copy = content.copy()
                # imgs = content_copy.find_all('img')
                imgs = content.find_all('img')
                for img in imgs:
                    img.decompose()
                # data['Description'] = str(content_copy)
                data['Description'] = str(content)
            else:
                data['Description'] = "None"
            if self.VERBOSE:
                print(data)
            # data.append(datum)
            # else:
                # print(f"Error in crawling program page url: {uri}")
            return data
        elif len(re.findall(self.r_co, uri)) > 0:
            print(f"Extracting {uri} as course template")
            dict_attr = ['Code', 'Course', 'Content']

            data_dict = {}

            data : List[Dict] = []

            soup = self.scraper.mapper[id]
            # if "Courses" in soup.find('h1', {'class': 'gb-c-hero__title'}).text:
            contents = soup.find_all('li', {'class': 'gb-c-accordion__item'})
            for content in contents:
                datum = {}
                datum['Code'] = str(content.find('span', {'class': 'gb-c-accordion__sub-heading'}).text)
                datum['Course'] = str(content.find('span', {'class': 'gb-c-accordion__heading'}).text)
                datum['Content'] = str(content.find('div', {'class': 'gb-c-accordion__content'}).text)
                if self.VERBOSE:
                    print(datum)
                data.append(datum)
            data_dict['Courses'] = data
            # else:
            #     print(f"Error in crawling course listing page url: {uri}")
            return data_dict
        elif uri == base_uri:
            print(f"Extracting {uri} as main page template")
            # Test extract brief
            dict_attr = ['Subject', 'Major', 'Minor', 'Brief']
            # data : List[Dict] = []
            data: Dict = {}
            soup = self.scraper.mapper[id]
            content = soup.find('div', {'class': 'gb-u-spacing-bottom'})
            if content is not None:
                # Remove image tag
                # content_copy = content.copy()
                # imgs = content_copy.find_all('img')
                imgs = content.find_all('img')
                for img in imgs:
                    img.decompose()
                data['Subject'] = soup.find('h1', {'class': 'gb-c-hero__title'}).text
                data['Major'] = "Major" in content.text
                data['Minor'] = "Minor" in content.text
                # brief description may exist in a page or it may not
                brief = content.find('p', {'class': 'gb-u-type-p'})
                if brief:
                    data['Brief'] = str(brief)
                else:
                    data['Brief'] = "None"
                if self.VERBOSE:
                    print(data)
                return data
            # Else, the content of the base url is not of the same html tag and div class
            # This should be the sunderman music page and prehealth page
            # else:
            # print(f"Extracting the url {uri} in other formats...")
            # Handle conservatory of music
            content = soup.find('main', {'class': 'gb-u-spacing-quad-top'})
            if content is not None:
                # Remove image tag
                # content_copy = content.copy()
                # imgs = content_copy.find_all('img')
                imgs = content.find_all('img')
                for img in imgs:
                    img.decompose()
                data['Subject'] = soup.find('h1', {'class': 'gb-c-hero__title'}).text
                data['Major'] = True
                data['Minor'] = True
                # brief description may exist in a page or it may not
                brief = content.find('p', {'class': 'gb-u-space--bottom'})
                # print(brief)
                if brief:
                    data['Brief'] = str(brief.text)
                else:
                    data['Brief'] = "None"
                if self.VERBOSE:
                    print(data)
                return data
            
            # Else, the content of the base url is not of the same html tag and div class
            # This should be the sunderman music page and prehealth page
            # else:
            # Handle pre-health
            content = soup.find('div', {'class': 'gb-c-longform'})
            if content is not None:
                # Remove image tag
                # content_copy = content.copy()
                # imgs = content_copy.find_all('img')
                imgs = content.find_all('img')
                for img in imgs:
                    img.decompose()
                data['Subject'] = soup.find('h1', {'class': 'gb-c-hero__title'}).text
                data['Major'] = None
                data['Minor'] = None

                brief = ""
                for tag in content.find_all():
                    brief += str(tag)
                    if "gb-u-type-delta" in str(tag.next_element):
                        break
                # print(brief)
                # brief = content.text
                # if brief:
                #     data['Brief'] = brief.text
                # else:
                #     data['Brief'] = "None"
                if self.VERBOSE:
                    print(data)
                return data

        # elif len(re.findall(r_c, uri)) > 0:
        #     print(f"No template to extract this url: {uri}")
            
        else:
            print(f"No crawling template for this url: {uri}")
        
        pass

    def extract_all_soup(self):
        """ Extract every soup in the soup list
        
        Returns:
            List[Dict]: List of subject content (each content is represented by a dictionary)
        """
        print("Extracting...")
        # Take only the core links (the link with no programs, courses, major or minor in the sub): 
        # r_c = r"\/academic-programs\/.+\/$"
        # Take only the core link with the program sublink: 
        # r_p = r"\/academic-programs\/.+\/programs\/$"
        # Take only the links with program requirements(I.e. major, minor)
        # r_m = r"\/academic-programs\/.+\/programs\/.+$"
        # Take the course link
        # r_co = r"\/academic-programs\/.+\/courses\/$"

        data = {}

        # debugging code 
        # head = 200
        current_subject_name = ""
        current_subject_data = {}

        # current_uri = self.scraper.df.loc[self.course_index[0]]["URL"]
        # current_subject_uri = current_uri
        # current_subject_name = re.findall(self.r_c, current_subject_uri)[0][len("/academic-programs\/"):]
        
        core = 0
        confirm_extract = 0
        for ptr in range(len(self.course_index)):
            # debugging code
            # if head == 0:
            #     break

            current_uri = self.scraper.df.loc[self.course_index[ptr]]["URL"]

            # If go to a new link then change the base link _ new category (subject)
            if len(re.findall(self.r_c, current_uri)) > 0:
                core += 1
                # print(current_uri)
                if ptr != 0:
                    if current_subject_name not in data.keys():
                        data[current_subject_name] = current_subject_data
                    else:
                        data[current_subject_name] = {**data[current_subject_name], **current_subject_data}
                    # print(data[current_subject_name].keys())
                    current_subject_data = {}
                current_subject_uri = current_uri
                current_subject_name = re.findall(self.r_c, current_subject_uri)[0][len("/academic-programs\/") - 2: - 1]
                
            soup = self.scraper.mapper[self.course_index[ptr]]

            # Returned content is a dict
            content = self.extract_soup(ptr, current_subject_uri, current_uri, soup)
            
            if content:
                # print("Content keys: "  + str(content.keys()))
                # print(content)
                current_subject_data = {**current_subject_data, **content}
                confirm_extract += 1

            else:
                print(f"Failed extracting url: {current_uri}")
                # pass
            # debugging code
            # head -= 1
        
        # Append the last current subject
        data[current_subject_name] = current_subject_data
        print (f"There are {core} number of subjects!")
        print(f"Extracted {confirm_extract} number of urls out of {len(self.course_index)} urls!")

        return data

    def extract_all_soup_deprecated(self):
        """ Extract every soup in the soup list
        
        Returns:
            List[Dict]: List of subject content (each content is represented by a dictionary)
        """
        print("Extracting...")

        data = []

        # debugging code 
        head = 200

        current_subject = {}

        current_core_link = self.scraper.df.loc[0]["URL"]
        confirm_extract = 0
        for ptr in self.course_index:
            # debugging code
            if head == 0:
                break

            # If go to a new link then change the base link _ new category (subject)
            if ptr in self.base_uri:
                current_core_link = self.scraper.df.loc[ptr]["URL"]
                if ptr != 0:
                    data.append(current_subject)
                    # data[f'{self.}']
                    current_subject = {}

            current_uri = self.scraper.df.loc[ptr]["URL"]
            
            title = self.scraper.df.loc[ptr]["Title"]
            notes = self.scraper.df.loc[ptr]["Notes"]
            soup = self.scraper.mapper[ptr]

            # Returned content is a dict
            content = self.extract_soup(ptr, current_core_link, current_uri, title, notes, soup)

            if content:
                # Merge 2 dicts
                # print(f"Current ptr: {ptr}\n")
                current_subject = {**current_subject, **content}
                confirm_extract += 1

            else:
                print(f"Failed extracting url: {current_uri}")

            # debugging code
            head -= 1
        
        # Append the last current subject
        data.append(current_subject)

        print(f"Extracted {confirm_extract} number of urls out of {len(self.course_index)} urls!")

        return data


    def __str__(self):
        """ From crawl data, generate the html string to be written to file.
        
        Returns: 
            str: String of the data
        """
        pass
