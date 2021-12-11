""" @author: Alex Nguyen
  @file: template.py
  This file work extract the information from the template 
"""

import os
from typing import Dict
import bs4
from bs4 import BeautifulSoup
# import pickle
import dill as pickle

from .const import *
from .page import Page
from .utils import load_json_locators, request_json_from_api
from .explorer import CourseExplorer, CoursePage

class Template:
  """ This class is the template extractor
  """
  
  def __init__(
      self, 
      template_path: str, 
      locators_path: str, 
      course_crawling_mode=COURSE_CRAWLING_MODE.raw, 
      course_explorer: CourseExplorer = None,
      data_path: str=None,
      verbose=True
    ) -> None:
    """ initializer

    Args:
      template_path (str): Path to template file. Defaults to '../data/template.html'.
    """
    self.template_path = template_path
    self.locators_path = locators_path
    self.n_links = 0
    self.toc: str = ""
    self.pages = []
    self.title = ""
    self.course_crawling_mode = course_crawling_mode # either "api" or "raw"
    self.course_explorer = course_explorer
    self.verbose = verbose
    self.locators_data = self.__load_locators()
    self.template_src = self.__read_template_file(self.template_path)
    self.data_path = data_path

    if not os.path.exists(data_path):
      os.mkdir(data_path)

    # The actual data
    self.id_to_page: Dict[str, Page] = {}

  def __read_template_file(self, path) -> str:
    src = ""
    with open(path, "rb") as f:
      src = f.read()
    
    if not src:
      if self.verbose:
        print("Cannot read template file")
      return None
    
    return src

  def __load_locators(self) -> Dict:
    data = load_json_locators(self.locators_path)
    # TODO: check if locators is a proper structure
    if data:
      return data
    return None

  def insight(self):
    # TODO: Currently reaching maximum recursion depth, CAUSING ERROR
    # id_to_page_path = os.path.join(self.data_path, DEFAULT_SAVED_PICKLE_PAGE_DATA_FILE_NAME)
    # # If the data exists, no need to crawl any more
    # if os.path.exists(id_to_page_path):
      
    #   with open(id_to_page_path, "rb") as f:
    #     self.id_to_page = pickle.load(f)
    #   print("The data exists, simply load the data.")
    #   return

    soup = BeautifulSoup(self.template_src, 'html.parser')
    toc_soup = BeautifulSoup(self.template_src, 'html.parser').body
    all_content_soup = BeautifulSoup(self.template_src, 'html.parser').body

    # Extract the toc by the `\<hr\>` tag => in toc_soup
    hr_separator = toc_soup.find_all('hr')[0]
    for tag in hr_separator.find_next_siblings():
      tag.extract()
    hr_separator.extract()

    # Test toc -> ok
    # for i, tag in enumerate(toc_soup.find_all()):
    #   print(f"{i}: {tag}")

    # Extract the body by the `\<hr\>` tag => in all_content_soup
    hr_separator = all_content_soup.find_all('hr')[0]
    for tag in hr_separator.find_previous_siblings():
      tag.extract()
    hr_separator.extract()

    # Loop through every elements
    first_tag_pointer = all_content_soup.find_all()[0]
    # print(first_tag_pointer)
    current_page_header: bs4.BeautifulSoup = None
    for i, tag in enumerate(first_tag_pointer.find_next_siblings()):

      # Debugging for courses pages only
      # if i < 80:
      #   continue

      # print(f"{i}: {tag}")

      # If it is contained in a div, then it is a link
      if tag.name == 'div':
        assert "id" in current_page_header.attrs, "Unexpected error: Wrong current_page_header behavior!"
        # Create a page
        url = tag.find("a") # Get the first and only link
        this_page = Page(
          page_tag=PAGE_TAG.COURSE_PROG,
          html_id=current_page_header["id"],
          header_level=current_page_header.name,
          locators_data=self.locators_data,
          url=url["href"]
        )
        self.id_to_page[current_page_header["id"]] = this_page
        if self.verbose:
          print(this_page)

      # Otherwise, it is a header
      else:
        current_page_header = tag
        # print(current_page_header)

      # if i == 150:
      #   break
    
    # Save the pickle serialized data inside the data folder
    # TODO: Currently reaching maximum recursion depth, CAUSING ERROR
    # self.__save_id_to_page_data()

  def clear_cached_data(self):
    id_to_page_path = os.path.join(self.data_path, DEFAULT_SAVED_PICKLE_PAGE_DATA_FILE_NAME)
    if os.path.exists(id_to_page_path):
      os.remove(id_to_page_path)

  def __save_id_to_page_data(self):
    id_to_page_path = os.path.join(self.data_path, DEFAULT_SAVED_PICKLE_PAGE_DATA_FILE_NAME)
    with open(id_to_page_path, "wb") as f:
      pickle.dump(self.id_to_page, f)

  def show_temporary_result(self) -> None:
    """ Show the user the webdriver of the resulted generated website
    """
    # Driver - which can show the website temporarily using seleniums - class involved?
    pass

  def generate(self) -> str:
    content = ""
    
    soup = BeautifulSoup(self.template_src, 'html.parser')
    toc_soup = BeautifulSoup(self.template_src, 'html.parser').body
    all_content_soup = BeautifulSoup(self.template_src, 'html.parser').body

    # Extract the toc by the `\<hr\>` tag => in toc_soup
    hr_separator = toc_soup.find_all('hr')[0]
    for tag in hr_separator.find_next_siblings():
      tag.extract()
    hr_separator.extract()

    # Test toc -> ok
    # for i, tag in enumerate(toc_soup.find_all()):
    #   print(f"{i}: {tag}")

    # Extract the body by the `\<hr\>` tag => in all_content_soup
    hr_separator = all_content_soup.find_all('hr')[0]
    for tag in hr_separator.find_previous_siblings():
      tag.extract()
    hr_separator.extract()

    # Loop through every elements
    first_tag_pointer = all_content_soup.find_all()[0]
    # print(first_tag_pointer)
    current_course_subject: str = None
    current_page_header: bs4.BeautifulSoup = None
    for i, tag in enumerate(first_tag_pointer.find_next_siblings()):
      # If it is contained in a div, then it is a link
      if tag.name == 'div':
        if current_page_header.text.strip() == "Courses": # If it is courses crawling, then we have two cases
          if self.course_crawling_mode == COURSE_CRAWLING_MODE.api:
            # TODO: Working on course crawling api here
            # Exclude the link
            tag_link = tag.find("code")
            tag_link.extract()

            # Create a new course page (department name)
            course_page = CoursePage(subject_name=current_course_subject, data=self.course_explorer.data)
            # print(course_page)
            for page_child_tag in course_page.gen_all_courses_for_this_subject().find_all(recursive=False):
              # print("hello")
              tag.append(page_child_tag)
                
          elif self.course_crawling_mode == COURSE_CRAWLING_MODE.raw:
            # We are generating based on raw html crawled pages
            if current_page_header["id"] in self.id_to_page.keys():
              # Exclude the link
              tag_link = tag.find("code")
              tag_link.extract()

              # Append the content of that page into the children list of the tag
              # tag.append(self.id_to_page[current_page_header["id"]].generate())

              # Append each piece of the content of that page into the children list of the tag
              for page_child_tag in self.id_to_page[current_page_header["id"]].generate().find_all(recursive=False):
                tag.append(page_child_tag)
                pass
        else: # else, we have one case!
          if current_page_header["id"] in self.id_to_page.keys():
            # Exclude the link
            tag_link = tag.find("code")
            tag_link.extract()

            # Append the content of that page into the children list of the tag
            # tag.append(self.id_to_page[current_page_header["id"]].generate())

            # Append each piece of the content of that page into the children list of the tag
            for page_child_tag in self.id_to_page[current_page_header["id"]].generate().find_all(recursive=False):
              tag.append(page_child_tag)

      # Otherwise, it is a header
      else:
        current_page_header = tag
        # print(self.course_explorer.subjects_dict)
        # print(f"Searching {tag.text.strip()} to {self.course_explorer.subjects_dict.keys()} => {tag in self.course_explorer.subjects_dict.keys()}")
        
        if tag.text.strip() in self.course_explorer.subjects_dict.keys():
          current_course_subject = tag.text.strip()
          # print(current_course_subject)

    toc_soup.append(all_content_soup)
    return toc_soup
    