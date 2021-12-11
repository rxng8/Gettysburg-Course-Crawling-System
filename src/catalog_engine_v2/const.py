""" @author: Alex Nguyen
  const.py
"""

from enum import Enum

from .setting import BlockSetting

# class TAG:
#   COURSE = "COURSE"
#   POLICY = "POLICY"
#   FACULTY = "FACULTY"
#   COURSE_PROG = "COURSE_PROG"
#   COURSE_REQ = "COURSE_REQ"
#   COURSE_CLS = "COURSE_CLS"
#   COURSE_MAIN = "COURSE_MAIN"

class PAGE_TAG(Enum):
  POLICY = "POLICY"
  FACULTY = "FACULTY"
  COURSE_PROG = "COURSE_PROG"
  COURSE_REQ = "COURSE_REQ"
  COURSE_CLS = "COURSE_CLS"
  COURSE_MAIN = "COURSE_MAIN"

PAGE_TAG_TO_DEFAULT_LOCATOR_NAME = {
  PAGE_TAG.POLICY: "DEFAULT_CONFIG_POLICIES",
  PAGE_TAG.FACULTY: "DEFAULT_CONFIG_FACULTY",
  PAGE_TAG.COURSE_PROG: "DEFAULT_CONFIG_COURSE_PROG",
  PAGE_TAG.COURSE_REQ: "DEFAULT_CONFIG_COURSE_REQ",
  PAGE_TAG.COURSE_CLS: "DEFAULT_CONFIG_COURSE_CLS",
  PAGE_TAG.COURSE_MAIN: "DEFAULT_CONFIG_COURSE_MAIN",
}

# Unused
PAGE_TAG_TO_DEFAULT_LOCATOR_IDS_LIST = {
  PAGE_TAG.POLICY: "IDS_FOR_DEFAULT_POLICIES",
  PAGE_TAG.FACULTY: "IDS_FOR_DEFAULT_FACULTY",
  PAGE_TAG.COURSE_PROG: "IDS_FOR_DEFAULT_COURSE_PROG",
  PAGE_TAG.COURSE_REQ: "IDS_FOR_DEFAULT_COURSE_REQ",
  PAGE_TAG.COURSE_CLS: "IDS_FOR_DEFAULT_COURSE_CLS",
  PAGE_TAG.COURSE_MAIN: "IDS_FOR_DEFAULT_COURSE_MAIN",
}

# Deprecated
class PAGE_SETTINGS:
  # COURSE_CLS_TXT = BlockSetting()
  # COURSE_REQ_TXT = BlockSetting()
  COURSE_DES_TXT = BlockSetting("", "gb-c-longform gb-u-spacing-triple gb-u-spacing-double-bottom", "text")
  # FACULTY_TXT = BlockSetting()
  # POLICY_TXT = BlockSetting()
  pass

# Configuration with each type of tag
class HTML_TAG_NAME:
  a = "a"
  b = "b"
  br = "br"
  p = "p"
  ul = "ul"
  li = "li"
  ol = "ol"
  img = "img"
  code = "code"
  div = "div"
  svg = "svg"
  span = "span"
  button = "button"
  rect = "rect"
  hr = "hr"
  h1 = "h1"
  h2 = "h2"
  h3 = "h3"
  h4 = "h4"
  h5 = "h5"
  h6 = "h6"
  strong = "strong"
  body = "body"
  head = "head"
  html = "html"

class COURSE_CRAWLING_MODE:
  raw = "raw"
  api = "api"

FUNNELBACK_COURSE_API = "https://www.gettysburg.edu/api/funnelback/courses/"

DEFAULT_SAVED_PICKLE_PAGE_DATA_FILE_NAME = "id_to_page.pickle"