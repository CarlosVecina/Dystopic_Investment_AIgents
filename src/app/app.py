import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine
import streamlit as st

from src.data_ingestion.db.postgres_db import PostgresConfig

# Base de datos
load_dotenv()

# Page config
st.set_page_config(
    page_title="Dystopic Index - AIgenticFund",
    page_icon="📈",
    menu_items={
        "Get Help": "https://www.linkedin.com/in/carlos-vecina/",
    },
    layout="wide",
)

# Load csss
with open('./src/app/style.css') as f:
    css = f.read()
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# Define your javascript
#my_js = """
#alert("Hola mundo");
#"""

# Wrapt the javascript as html code
#my_html = f"<script>{my_js}</script>"

# Execute your app
#st.title("Javascript example")
#from streamlit.components.v1 import html
#html(my_html)

#st.markdown('<h1 class="title">👁 <br /> AIgentic Index <br /> for companies thriving in a  Dystopian Future</h1>', unsafe_allow_html=True)
st.markdown('<h1 class="title">👁 <br /> AIgents <br /> envisioning the Dystopian Future</h1>', unsafe_allow_html=True)


st.markdown('<h2  class="heading" style="text-align: center; color: grey;">Betting for or against it, it s up to <span class="underline--magical">You!</span></h2>', unsafe_allow_html=True)


st.write("<br></br>", unsafe_allow_html=True)
col1 = st.columns([1])

load_dotenv()

db_uri = PostgresConfig(
    host=os.environ["SB_DDBB_HOST"],
    port=os.environ["SB_DDBB_PORT"],
    database=os.environ["SB_DDBB_DATABASE"],
    user=os.environ["SB_DDBB_USER"],
    password=os.environ["SB_DDBB_PWD"],
).get_connection_string()


@st.cache_data
def load_data(query, db_uri):
    engine = create_engine(db_uri)
    df = pd.read_sql(query, engine)
    return df


with col1[0]:
    st.markdown("<h2 style='color: black;'><span class='underline--magical'> Current portfolio</span></h2>", unsafe_allow_html=True)
    df = load_data(
        "SELECT * FROM portfolio WHERE created_at = (SELECT max(created_at) FROM portfolio)",
        db_uri,
    )
    st.text(f"Updated date {df['created_at'].values[0].astype('datetime64[D]')}")
    st.dataframe(
        df[["stock_name", "weight"]], hide_index=True, use_container_width=True
    )

    st.markdown("<h2 style='color: black;'><span class='underline--magical'>Manager AIgent narrative</span></h2>", unsafe_allow_html=True)

    st.markdown("<h2 style='color: black;'><span class='underline--magical'>Past performance</span></h2>", unsafe_allow_html=True)
