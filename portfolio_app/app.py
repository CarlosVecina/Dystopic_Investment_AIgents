import datetime
import os

import pandas as pd
import plotly.express as p
import plotly.graph_objs as go
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

from dystopic_investment_aigents.data_ingestion.db.postgres_db import PostgresConfig
from dystopic_investment_aigents.utils.portfolio_utils import (expand_df_dates,
                                       generate_portfolio_evolution)

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
with open("./portfolio_app/style.css") as f:
    css = f.read()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Define your javascript
# my_js = """
# alert("Hola mundo");
# """

# Wrapt the javascript as html code
# my_html = f"<script>{my_js}</script>"

# Execute your app
# st.title("Javascript example")
# from streamlit.components.v1 import html
# html(my_html)

# st.markdown('<h1 class="title">👁 <br /> AIgentic Index <br /> for companies thriving in a  Dystopian Future</h1>', unsafe_allow_html=True)
st.markdown(
    '<h1 class="title">👁 <br /> AIgents <br /> envisioning the Dystopian Future</h1>',
    unsafe_allow_html=True,
)


st.markdown(
    '<h2  class="heading" style="text-align: center; color: grey;">Betting for or against it, it s up to <span class="underline--magical">You!</span></h2>',
    unsafe_allow_html=True,
)


st.write("<br></br>", unsafe_allow_html=True)
col1 = st.columns([1])


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
    # 1. CURRENT PORFOLIO
    st.markdown(
        "<h2 style='color: black;'><span class='underline--magical'> Current portfolio</span></h2>",
        unsafe_allow_html=True,
    )
    df_portfolio = load_data(
        "SELECT * FROM portfolio WHERE created_at = (SELECT max(created_at) FROM portfolio)",
        db_uri,
    )
    st.text(
        f"Updated date {df_portfolio['created_at'].values[0].astype('datetime64[D]')}"
    )
    st.dataframe(
        df_portfolio[["asset_name", "weight"]],
        hide_index=True,
        use_container_width=True,
    )

    # 2. NARRATIVE
    st.markdown(
        "<h2 style='color: black;'><span class='underline--magical'>Manager AIgent narrative</span></h2>",
        unsafe_allow_html=True,
    )

    # 3. PAST PERFORMANCE
    st.markdown(
        "<h2 style='color: black;'><span class='underline--magical'>Past performance</span></h2>",
        unsafe_allow_html=True,
    )

    df_current_portfolio = df_portfolio.copy()
    df_current_portfolio["date"] = df_current_portfolio[
        "created_at"
    ].dt.date.astype("datetime64[ns]") - datetime.timedelta(days=60)
    df_current_portfolio = generate_portfolio_evolution(
        df_current_portfolio, "2024-06-01", "2024-07-27", "left"
    )
    df_current_portfolio.drop(columns=["created_at"], inplace=True)

    df_prices = load_data(
        "SELECT * FROM stock_price_daily WHERE date >= '2024-06-01'",
        db_uri,
    )
    df_prices["asset_short_name"] = df_prices["ticker"]
    df_prices["date"] = df_prices["date"].astype("datetime64[ns]")

    # 3.1 merge dfs and agg computation
    df_merged = pd.merge(
        df_current_portfolio,
        df_prices,
        on=["asset_short_name", "date"],
        how="left",
    )
    df_merged["value"] = df_merged["weight"] * df_merged["close"]
    agg_portfolio_value = df_merged.groupby(["date"], as_index=False).agg(
        {"value": "sum"}
    )
    agg_portfolio_value = agg_portfolio_value[agg_portfolio_value["value"] > 0]
    agg_portfolio_value["value_perc_vs_init"] = (
        (agg_portfolio_value["value"] - agg_portfolio_value["value"][0])
        / agg_portfolio_value["value"][0]
        * 100
    )

    # 📈 3.2 Portfolio performance Plot
    negative_traces_df = expand_df_dates(
        agg_portfolio_value[agg_portfolio_value["value_perc_vs_init"] < 0],
        "date",
        agg_portfolio_value.date.tolist()[0],
        agg_portfolio_value.date.tolist()[-1],
        "both",
    )

    fig = p.line(
        agg_portfolio_value,
        x="date",
        y="value_perc_vs_init",
        title="Dystopic Portfolio Performance Evolution",
    )
    fig.add_trace(
        go.Scatter(
            x=negative_traces_df.date,
            y=negative_traces_df.value_perc_vs_init,
            connectgaps=True,
            name="negative",
            showlegend=False,
        ),
    )
    fig.update_traces(
        selector=lambda x: x["name"] != "negative", line_color="#147852"
    )
    fig.update_traces(
        selector=lambda x: x["name"] == "negative", line_color="#c61a09"
    )
    fig.update_legends(overwrite=True)

    st.plotly_chart(fig)
