""" This file contain data structure for block setting
    @deprecated
"""

from typing import List, Dict
import json

# Deprecated
class BlockSetting:
    """ Configuration in order for a block of element to be selected by bs4.
    Reference: https://www.crummy.com/software/BeautifulSoup/bs4/doc/#searching-by-css-class
    What should it be, how is the architecture of Block Setting, what can it be?
    """

    def __init__(self, method: str, tag: str, block_type: str) -> None:
        """ [description]

        Args:
            method (str): [description]
            tag (str): [description]
            block_type (str): [description]
        """
        self.method = method
        self.tag = tag
        self.block_type = block_type

class PageLocator:
    """ The setting for the whole page
    """

    def __init__(self, html_tag: str, css_class: str, exclude_list: List[Dict]=None) -> None:
        self.html_tag: str = html_tag
        self.css_class: List[str] = css_class.split(" ")
        self.exclude_list = exclude_list
        if self.exclude_list == None:
            self.exclude_list = []

        # Have not been used. Deprecated
        self.settings: List[BlockSetting] = []

    def push_setting(self, setting: BlockSetting):
        self.settings.append(setting)

    def pop_setting(self):
        self.settings.pop()

    def process_exclude_list(self):
        pass