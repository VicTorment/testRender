import networkx as nx
import matplotlib.pyplot as plt

def build_organizational_chart(data):
    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes and edges to the graph based on data
    for row in data:
        parent_name, parent_level, child_name, child_level = row
        G.add_node(parent_name, level=parent_level)
        G.add_node(child_name, level=child_level)
        G.add_edge(parent_name, child_name)

    # Draw the graph
    pos = nx.spring_layout(G)
    labels = {node: node for node in G.nodes()}

    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, labels=labels, with_labels=True, node_size=3000, node_color='skyblue', font_size=15)
    plt.title("Organizational Chart")
    plt.show()

# Sample data: [parent name, parent level, child name, child level]
data = [
    ["CEO", 1, "CTO", 2],
    ["CEO", 1, "CFO", 2],
    ["CTO", 2, "Dev Team", 3],
    ["CFO", 2, "Finance Team", 3],
    ["Dev Team", 3, "Frontend", 4],
    ["Dev Team", 3, "Backend", 4],
]

build_organizational_chart(data)
