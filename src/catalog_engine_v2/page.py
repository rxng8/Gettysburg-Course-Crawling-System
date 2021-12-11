""" @author: Alex Nguyen
  @file: page.py
  This class is for the data structure.
"""

from typing import List, Dict
import requests
import bs4

from .setting import BlockSetting, PageLocator
from .const import PAGE_TAG, PAGE_TAG_TO_DEFAULT_LOCATOR_NAME, HTML_TAG_NAME


class Page:
  """ This is the page class
  
  """
  
  def __init__(self, page_tag: PAGE_TAG, html_id, header_level, url, locators_data) -> None:
    # For debuggin purpose
    self.logging: List[str] = []
    
    # Main variables
    self.html_id = html_id # the unique id of that page, which is also on the template
    self.page_tag = page_tag
    self.header_level: str = header_level
    self.url = url
    self.soup: bs4.BeautifulSoup = None
    self.crawl_success = self.__crawl()
    self.locators_data = locators_data
    self.locator: PageLocator = self.__get_locator()
    
    # Content to be shown out
    self.content = self.__extract()

  def __crawl(self) -> bool:
    """ Crawl and return whether it has been crawled

    Returns:
        bool: Whether the source has been crawled
    """
    if self.url.endswith(".pdf"):
      if self.VERBOSE:
        print("Not crawling pdf file, continue...")
      return False
    src = requests.get(self.url).text
    self.soup = bs4.BeautifulSoup(src, 'html.parser')
    return True

  def __get_locator(self) -> PageLocator:
    # This method figures out the actual tag of the page and the coresponding css class of the page using defaults and human-defined parameters.
    
    # For example, we try to do the page with id `africana-studies-program-description`
    # return PageLocator("div", "gb-c-longform gb-u-spacing-triple gb-u-spacing-double-bottom")
    
    # If it is a special case
    if self.html_id in self.locators_data["data"].keys():
      self.logging.append("Special locator case")
      default_locator_name = self.html_id
      page_locator_data = self.locators_data["data"][default_locator_name]
      return PageLocator(
        html_tag=page_locator_data["data"]["html_tag"],
        css_class=page_locator_data["data"]["css_class"],
        exclude_list=page_locator_data["exclude"] if "exclude" in page_locator_data else None
      )
    # Else, it is a default cases
    else:
      assert self.page_tag in PAGE_TAG_TO_DEFAULT_LOCATOR_NAME.keys(), "Wrong behavior"
      self.logging.append("Default locator case")
      # For example, `DEFAULT_CONFIG_COURSE_MAIN` in locators.json
      default_locator_name = PAGE_TAG_TO_DEFAULT_LOCATOR_NAME[self.page_tag]
      page_locator_data = self.locators_data["data"][default_locator_name]
      return PageLocator(
        html_tag=page_locator_data["data"]["html_tag"],
        css_class=page_locator_data["data"]["css_class"],
        exclude_list=page_locator_data["exclude"] if "exclude" in page_locator_data else None
      )

  def __extract(self):
    page_content = self.soup.find(self.locator.html_tag, {'class': self.locator.css_class})

    if page_content == None:
      return "[CONTENT BLANK]"
    self.logging.append(f"Root page attrs: {str(page_content.attrs)}")
    # page_content.attrs = {}

    # Debug
    # if self.html_id == "music-sunderman-conservatory-program-description":
    #   print(self.locator.exclude_list)

    # First, exclude every excluding tag specified in the locator!
    for i, excluding_tag in enumerate(self.locator.exclude_list):
      if "from" in excluding_tag:
        # TODO: Fix this bug
        # print(self.__str__())
        # tag = page_content.find(excluding_tag["from"]["html_tag"])
        
        # if "css_class" in excluding_tag["from"] and len(excluding_tag["from"]["css_class"].split()) != 0:
        #   tag = page_content.find(excluding_tag["from"]["html_tag"], {"class": excluding_tag["from"]["css_class"].split()})
        # print(f"This is tag: ___ {tag}")
        # if "inclusive" in excluding_tag["from"] and excluding_tag["from"]["inclusive"]:
        #   tag.extract()
        # for t in tag.find_next_siblings():
        #   print(f"[taggaga] _____ {t}")
        #   t.extract()
        pass
      elif "to" in excluding_tag:
        # TODO: Fix this bug
        # NOTE: Untested code
        # print(self.__str__())
        # tag = page_content.find_all(recursive=False)[0]
        # stop = True
        # for t in tag.find_next_siblings():
        #   if t.name == excluding_tag["to"]["html_tag"]:
        #     for css_attr in t.attrs["class"]:
        #       if css_attr not in excluding_tag["to"]["css_class"].split():
        #         stop = False
        #         break
        #   else:
        #     stop = False
          
        #   t.exclude()
        #   if stop:
        #     break
        pass
        
      # Else, it is just normal tag excluding
      else:
        assert "html_tag" in excluding_tag and "css_class" in excluding_tag, "Wrong behavior excluding locators."
        tags = page_content.find_all(excluding_tag["html_tag"], {"class": excluding_tag["css_class"].split(" ")})
        for tag in tags:
          tag.extract()
    
    # Second 
    # TODO: Work on this
    # Array data to keep track of the current heading level of the page

    # Maximum heading level of the original page, always be the first heading_n
    # (h) 1 < 2 < 3 < 4 < 5 < 6
    max_heading_level = 0

    for tag in page_content.find_all(): # We want to process recursively here.
      
      # tag name is one of the h_n with n from 1 to 6 inclusive
      # Use for the second elif
      list_h_n = list(str(tag.name).lower())

      # First, process accordingly to different tag names.
      if tag.name == HTML_TAG_NAME.img or \
          tag.name == HTML_TAG_NAME.hr or \
          tag.name == HTML_TAG_NAME.button or \
          tag.name == HTML_TAG_NAME.rect or \
          tag.name == HTML_TAG_NAME.svg:
          # or tag.name == HTML_TAG_NAME.br:
        self.logging.append(f"Removed img or hr tag.")
        tag.extract()
      # tag name is one of the h_n with n from 1 to 6 inclusive
      elif list_h_n[0] == "h":
        original_heading_level = int(list_h_n[1])
        assert original_heading_level <= 6 and original_heading_level >= 1, "Wrong behavior heading level"
        # Process something to put to result content
        if max_heading_level == 0:
          max_heading_level = original_heading_level
        
        # When we have max heading level, we will have original_heading_level - max_heading_level as the
        # difference of level between max level, and plus 1 to get the difference + 1
        # We now can plus those differneces to the current desired page heading level
        desired_page_heading_level_list_h_n = list(str(self.header_level).lower())
        desired_page_heading_level = int(desired_page_heading_level_list_h_n[1]) + original_heading_level - max_heading_level + 1
        
        # Set new tag name
        tag.name = "h" + str(desired_page_heading_level)
        # pass
      # elif tag.name == HTML_TAG_NAME.h1:
      #   pass
      elif tag.name == HTML_TAG_NAME.p and tag.text.strip() == "" and len(tag.find_all()) == 0: # Extract the blank 'p' tag
        tag.extract()
      else:
        pass

      # Lastly, rmeove all attributes except for urls:
      if tag.name != HTML_TAG_NAME.a:
        self.logging.append(f"Remove attributes")
        tag.attrs = {}
      else:
        self.logging.append(f"Leave tag link: {tag.href}")
        if "href" in tag.attrs:
          # TODO: We also need to add the host name gettysburg.edu to every urls that does not contains them
          this_url = tag.attrs["href"]
          if this_url[0] == "/":
            this_url = "https://www.gettysburg.edu" + this_url

          # Exclude all other attributes except for href
          tag.attrs = {"href": this_url} 
          
    self.logging.append(f"{page_content}")
    return page_content
  
  def get_subject_abbrs(self) -> List[str]:
    """ Look in a course page and get as many different subject abbreviation as possible

    Returns:
        List[str]: List of the subject abbreviations. E.g: ["ARTS", "ARTH"]
    """
    result_abbrs: List[str] = []
    # print(f"[COURSE EXPLORER] soup: {self.soup}")
    accordion_groups = self.soup.find_all("ul", {"class": "gb-c-accordion__group"})
    # print(f"[COURSE EXPLORER] Accordion group: {accordion_groups}")
    for group in accordion_groups:
      first_course_in_group = group.find("li", {"class": "gb-c-accordion__item"})
      # print(f"[COURSE EXPLORER] first_course_in_group: {first_course_in_group}")
      course_code = first_course_in_group.find("button").find("span", {"class": "gb-c-accordion__sub-heading"}).text
      # print(f"[COURSE EXPLORER] course_code: {course_code}")
      abbr = course_code.split("-")[0]
      # print(f"[COURSE EXPLORER] abbr: {abbr}")
      result_abbrs.append(abbr)
    return result_abbrs

  def __str__(self) -> str:
    return f"[Page] Unique id: {self.html_id}, this page's header is {self.header_level}."

  def generate(self) -> str:
    return self.content