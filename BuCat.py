import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
import streamlit as st
st.set_page_config(page_title="Assessment tool", page_icon=":bar_chart:", layout="wide")
# Suppose this is your list of data for which you want subplots
data = [
    np.random.randn(100) for _ in range(7)  # 7 random datasets as an example
]
df = pd.read_excel(io='Dummy_Lean_all.xls', usecols='A:Q', sheet_name='Sheet0', nrows=2000)

try:
    
    st.sidebar.header("Please filter here:")
    bunit = st.sidebar.multiselect(
        "Select Business unit:",
        options=df["Business unit child"].unique(),
        default=df["Business unit child"].unique()
    )
    # filter df with previous seletec items
    df = df.query('`Business unit child` == @bunit')
    st.markdown("##")

    df_cols= df[["Business unit child", "Category","Subcategory", "Subcategory target score", "Score Value"]]
    grouped_data = df_cols.groupby([ "Business unit child","Category","Subcategory"]).mean().reset_index()
    unique_BU = grouped_data['Business unit child'].unique()
    #for index,each_bu in enumerate(grouped_data['Business unit child'].unique()):
        
        #df_unit= grouped_data[grouped_data['Business unit child'] == each_bu]
    cats = grouped_data["Category"].unique()
    legends = grouped_data['Category'].unique()
    # Calculate rows based on the length of data and the number of columns you want
    cols = 2
    rows = int(np.ceil(len(cats) / cols))

    # Create subplots
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=legends)

    #df_unit= grouped_data[grouped_data['Business unit child'] == 'Shift Mngr B']

    
    # Add traces (plots) to the subplots
    for index, (dataset,legend) in enumerate(zip(cats,legends)):
        df_sel = grouped_data[grouped_data['Category'] == dataset]
        row = (index // cols) + 1
        col = (index % cols) + 1
        
        #fig.add_trace(go.Scatter(y=df_sel['Score Value'], mode='markers'), row=row, col=col)
        for each_bu in unique_BU:
            df_sel = df_sel.query(
            " `Business unit child` == @each_bu"
            )
            fig.add_trace(
            go.Bar(
                x=df_sel['Subcategory'],
                y=df_sel['Score Value'],
                text=round(df_sel['Score Value'],2),
                name=f"{each_bu} Score",
                offsetgroup=each_bu,
                legendgroup=each_bu,
                #textfont_color=data['theme']['textColor'],
                textposition='outside',
                #legendgrouptitle_text=each_doa,
            )
            )
            fig.add_trace(
            go.Scatter(
                x=df_sel['Subcategory'],
                y=df_sel['Subcategory target score'],
                text=round(df_sel['Subcategory target score'],2),
                textposition='top center',
                #textfont_color=data['theme']['textColor'],
                mode="markers+text",
                marker_symbol='hexagon-dot',
                name=f"{each_bu} Target",
                marker=dict(size=10 ),
                offsetgroup=each_bu,
                legendgroup=each_bu,
            )
            )
        fig.update_layout(
            yaxis1=dict(tickformat=".0%"),
            yaxis2=dict(tickformat=".0%"),
            height=(rows * 400),
            width=800,
            #margin=dict(r=20),
            xaxis={'categoryorder':'category ascending'},
        )
    st.plotly_chart(fig, use_container_width=True)
except:
    st.write("Can not display anything until data has been uploaded, or proper items have been selected")