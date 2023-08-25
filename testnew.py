import networkx as nx
import plotly.graph_objects as go
import pandas as pd

def compute_positions(data):
    levels = {}
    for row in data:
        _, parent_level, _, child_level = row
        levels[parent_level] = levels.get(parent_level, [])
        levels[child_level] = levels.get(child_level, [])

    # Counting nodes at each level
    for row in data:
        parent_name, parent_level, child_name, child_level = row
        if parent_name not in levels[parent_level]:
            levels[parent_level].append(parent_name)
        if child_name not in levels[child_level]:
            levels[child_level].append(child_name)

    pos = {}
    max_width = max([len(levels[key]) for key in levels])
    
    for level in levels:
        y = -level  # Adjusting to start from top
        nodes = levels[level]
        total_nodes = len(nodes)
        offset = (max_width - total_nodes) / 2  # Centering nodes
        for idx, node in enumerate(nodes):
            x = idx + offset
            pos[node] = (x, y)

    return pos

def build_organizational_chart(data):
    G = nx.DiGraph()

    for row in data:
        parent_name, _, child_name, _ = row
        G.add_edge(parent_name, child_name)

    pos = compute_positions(data)

    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        marker=dict(
            showscale=False,
            size=50,
            line_width=2
        ),
        text=[node for node in G.nodes()],
        textposition="top center"
    )

    fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                title="Organizational Chart",
                showlegend=False,
                hovermode='closest',
                margin=dict(t=0, b=0, l=0, r=0),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x")
             )
    )

    fig.show()

# Sample data: [parent name, parent level, child name, child level]
data = {
    'parent_name': ["CEO", "CEO", "CTO", "CFO", "Dev Team", "Dev Team"],
    'parent_level': [1, 1, 2, 2, 3, 3],
    'child_name': ["CTO", "CFO", "Dev Team", "Finance Team", "Frontend", "Backend"],
    'child_level': [2, 2, 3, 3, 4, 4]
}

df = pd.DataFrame(data)
df_cols = pd.read_excel(io='Data2.xlsx', engine='openpyxl', usecols='A:Q', sheet_name='Sheet0', nrows=2000)
df = df_cols[["Business unit parent","Business unit parent tier","Business unit child","Business unit child tier"]]
grouped_data = df_cols.groupby(["Business unit parent"])

# Convert DataFrame rows into tuples for the function
#rows = [tuple(row) for _, row in df.iterrows()]
rows = [tuple(row) for _, row in df.iterrows()]
build_organizational_chart(rows)