# Dystopic Investment AIgents

**AI agents fully manage the Fund**, predicting dystopian futures and uncovering the companies ready to dominate them.

The project consists of two main components: data ingestion and AI agent workflows.

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

If you want to run the agents, you can do it with `make install-agents` and `make run-fund`.

- [Agents README](./dystopic_investment_aigents/agents/README.md)
