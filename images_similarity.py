#!/usr/bin/env python
# coding: utf-8

import requests
import pandas as pd
import re
from IPython.display import HTML



base_url = "https://api.nb.no/dhlab/similarity"


def display_finds(r, num_rows, num_columns, width=500):
    """A list of urls in r is displayed in a grid layout with specified number of rows and columns."""
    base = "https://www.nb.no/items/"
    # Initialize the rows list which will contain HTML string for each row
    rows_html = []
    # Calculate total number of items to display, based on the specified rows and columns
    total_items = num_rows * num_columns
    # Ensure we don't try to display more items than we have
    r = r[:total_items]
    
    # Split the list into rows with the specified number of columns
    for row_start in range(0, len(r), num_columns):
        row_items = r[row_start:row_start+num_columns]
        # For each row, create a list of cell HTML strings
        cells_html = []
        for i, item in enumerate(row_items):
            urnstring = re.findall("URN[^/]*", item)[0]
            prefix, doctyp, urn, page = urnstring.split('_')
            cell_html = f"<td><a href='{base}{prefix}_{doctyp}_{urn}?page={int(page) + 1}' target='_'><img src='{item}' width={width}></a>{row_start+i}</td>"
            cells_html.append(cell_html)
        # Join the cell HTML strings into a row and add it to the rows list
        rows_html.append(f"<tr>{' '.join(cells_html)}</tr>")

    # Join all rows into the final HTML table
    html_table = f"<table>{' '.join(rows_html)}</table>"
    return HTML(f"""<html><head></head><body>{html_table}</body></html>""")
import numpy as np


# In[3]:


def collections():
    r = requests.get(f"{base_url}/collections")
    if r.status_code == 200:
        res = r.text
    else:
        res = ""
    return res


# In[4]:


def words(word=None, collection_name=None):
    params = locals()
    r = requests.get(f"{base_url}/sim_words", params=params)
    if r.status_code == 200:
        res = pd.DataFrame(r.json(), columns=['word','score'])
    else:
        res = pd.DataFrame()
    return res


# In[25]:


def image(search=None, hits=10):
    params = locals()
    r = requests.get(f"{base_url}/images", params=params)
    if r.status_code == 200:
        res = r.json()
    else:
        print(r.status_code)
        res = ""
    return res


# In[28]:


def sim_image(image_url=None, limit=10):
    params = locals()
    r = requests.get(f"{base_url}/sim_images", params=params)
    if r.status_code == 200:
        res = r.json()
    else:
        print(r.status_code)
        res = ""
    return res









