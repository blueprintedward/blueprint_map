"""Graph module for loading blueprint, adding events, and rendering to image."""

import json

import matplotlib
import matplotlib.pyplot as plt
import networkx as nx

# Use a font that supports Chinese (CJK); fallback order for Windows / common systems
matplotlib.rcParams["font.sans-serif"] = [
    "Microsoft JhengHei",
    "SimHei",
    "SimSun",
    "DejaVu Sans",
]
matplotlib.rcParams["axes.unicode_minus"] = False  # avoid minus sign as square


def load_blueprint(path: str) -> tuple[nx.Graph, dict]:
    """Load blueprint from JSON and return NetworkX graph and node metadata."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    G = nx.Graph()
    id_to_label = {}

    for node in data.get("nodes", []):
        nid = node["id"]
        label = node.get("label", nid)
        category = node.get("category", "concept")
        G.add_node(nid, label=label, category=category)
        id_to_label[nid] = label

    for edge in data.get("edges", []):
        src = edge.get("source")
        tgt = edge.get("target")
        if src and tgt and src in G and tgt in G:
            G.add_edge(src, tgt)

    return G, id_to_label


def add_event(graph: nx.Graph, event: str, placement: dict, id_to_label: dict) -> nx.Graph:
    """Add event as new node and connect to specified nodes."""
    safe = "".join(c if c.isalnum() or c in " -" else "_" for c in event[:30])
    event_id = "event_" + safe.replace(" ", "_").replace("-", "_").strip("_") or "new_event"
    connections = placement.get("connections", [])
    category = placement.get("category", "concept")

    graph.add_node(event_id, label=event, category=category)
    id_to_label[event_id] = event

    for conn in connections:
        if conn in graph:
            graph.add_edge(event_id, conn)

    return graph


def render_to_image(graph: nx.Graph, output_path: str) -> None:
    """Render graph to PNG image using NetworkX and matplotlib."""
    pos = nx.spring_layout(graph, k=2, iterations=50, seed=42)
    node_labels = nx.get_node_attributes(graph, "label")
    categories = nx.get_node_attributes(graph, "category")

    plt.figure(figsize=(16, 12))
    nx.draw_networkx_edges(graph, pos, alpha=0.5, width=0.5)
    nx.draw_networkx_nodes(graph, pos, node_size=300, alpha=0.9)
    nx.draw_networkx_labels(graph, pos, node_labels, font_size=6)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output_path, dpi=120, bbox_inches="tight")
    plt.close()
