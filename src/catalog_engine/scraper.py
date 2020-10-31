"""
    @file scraper.py
    @author Alex Nguyen

    This file contain every scraper classes and methods

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
import os

class Scraper:
    """
    The scraper class will crawl all data from link
    """
    def __init__(self, csv_path, data_path='../data/'):
        """
        Args:
            csv_path (str): The path to the csv file that contains all link
        """
        super().__init__()
        self.csv_path = csv_path
        self.mapper = {}
        self.VERBOSE = True
        
        self.df = pd.read_csv(csv_path, names=['URL', 'Title', 'Notes']).iloc[:, :].reset_index()[["URL", "Title", "Notes"]]

        if not os.path.isdir(data_path + "html/"):
            os.mkdir(data_path + "html/")
        self.soup = self.scrape_src(data_path + "html/")
        
    def scrape_src(self, data_path_html=None) -> List[bs4.BeautifulSoup]:
        """Scrape every link from the csv file
        Returns:
            List[bs4.BeautifulSoup]: [description]
        """
        if self.VERBOSE:
            print("Crawling data from all links ...")
        # print("len: " + str(len(os.listdir(data_path_html))))


        soup = []
        for i, line in self.df.iterrows():
            uri = line["URL"]
            if uri.endswith(".pdf"):
                if self.VERBOSE:
                    print("Not crawling pdf file, continue...")
                continue
            
            if (os.path.exists(data_path_html + str(i) + ".html")):
                with open(data_path_html + str(i) + ".html", "rb") as f:
                    src = f.read()
            else:
                if self.VERBOSE:
                    print(f"Crawling Url: {uri}...")
                src = requests.get(uri).text
                with open(data_path_html + str(i) + ".html", "wb") as f:
                    f.write(src.encode("utf8"))
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

    def __str__(self):
        """From crawl data, generate the html string to be written to file.
        @Params:
        @Return: (str): String of the data
        """
        description = f"The data is at `self.soup` and the mapper (int, soup) from dataframe row num to the soup data"
        return description


class CourseURLScraper:
    """
    This class only crawl every course url from this link:
        "https://www.gettysburg.edu/academic-programs/curriculum/catalog/programs-of-study/"
        and extract links to csv file.
    """
    def __init__(self):
        self.uri = "https://www.gettysburg.edu/academic-programs/curriculum/catalog/programs-of-study/"
        self.soup: bs4.BeautifulSoup = self.scrape()
        self.links: List[str] = self.extract_link(self.soup)
    
    def scrape(self) -> bs4.BeautifulSoup:
        """Scrape source

        Returns:
            (bs4.BeautifulSoup): The soup for the source
        """
        src = requests.get(self.uri).text
        soup = bs4.BeautifulSoup(src, 'html.parser')
        return soup

    def extract_link(self, soup: bs4.BeautifulSoup) -> List[str]:
        links_soup = soup.find_all('a', {'href': re.compile(r"academic-programs")})
        links = []
        for link_soup in links_soup:
            links.append("https://www.gettysburg.edu" + str(link_soup['href']))
        return links

    def to_csv (self, path: str):
        """[summary]

        Args:
            path (str): [description]
        """
        df = pd.DataFrame(self.links)
        df.to_csv(path)

    def __str__(self):
        return str(self.links)