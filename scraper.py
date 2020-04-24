#!/bin/env/python

import requests
from bs4 import BeautifulSoup 
from csv import DictWriter
import re
import json

def parse_edges(page):
    try:
        pattern = re.search(
                r"var edges = new vis\.DataSet\((.*?)\);", 
                page.text,
                re.MULTILINE | re.DOTALL
            )
        return json.loads(pattern.group(1))
    except Exception as e:
        print(e)
        return None


def parse_nodes(page):
    soup = BeautifulSoup(page.text, features='html.parser')
    
    nodes = []
    headers = ["ID", ] + [ x.text for x in soup.select_one(".covid_table_header").find_all("div") ]
    for row in soup.select(".covid_table_row"):
        values = [row.get("data-id")] + [x.text for x in row.find_all("div") ]
        nodes.append(dict(zip(headers, values)))

    return nodes


def write_edges(edges):
    if edges:
        with open("edges_official.csv", "w") as f:
            writer = DictWriter(f, edges[0].keys())
            writer.writeheader()
            writer.writerows(edges)


def write_nodes(nodes):
    with open("nodes_official.csv", "w") as f:
        writer = DictWriter(f, nodes[0].keys())
        writer.writeheader()
        writer.writerows(nodes)


if __name__ == "__main__":
    doc = requests.get(
            "https://covid19.health.gov.mv/dashboard",
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
                }
        )

    write_nodes(parse_nodes(doc))
    write_edges(parse_edges(doc))
