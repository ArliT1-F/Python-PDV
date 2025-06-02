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


def get_outdated_packages():
    result = subprocess.run(["pip", "list", "--outdated", "--format=json"], capture_output=True, text=True)
    data = json.loads(result.stdout)
    return {pkg['name'].lower() for pkg in data}


def build_graph(dep_json):
    G = nx.DiGraph()
    for package in dep_json:
        pkg_info = package.get("package", {})
        pkg_name = pkg_info.get("key") or pkg_info.get("name") or "unknown"
        G.add_node(pkg_name)
        for dep in package.get("dependencies", []):
            dep_name = dep.get("key") or dep.get("name") or "unknown"
            G.add_edge(pkg_name, dep_name)
    return G


def draw_graph(G, outdated):
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, k=0.5, iterations=20)
    node_colors = ['red' if node in outdated else 'lightblue' for node in G.nodes()]
    nx.draw(G, pos, with_labels=True, node_size=1500, node_color=node_colors, 
            font_size=10, font_weight='bold', edge_color='gray')
    plt.title("Python Package Dependency Graph")
    plt.tight_layout()
    plt.show()
    plt.savefig("dependency_graph.png")
    print("[+] Saved graph to dependency_graph.png")


@click.command()
@click.option('--show', is_flag=True, help="Display graph in a window.")
def main(show):
    print("[+] Parsing dependency tree...")
    dep_data = get_dependency_tree()
    print(f"[+] {len(dep_data)} top-level packages found.")

    print("[+] Building graph...")
    graph = build_graph(dep_data)

    print("[+] Checking for outdated packages...")
    outdated = get_outdated_packages()
    print(f"[i] {len(outdated)} packages are outdated.")

    if show:
        print("[+] Displaying graph...")
        draw_graph(graph, outdated)
    else:
        print("[i] Graph build completed. Use --show to visualize it.")
        draw_graph(graph, outdated)


if __name__ == '__main__':
    main()
