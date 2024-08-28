# Dystopic Investment AIgents

Dystopic stock &amp; investment indexes 📈 managed by AI agents 🤖.

Welcome to Dystopic Investment AIgents, where dystopic stock and investment indexes are managed by AI agents. Our project is an innovative endeavor that combines data engineering with artificial intelligence to provide insights and manage investments in a dystopian-themed environment.

The project is composed by two main components: data ingestion and AI agents. 

<br>

## ➡️☁️ Data ingestion (Orchestated load and transform with Mage AI)

As a summary, we need different information sources as:
- Stock prices
- Market news (both for traded stocks & pre-IPO startups)
- Startup platforms. For now implemented:
    - Crunchbase
    - Product Hunt
- Financial reports (TBD)
- Newsletters & social feeds (TBD)

We are gathering all the financial context as possible, to make it available for the agents afterwards. Some of them would make use of macro data to detect investment trends and market sentiments, while others would be the owners of specific & optimized market actions with the price and micro data.

- [Data Ingestion README](./dystopic_investment_aigents/data_ingestion/README.md)

<br>

## 🕵️🕵️Agents

- [Agents README](./dystopic_investment_aigents/agents/README.md)
