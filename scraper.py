#!/bin/env/python

import json
import time
from csv import DictWriter
from datetime import datetime
from shutil import which
from subprocess import call

import requests


# def parse_last_update(page):
#     try:
#         soup = BeautifulSoup(page.text, features="html.parser")
#         update_tag = soup.find(lambda tag: tag.name == "div" and tag.text.startswith("Last Updated Date"))
#         return update_tag.text
#     except Exception as e:
#         print("unable to parse last updated")


def sanitize_id(val):
    if isinstance(val, str):
        return val
    else:
        return f"MAV{val:05}"


def parse_edges(page):

    try:
        j = page.json()
        edges = j["clusters"]

        return [
            {"from": sanitize_id(edge["from"]), "to": sanitize_id(edge["to"]), "dashes": edge.get("dashes", False)}
            for edge in edges
        ]

    except Exception as e:
        print(e)
        return None


def convert_date(dt, fmt='%Y%m%d'):
    if not dt:
        return None
    else:
        if "-" in dt:
            fmt = "%d-%b-%y"
        datetimeobject = datetime.strptime(dt, fmt)
        return datetimeobject.strftime('%d %B %Y')


def parse_nodes(page):
    # soup = BeautifulSoup(page.text, features='html.parser')

    nodes = []
    # headers = ["ID", ] + [ x.text for x in soup.select_one(".covid_table_header").find_all("div") ]
    # for row in soup.select(".covid_table_row"):
    #     values = [row.get("data-id")] + [x.text for x in row.find_all("div") ]
    #     nodes.append(dict(zip(headers, values)))

    items = json.loads(page.text)

    for key, item in items.items():
        node = {
            "ID": f"MAV{item['case_id']:05}",
            "Case": f"MAV{item['case_id']:05}",
            "Age": item["age"],
            "Gender": item["gender"],
            "Nationality": item["nationality"],
            "Condition": item["condition"],
            "Transmission": item["infection_source"],
            "Cluster": item["cluster"],
            "Confirmed On": convert_date(item["confirmed_date"]),
            "Recovered On": convert_date(item["recovered_date"]),
            "Discharged On": convert_date(item["discharged_date"]),
            "Deceased On": convert_date(item["deceased_date"]),
        }

        nodes.append(node)

    return nodes


def write_edges(edges):
    if edges:
        with open("edges_official.csv", "w") as f:
            writer = DictWriter(f, ['to', 'from', 'dashes'])
            writer.writeheader()
            writer.writerows(edges)


def write_nodes(nodes):
    with open("nodes_official.csv", "w") as f:
        writer = DictWriter(f, nodes[0].keys())
        writer.writeheader()
        writer.writerows(nodes)


def fetch_document(url, title, parser):
    # retrieve the document
    print(f"fetching {title} -> {url}")
    doc = requests.get(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        }
    )

    if doc.status_code == 200:  # note: requests doesn't necessary mean HTTP200 here
        return parser(doc)
    else:
        print(f"Error: Failed to fetch {title}")
        return None


def sanitize_node(item: dict):
    for key in list(item.keys()):   # list to avoid mutating
        if item[key] is None:
            del item[key]


def build_graph(nodes, edges):
    import networkx as nx
    G = nx.DiGraph()

    print("Building Graph")

    for node in nodes:
        status = "active"
        if node.get("Deceased On"):
            status = "deceased"
        elif node.get("Recovered On"):
            status = "recovered"

        node["status"] = status

        node_id = node["ID"]
        cluster_id = node.get("Cluster")

        sanitize_node(node)
        G.add_node(node_id, **node)
        if cluster_id:
            G.add_edge(node_id, cluster_id)

    for edge in edges:
        sanitize_node(edge)
        G.add_edge(edge["from"], edge["to"], **edge)

    print("Writing Graph")
    nx.write_graphml(G, "cases.graphml")


if __name__ == "__main__":

    # process nodes
    nodes = fetch_document(f"https://covid19.health.gov.mv/cases.json?t={int(time.time())}", "Nodes", parse_nodes)
    print(f"Writing {len(nodes)} Nodes to file")
    if nodes:
        write_nodes(nodes)

    # process edges
    edges = fetch_document(f"https://covid19.health.gov.mv/data3.json?t={int(time.time())}", "Edges", parse_edges)
    if edges:
        print(f"Writing {len(edges)} Edges to file")
        write_edges(edges)


    # generate graphml
    build_graph(nodes, edges)

    # print git diff
    print("\n")  # sugar
    if which("git"):
        call([
            "git",
            "diff",
            "--stat",
            "nodes_official.csv",
            "edges_official.csv",
            "cases.graphml"
        ])

    else:
        print("Error: Response returned unsuccessful")
