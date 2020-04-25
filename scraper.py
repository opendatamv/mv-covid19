#!/bin/env/python

import requests
from bs4 import BeautifulSoup 
from csv import DictWriter
import re
import json
from shutil import which 
from subprocess import call

def parse_last_update(page):
    soup = BeautifulSoup(page.text, features="html.parser")
    update_tag = soup.find(lambda tag:tag.name=="div" and tag.text.startswith("Last Updated Date"))
    return update_tag.text


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
            writer = DictWriter(f, ['to', 'from', 'dashes'] )
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
    if doc.status_code == 200:                  # note: requests doesn't necessary mean HTTP200 here
        updated_on = parse_last_update(doc)
        print(f"Fetched Dashboard: {updated_on}")
        
        # process nodes
        nodes = parse_nodes(doc)
        if nodes:
            print(f"Writing {len(nodes)} Nodes to file")
            write_nodes(nodes)

        edges = parse_edges(doc)
        if edges:
            print(f"Writing {len(edges)} Edges to file")
            write_edges(edges)

        # print git diff
        if which("git"):
            call([
                "git",
                "diff",
                "--stat",
                "nodes_official.csv",
                "edges_official.csv"
            ])

    else:
        print("Error: Response returned unsuccessful")