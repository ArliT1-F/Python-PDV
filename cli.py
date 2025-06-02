import click
import subprocess
import json
import networkx as nx
import matplotlib.pyplot as plt
from tempfile import NamedTemporaryFile


def get_dependency_tree():
    with NamedTemporaryFile(delete=False) as tmp:
        subprocess.run(["pipdeptree", "--json"], stdout=tmp)
        tmp.seek(0)
        data = json.load(open(tmp.name))
    return data

def build_graph(dep_json):
    G = nx.DiGraph()
    for package in dep_json:
        pkg_name = package["package"]["name"]
        G.add_node(pkg_name)
        for dep in package.get("dependencies", []):
            dep_name = dep["package"]["name"]
            G.add_edge(pkg_name, dep_name)
    return G


def draw_graph(G):
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, k=0.5, iterations=20)
    nx.draw(G, pos, with_labels=True, node_size=1500, node_color='lightblue', font_size=10, font_weight='bold', edge_color='gray')
    plt.title("Python Package Dependency Graph")
    plt.tight_layout()
    plt.show()


@click.command()
@click.option('--show', is_flag=True, help="Display graph in a window.")
def main(show):
    print("[+] Parsing dependency tree...")
    dep_data =get_dependency_tree()
    print(f"[+] {len(dep_data)} top-level packages found.")

    print("[+] Building graph...")
    graph = build_graph(dep_data)

    if show:
        print("[+] Displaying graph...")
        draw_graph(graph)
    else:
        print("[+] Graph build complete. Use --show to vusualize it.")

if __name__ == '__main__':
    main()