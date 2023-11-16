import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Sample data
data = [
    np.random.randn(100) for _ in range(7)
]

# Legend names
legends = ['Data ' + str(i+1) for i in range(len(data))]

cols = 3
rows = int(np.ceil(len(data) / cols))

fig = make_subplots(rows=rows, cols=cols, subplot_titles=legends)  # Set subplot titles here

# Add traces (plots) to the subplots
for index, (dataset, legend) in enumerate(zip(data, legends)):
    row = (index // cols) + 1
    col = (index % cols) + 1
    
    fig.add_trace(go.Scatter(y=dataset, mode='lines', showlegend=False), row=row, col=col)  # Disable the legend for the trace

fig.show()
