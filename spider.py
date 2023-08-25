import plotly.graph_objects as go
import pandas as pd
import numpy as np

df = pd.read_excel(io='Data2.xlsx', engine='openpyxl', usecols='A:Q', sheet_name='Sheet0', nrows=2000)
vals = []
target_val=[]
cats = df["Category"].unique()

for x in cats:
    val= df.query('Category == @x')
    the_mean = round(val['Score Value'].mean(),2)
    targ_mean = round(val['Subcategory target score'].mean(),2)
    target_val = np.append(target_val, targ_mean)
    vals = np.append(vals, the_mean)

target_val = np.append(target_val, target_val[0])
vals = np.append(vals, vals[0])   

cats_one = df["Category"].unique()[0]
category_count = df["Category"].nunique()
new_record = pd.DataFrame([{'Category':cats_one}])
cats = np.append(cats, cats_one)
#cats =pd.concat([cats, new_record], ignore_index=True)

fig = go.Figure()
fig.add_trace(go.Scatterpolar(
    name = "Score",
    r = vals,
    theta = cats,
    ))
fig.add_trace(go.Scatterpolar(
    name = "Target score",
    r = target_val,
    theta = cats,
    ))
fig.update_traces(fill='toself')
fig.update_layout(
    polar = dict(
    radialaxis_angle = -45,
    angularaxis = dict(
    direction = "clockwise",
    period = category_count)
    ))

fig.show()