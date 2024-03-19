import pandas as pd
import re
import dhlab.api.dhlab_api as api
import dhlab as dh
import sqlite3
import streamlit as st
from PIL import Image
import images_similarity as ims
import re
from IPython.display import HTML
from st_clickable_images import clickable_images

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

def link(item):
    """A list of urls in r is displayed in a grid layout with specified number of rows and columns."""
    base = "https://www.nb.no/items/"
    urnstring = re.findall("URN[^/]*", item)[0]
    prefix, doctyp, urn, page = urnstring.split('_')
    return f"{base}{prefix}_{doctyp}_{urn}?page={int(page) + 1}"
        

@st.cache_data(show_spinner = False)
def get_pictures(text="", hits = 10):
    return ims.image(search=text, hits=hits)

@st.cache_data(show_spinner = False)
def similar(image_url="", limit = 10):
    return ims.sim_image(image_url=image_url, limit=limit)


st.set_page_config(page_title="Images", layout="wide", initial_sidebar_state="auto", menu_items=None)
st.session_state.update(st.session_state)

st.header("Illustrasjoner i bøker før 1900")
st.markdown("Finn bilder i bøker med tekstsøk, og bruk bildene til å finne lignende bilder")
col1, col2, col3, col4 = st.columns([5,2,2,2])

if "search" not in st.session_state:
    st.session_state['search'] = 'luftsprang'
if "distance" not in st.session_state:
    st.session_state['distance'] = 5
if "image_size" not in st.session_state:
    st.session_state["image_size"] = 150
if "sortby" not in st.session_state:
    st.session_state["sortby"] = "relevans"

if "target" not in st.session_state:
    st.session_state['target'] = ""

if "book_click" not in st.session_state:
    st.session_state['book_click'] = -1
if "sim_click" not in st.session_state:
    st.session_state['sim_click'] = -1

if "previous_book_click" not in st.session_state:
    st.session_state['previous_book_click'] = -1
if "previous_sim_click" not in st.session_state:
    st.session_state['previous_sim_click'] = -1
if "sim_click_changed" not in st.session_state:
    st.session_state['sim_click_changed'] = False

#st.write("simclick changed", st.session_state.sim_click_changed)


with col1:
    search = st.text_input(
        'Skriv en liste med ord eller fraser for å finne illustrasjoner i nærheten av frasen/ordene', 
        st.session_state.search, 
        key='search', 
        help="For å lage fraser sett ordene i anførselstegn. Det kan være lurt å benytte såkalt trunkert søk. For å få treff på alle ord som starter med _krig_, søk etter _krig*_.")

with col2:
    dist = st.number_input(
        "Avstand mellom ord/fraser", 
        min_value=0, 
        max_value=500, 
        value=st.session_state.distance,
        key="distance",
        help="Ved å sett 0 kan det ikke komme noen ord mellom, med 5 kan det være alt inntil 5 ord mellom - verdiene kan ligge mellom 0 og 500")

with col3:
    part = st.number_input(
        "Størrelse på visning", 
        min_value = 50, 
        max_value = 1500, 
        value = st.session_state.image_size,
        step = 50,
        key = "image_size",
        help = "Finn en passende verdi")

with col4:
    columns = st.number_input(
        "Antall treff", 
        min_value = 1,
        max_value = 50,
        value = st.session_state.get('cols',10),
        key='cols')

search = f"NEAR({search}, {dist})"
resbook = [x[0] for x in ims.image(search,hits=st.session_state.get('cols')).values()]

#st.image(resbook, width=part, caption=list(range(len(resbook))))

#####
##### Display search pane
#####

st.session_state.book_click = clickable_images(
    resbook,
    titles=[f"Klikk for lignende" for i in resbook],
    div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
    img_style={"margin": "2px", "height": f"{part}px"},
    key = "search_images"
)

####
#### Change the click pane 
####

#st.write(st.session_state.previous_book_click, st.session_state.book_click)
book_click_changed = st.session_state.previous_book_click != st.session_state.book_click 
st.session_state.previous_book_click = st.session_state.book_click

if book_click_changed:
    #st.write('pane 1 book!!!')
    st.session_state.target = resbook[st.session_state.book_click]
    st.session_state.similar = [x[0] for x in similar(st.session_state.target, 20)]



st.markdown("## Lignende bilder")

# if st.session_state.target != "" :
#     st.markdown(f"Informasjon om valgte bilde {link(st.session_state.target)} ")
#     #st.markdown(f"""![Valgte bilde]({st.session_state.target}#center)""")
# else:
#     st.session_state.similar = []
col1, col2, col3 = st.columns([3,3,3])
if st.session_state.target != "":
    with col2:
        st.markdown(f"""![Valgte bilde]({st.session_state.target}#center)""")
        st.markdown(f"Gå til boken {link(st.session_state.target)} ")
    st.session_state.sim_click = clickable_images(
        st.session_state.similar,
        titles=[f"Klikk for lignende" for i in range(len(st.session_state.similar))],
        div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
        img_style={"margin": "2px", "height": f"{part}px"},
        key="similar_images"
    )

st.session_state.sim_click_changed = st.session_state.previous_sim_click != st.session_state.sim_click
#st.write(st.session_state.previous_sim_click, st.session_state.sim_click)
st.session_state.previous_sim_click = st.session_state.sim_click

if st.session_state.sim_click_changed:
    st.session_state.target = st.session_state.similar[st.session_state.sim_click]
    st.session_state.similar = [x[0] for x in similar(st.session_state.target, 20)]
    st.rerun()
    
