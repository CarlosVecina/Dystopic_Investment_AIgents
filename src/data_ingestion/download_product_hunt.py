import time
from typing import Any
import dotenv
import requests
import os
from pydantic import BaseModel
import schedule
import pandas as pd


dotenv.load_dotenv()
PHUNT_API_TOKEN = os.environ["PHUNT_API_TOKEN"]


class PHuntProduct(BaseModel):
    id: str
    name: str
    description: str
    url: str
    n_votes: int
    prod_topics: str


def fetch_ph_posts(n_posts: int):
    url = "https://api.producthunt.com/v2/api/graphql"
    headers = {"Authorization": "Bearer {}".format(PHUNT_API_TOKEN)}
    data = {
        "query": """{
              posts(first: %d) {
                edges {
                  node {
                    id
                    name
                    description
                    url
                    votesCount
                    topics {
                      edges {
                        node {
                          name
                        }
                      }
                    }
                  }
                }
              }
            }"""
        % n_posts
    }
    r = requests.post(url, json=data, headers=headers)
    result = r.json()
    return result


def parse_ph_response(ph_response: dict[str, Any]) -> list[PHuntProduct]:
    product_list = ph_response["data"]["posts"]["edges"]
    product_model_list = []
    for product in product_list:
        product_dict = product["node"]
        product_dict["n_votes"] = product_dict["votesCount"]
        product_dict["prod_topics"] = ", ".join(
            [i["node"]["name"] for i in product_dict["topics"]["edges"]]
        )
        product_model_list.append(PHuntProduct.parse_obj(product_dict))

    return product_model_list

def main():
    response = fetch_ph_posts(10)
    product_list = parse_ph_response(response)

    df = pd.DataFrame([i.model_dump() for i in product_list])
    return df

if __name__ == "__main__":
    main()
    schedule.every(10).minutes.do(main)

    while True:
        schedule.run_pending()
        time.sleep(1)