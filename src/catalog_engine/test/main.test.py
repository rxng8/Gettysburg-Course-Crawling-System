#  %%

import requests
import re
import bs4

# %%

url = 'https://www.gettysburg.edu/academic-programs/africana-studies/'

src = requests.get(url).text

soup = BeautifulSoup(src, 'html.parser')

dest = soup.find('div', class_="gb-u-bg-color-sapphire")

# %%%%%

dest['div']

# %%
data = '''<span>
  I Like
  <span class='unwanted'> to punch </span>
   your face
 <span>'''

from bs4 import BeautifulSoup as BS

soup = BS(data, 'html.parser')

external_span = soup.find('span')
# %%


print("1 HTML:", external_span)
print("1 TEXT:", external_span.text.strip())

unwanted = external_span.find('span')
unwanted.extract()

print("2 HTML:", external_span)
print("2 TEXT:", external_span.text.strip())


# %%

external_span

# %%

# %%

ce.data

# %%

len(ce.base_uri)

# %%%

# s.df.loc[idx[0]]["URL"]
# with open("test.html", "wb") as f:
#     f.write(s.mapper[0].encode('utf8'))

with open("test.html", "wb") as f:
    # f.write(mes.encode('utf8'))
    pass


# %%

s.mapper[0].find('div', class_="gb-u-spacing-bottom")
    


# %%
idx = ce.courses_index
# Test extrract
for i, id in enumerate(idx):
    soup = s.mapper[id]
    content = soup.find('div', {'class': 'gb-u-spacing-bottom'})
    if content is not None:
        print(content)
    break


# %%

# Test extract brief
dict_attr = ['Subject', 'Major', 'Minor', 'Brief']
data : List[Dict] = []

soup = s.mapper[0]
content = soup.find('div', {'class': 'gb-u-spacing-bottom'})
if content is not None:

    datum = {}
    datum['Subject'] = soup.find('h1', {'class': 'gb-c-hero__title'}).text
    datum['Major'] = "Major" in content.text
    datum['Minor'] = "Minor" in content.text
    # brief description may exist in a page or it may not
    brief = content.find('p', {'class': 'gb-u-type-p'})
    if brief:
        datum['Brief'] = brief
    print(datum['Brief'])

# %%

# Extract program pages
dict_attr = ['Description']
data : List[Dict] = []

soup = s.mapper[2]
if "Program" in soup.find('h1', {'class': 'gb-c-hero__title'}).text:
    content = soup.find('div', {'class': 'gb-u-spacing-quad-top'})
    datum['Description'] = str(content)
    print(datum)
# %%


# Extract courses pages
dict_attr = ['Code', 'Course', 'Content']
data : List[Dict] = []

soup = s.mapper[1]
if "Courses" in soup.find('h1', {'class': 'gb-c-hero__title'}).text:
    contents = soup.find_all('li', {'class': 'gb-c-accordion__item'})
    for content in contents:
        datum = {}
        datum['Code'] = str(content.find('span', {'class': 'gb-c-accordion__sub-heading'}))
        datum['Course'] = str(content.find('span', {'class': 'gb-c-accordion__heading'}))
        datum['Content'] = str(content.find('div', {'class': 'gb-c-accordion__content'}))
        print(datum)

# %%

# Test itterrow in df
for i, line in s.df.iterrows():
    print(str(line["Notes"]))
    break

# %%


s = "absd"

s.append("s")


# %%


# %%

with open ('target.html','wb') as target:
    message = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8" />
        <title>2020–21 Course Catalog</title>
    </head>
    <body>
    <h1>
        2020–21 Course Catalog 
    </h1>
    <p>
        <a href="https://www.gettysburg.edu/">Gettysburg College</a> 
    </p>
    <p>
        <a href="https://www.gettysburg.edu/academic-programs/curriculum/catalog/">Catalog</a> generated on $date. 
    </p>"""
    target.write(message.encode('utf8'))
