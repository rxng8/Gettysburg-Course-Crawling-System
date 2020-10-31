# %%
from typing import List, Dict
import re
import pandas as pd
import bs4
import requests
import json

class Scraper:
    """
    The scraper class will crawl all data from link
    """
    def __init__(self, csv_path):
        """
        Args:
            csv_path (str): The path to the csv file that contains all link
        """
        super().__init__()
        self.csv_path = csv_path
        self.mapper = {}
        self.VERBOSE = True
        self.df = pd.read_csv(csv_path, names=['URL', 'Title', 'Notes']).iloc[1:, :].reset_index()[["URL", "Title", "Notes"]]
        self.soup = self.scrape_src()
        
    def scrape_src(self) -> List[bs4.BeautifulSoup]:
        """Scrape every link from the csv file
        Returns:
            List[bs4.BeautifulSoup]: [description]
        """
        if self.VERBOSE:
            print("Crawling data from all links ...")
        soup = []
        for i, line in self.df.iterrows():
            uri = line["URL"]
            if uri.endswith(".pdf"):
                if self.VERBOSE:
                    print("Not crawling pdf file, continue...")
                continue
            if self.VERBOSE:
                print(f"Crawling Url: {uri}...")
            src = requests.get(uri).text
            soup_src = bs4.BeautifulSoup(src, 'html.parser')
            soup.append(soup_src)
            self.mapper[i] = soup_src
        if self.VERBOSE:
            print("Done! Data now loaded in self.soup array")
        return soup

    def request_json_from_api(self, url: str):
        res = requests.get(url)
        data = res.json()
        return data

    def set_verbose(self, v):
        """Debugger
        Args:
            v (bool): Whether the debugger mode is on or off.
        """
        self.VERBOSE = v

    def toString(self):
        """From crawl data, generate the html string to be written to file.
        @Params:
        @Return: (str): String of the data
        """
        description = f"The data is at `self.soup` and the mapper (int, soup) from dataframe row num to the soup data"
        return description

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


class Extractor:
    """
        Super class of extractor
    """
    def __init__(self, n_url: int):
        """
        Args:
            n_url (int): number of total page have been crawled.
        """
        self.extracted: List[bool] = [False] * n_url

    def extract_all_source(self):
        """
        Extract all sources
        """
        pass

    def extract_subjects(self):
        """
        Extract all subject pages
        """
        pass

    def extract_policy(self):
        """
        Extract all policy pages
        """
        pass
        

class PolicyExtractor (Extractor):
    """
        This class extracts policy pages
    """
    def __init__(self, scraper: Scraper):
        """
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
      """
      Gets a list of all links of the type "Policy Details"

      Returns:
          List[Tuple]: List of (index in df, link) of core links courses
      """
      policy_ids = []
      for i, line in self.scraper.df.iterrows():
        if self.base_uri in str(line["URL"]):
          policy_id = str(line["URL"].split('?')[1])[3:]
          policy_ids.append((i, policy_id))
      return policy_ids

    def get_policy_type(self, title):
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
        """Extract policy information for a specific policy
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
        """From crawl data, generate the html string to be written to file.
        @Params:
        @Return: (str): String of the data
        """
        pass

