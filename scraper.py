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


def sanitize_node(item: dict):
    for key in list(item.keys()):   # list to avoid mutating
        if item[key] is None:
            del item[key]


def convert_date(dt, fmt='%Y%m%d'):
    if not dt:
        return None
    else:
        if "-" in dt:
            fmt = "%d-%b-%y"
        try:
            datetimeobject = datetime.strptime(dt, fmt)
            return datetimeobject.strftime('%d %B %Y')
        except Exception as e:
            return None


def parse_nodes(page):

    nodes = []
    edges = []
    items = json.loads(page.text)

    for key, item in items.items():
        node = {
            "ID": sanitize_id(item['i']),
            "Case": sanitize_id(item['i']),
            "Age": item["a"],
            "Gender": item["g"],
            "Nationality": item["n"],
            "Condition": item["c"],
            "Transmission": item["s"],
            "Cluster": item["l"],
            "Confirmed On": convert_date(item["o"]),
            "Recovered On": convert_date(item["r"]),
            "Discharged On": convert_date(item["e"]),
            "Deceased On": convert_date(item["t"]),
            "Hospitalized": item["h"]
        }

        nodes.append(node)

        if "p" in item.keys():
            for p in item["p"]:
                edges.append({
                    "from": sanitize_id(p),
                    "to": node["ID"],
                })

    return nodes, edges


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
            if cluster_id not in G:
                first = next((x for x in nodes if x.get('Cluster') == cluster_id), None)
                last = next((x for x in nodes[::-1] if x.get('Cluster') == cluster_id), None)
                cluster_node = {"Cluster": cluster_id, "Confirmed On": first.get("Confirmed On"), "Recovered On": last.get("Recovered On")}
                sanitize_node(cluster_node)
                G.add_node(cluster_id, **cluster_node)

            G.add_edge(node_id, cluster_id)

    for edge in edges:
        sanitize_node(edge)
        G.add_edge(edge["from"], edge["to"], **edge)

    print("Writing Graph")
    nx.write_graphml(G, "cases.graphml")


if __name__ == "__main__":

    nodes, edges = fetch_document(f"https://covid19.health.gov.mv/cases.json?t={int(time.time())}", "Data", parse_nodes)

    # process nodes
    print(f"Writing {len(nodes)} Nodes to file")
    if nodes:
        write_nodes(nodes)

    # process edges
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