class CourseExtractor (Extractor):
    """
    This class extracts subject pages
    """

    def __init__(self, scraper: Scraper): 
        """
        Args:
            scraper (Scraper): [description]
        """

        self.VERBOSE = False
        super().__init__(len(scraper.df))
        print(len(self.extracted))
        self.scraper = scraper
        self.course_index, self.base_uri = self.extract_course_index()
        self.data = self.extract_all_soup()
        
    def get_core_link(self):
        """ Summary

        Returns:
            List[Tuple]: List of (index in df, link) of core links courses
        """
        core_links = []
        for i, line in self.scraper.df.iterrows():
            if "Until Featured course header" in str(line["Notes"]):
                core_links.append((i, str(line["URL"])))
        return core_links

    def extract_course_index(self):
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


    def extract_soup(self, id, base_uri, uri, title, notes, soup):
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
        p = "programs\/\Z"
        string = uri[len(base_uri):]
        regex_program = re.compile(p)
        if 'major' in uri or 'minor' in string:
            dict_attr = ['Major-minor']
            data: Dict = {}
            soup = self.scraper.mapper[id]
            # content = soup.find('main', {'class': 'gb-u-spacing-quad-top'})
            content = soup.find('div', {'class': 'gb-c-longform'})
            if content:
                # data['Major-minor'] = str(content.text)
                data['Major-minor'] = str(content)
            else:
                data['Major-minor'] = "None"
            if self.VERBOSE:
                print(data)
            return data
        elif 'program' in uri[len(base_uri):] and 'courses' not in string:
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
                data['Description'] = str(content)
            else:
                data['Description'] = "None"
            if self.VERBOSE:
                print(data)
            # data.append(datum)
            # else:
                # print(f"Error in crawling program page url: {uri}")
            return data
        elif 'courses' in string:
            dict_attr = ['Code', 'Course', 'Content']

            data_dict = {}

            data : List[Dict] = []

            soup = s.mapper[id]
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
            # Test extract brief
            dict_attr = ['Subject', 'Major', 'Minor', 'Brief']
            # data : List[Dict] = []
            data: Dict = {}
            soup = s.mapper[id]
            content = soup.find('div', {'class': 'gb-u-spacing-bottom'})
            if content is not None:
                
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
            print(f"Extracting the url {uri} in other formats...")
            # Handle conservatory of music
            content = soup.find('main', {'class': 'gb-u-spacing-quad-top'})
            if content is not None:
                
                data['Subject'] = soup.find('h1', {'class': 'gb-c-hero__title'}).text
                data['Major'] = True
                data['Minor'] = True
                # brief description may exist in a page or it may not
                brief = content.find('p', {'class': 'gb-u-space--bottom'}).text
                print(brief)
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
            # Handle pre-health
            content = soup.find('div', {'class': 'gb-c-longform'})
            if content is not None:
                
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
            
        else:
            print(f"No crawling template for this url: {uri}")
        
        pass

    def extract_all_soup(self):
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


    def toString(self):
        """From crawl data, generate the html string to be written to file.
        @Params:
        @Return: (str): String of the data
        """
        pass

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

        string = f"""
<h3 id="">
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

    def gen_policy(self, info: Dict):
        """
        Args:
            info (Dict): the dictionary containing policy information
        Return:
            (str): The html string for a single policy
        """
        elem_id_no_spec_chars = info['Title'].replace("&", "").replace(",", "")
        elem_id = " ".join(elem_id_no_spec_chars.split()).lower().replace(" ", "-")
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

    def generate_json_from_data(self, filename: str, cont=False):
        """ Write a JSON file
        Args:
            filename (str): file_path
            cont (bool, optional): Whether to concatenate or not. Defaults to False.
        """
        data = {}
        data['Policies'] = self.pE.data
        data['Programs'] = self.cE.data
        if cont:
            with open(f"../output/{filename}.json", "a") as f:
                json.dump(data, f)
        else:
            with open(f"../output/{filename}.json", "w") as f:
                json.dump(data, f)
        
    def generate_html_from_data(self, filename: str):
        """ Write html file
        Args:
            filename (str): file_path
        """
        with open(f"../output/{filename}.html", "wb") as f:
            if self.cE:
                f.write(self.gen_all_policies().encode("utf8"))
            if self.pE:
                f.write(self.gen_all_subjects().encode("utf8"))





# %%%%%%%%%%%%%%%%%

csv_path = './data/pages.csv'
s = Scraper(csv_path)
ce = CourseExtractor(s)
pe = PolicyExtractor(s)
# %%
api = 'https://www.gettysburg.edu/api/funnelback/courses/'
c_explore = CourseExplorer(s.request_json_from_api(api))

gen = Generator(ce, pe, c_explore)
gen.generate_json_from_data("output2")
gen.generate_html_from_data("output2")

# %%
