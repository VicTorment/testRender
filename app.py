import streamlit as st
from pathlib import Path
import networkx as nx
import pandas as pd 
import plotly.io as pio
from plotly.subplots import make_subplots
import plotly.express as px 
import plotly.graph_objects as go
import numpy as np
from streamlit_option_menu import option_menu
import toml
#import io
st.set_page_config(page_title="Assessment tool", page_icon=":bar_chart:", layout="wide")
#st.title("This is awsome!!!")


current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
css_file =  current_dir /"Styles" / "main.css"

with open(css_file) as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

data = toml.load(current_dir / ".streamlit" / "config.toml")

#@st.cache_data(experimental_allow_widgets=True, ttl=900)
#def load_and_display_csv():
#    if uploaded_file is not None:
#        if uploaded_file.name.endswith("xlsx"):
#            dataframe = pd.read_excel(io=uploaded_file, engine='openpyxl', usecols='A:Q', sheet_name='Sheet0', nrows=2000)
#        else:
#            dataframe = pd.read_excel(io=uploaded_file,  usecols='A:Q', sheet_name='Sheet0', nrows=2000)
#    return dataframe


selected = option_menu(
    menu_title = None, 
    options = ["File data","Parent/Child Business unit","Business unit/Category", "Category/ Subcategory","Overview pr Category/ Subcategory", "Business unit, over time", "Organisational chart"],
    icons= ["upload", "diagram-2", "bar-chart-fill", "bar-chart-line","bar-chart-steps", "file-diff", "diagram-3-fill"],
    orientation = "horizontal",
)

if selected == "File data":
    st.sidebar.header("Sidebar shows filters")
    st.subheader("Upload only .xls or .xlsx files")
    uploaded_file = st.file_uploader("Choose a file")
    try:
        if uploaded_file is not None:
            if uploaded_file.name.endswith("xlsx"):
                dataframe = pd.read_excel(io=uploaded_file, engine='openpyxl', usecols='A:Q', sheet_name='Sheet0', nrows=2000)
            else:
                dataframe = pd.read_excel(io=uploaded_file,  usecols='A:Q', sheet_name='Sheet0', nrows=2000)
        st.session_state.df = dataframe
    
        st.write(st.session_state.df.head())
    except:
        st.write("No data has ben provided yet")
    
if selected == "Parent/Child Business unit":
    try:
        df = st.session_state.df
        st.sidebar.header("Please filter here:")
        bunit = st.sidebar.multiselect(
            "Select Business unit parent:",
            options=df["Business unit parent"].unique(),
            default=df['Business unit parent'].unique()
        )
        # filter df with previous seletec items
        df = df.query('`Business unit parent` == @bunit')
        categorySel = st.sidebar.multiselect(
            "Select Business unit child:",
            options=df["Business unit child"].unique(),
            default=sorted(df["Business unit child"].unique())
            
        )


        df_selection = df.query(
            " `Business unit child` == @categorySel"
        )
        #st.title(":bar_chart: Dashboard for business units")
        st.markdown("##")

        #----- KPI-------
        total_sales = round(df_selection["Score Value"].mean(),2)
        score_max = df_selection["Score Value"].max()
        target_max = df_selection["Subcategory target score"].max()
        average_sales = round(df_selection["Subcategory target score"].mean(),2)
        total_Na = df_selection["Score Value"].isna().sum()
        if score_max >= target_max:
            nbr_y = score_max   
        else:
            nbr_y = target_max

        left_column, middle_column, right_column = st.columns(3)
        with left_column:
            st.subheader("Mean Score Business unit:")
            st.subheader(f"{total_sales:,}".replace(",","."))

        with middle_column:
            st.subheader("Mean Target Score:")
            st.subheader(f"{average_sales:,}".replace(",","."))

        with right_column:
            st.subheader("Numbers of N/A:")
            st.subheader(f"{total_Na}")

        st.markdown("---")

        #---- charts-----

        # Create a figure with bar and line traces
        df_cols= df_selection[["Business unit parent","Business unit child",  "Subcategory target score", "Score Value"]]

        grouped_data = df_cols.groupby([ "Business unit parent", "Business unit child"]).mean().reset_index()
        client_name = df['Client'][0]
        
        unique_count = grouped_data['Business unit parent'].nunique()
        unique_BU = grouped_data['Business unit parent'].unique()

        fig = go.Figure(
        layout=dict(
            #xaxis=dict(categoryorder="category ascending"),
            #yaxis=dict(range=[0, nbr_y]),
            yaxis=dict(range=[0, 5]),
            scattermode="group",
            legend=dict(groupclick="toggleitem"),
            title=f'{client_name} - parent business unit {unique_BU} <br>Average Score and Target pr. child business unit',
        )
        )
        for each_bu in unique_BU:
            df_select = grouped_data.query(
            " `Business unit parent` == @each_bu"
            )
            fig.add_trace(
            go.Bar(
                x=df_select['Business unit child'],
                y=df_select['Score Value'],
                text=round(df_select['Score Value'],2),
                textfont_color=data['theme']['textColor'],
                textposition='outside',
                name=f"Score",
                #textposition='top center',
                #marker_color='rgba(150,150,10,0.4)',
                offsetgroup=each_bu,
                legendgroup=each_bu,
                #legendgrouptitle_text=each_doa,
            )
            )
            fig.add_trace(
            go.Scatter(
                x=df_select['Business unit child'],
                y=df_select['Subcategory target score'],
                text=round(df_select['Subcategory target score'],2),
                textposition='top center',
                textfont_color=data['theme']['textColor'],
                mode="markers+text",
                marker_symbol='hexagon-dot',
                name=f"Target",
                marker=dict(size=10 ),
                offsetgroup=each_bu,
                legendgroup=each_bu,
            )
            )
            # Update layout for dual y-axes
        fig.update_layout(
            yaxis=dict(title='Score'),
            yaxis2=dict(title='Subcategory target score', overlaying='y', side='right'),
            legend=dict(x=0.9, y=1),
            width=1200,
            margin=dict(r=20),
            xaxis={'categoryorder':'category ascending'},
        )
        st.plotly_chart(fig,use_container_width=True)
    except:
        st.write("Can not display anything until data has been uploaded")
    
#-----------------------------------------------------------------Business unit/Category-------------------------------------------------------------------------
if selected == "Business unit/Category":
    
    

    df = st.session_state.df
    st.sidebar.header("Please filter here:")
    bunit = st.sidebar.multiselect(
        "Select Business unit:",
        options=df["Business unit child"].unique(),
        default=df['Business unit child'].unique()
    )
    # filter df with previous seletec items
    df = df.query('`Business unit child` == @bunit')

    categorySel = st.sidebar.multiselect(
        "Select Category:",
        options=df["Category"].unique(),
        default=sorted(df["Category"].unique())
        
    )


    df_selection = df.query(
        " Category == @categorySel"
    )
    #shows the df in a table
        #st.dataframe(df_selection)

    #st.title(":bar_chart: Dashboard for business unit and categories")
    st.markdown("##")
    
    #----- KPI-------
    total_sales = round(df_selection["Score Value"].mean(),2)
    score_max = df_selection["Score Value"].max()
    target_max = df_selection["Subcategory target score"].max()
    average_sales = round(df_selection["Subcategory target score"].mean(),2)
    total_Na = df_selection["Score Value"].isna().sum()
    if score_max >= target_max:
        nbr_y = score_max   
    else:
        nbr_y = target_max

    left_column, middle_column, right_column = st.columns(3)
    with left_column:
        st.subheader("Mean Score Business unit:")
        st.subheader(f"{total_sales:,}".replace(",","."))

    with middle_column:
        st.subheader("Mean Target Score:")
        st.subheader(f"{average_sales:,}".replace(",","."))

    with right_column:
        st.subheader("Numbers of N/A:")
        st.subheader(f"{total_Na}")

    st.markdown("---")

    #---- charts-----
    try:    
        df_cols= df_selection[["Business unit child", "Category", "Subcategory target score", "Score Value"]]

        grouped_data = df_cols.groupby([ "Business unit child","Category"]).mean().reset_index()
        client_name = df['Client'].unique()
        client_name = client_name[0]
        unique_count = grouped_data['Business unit child'].nunique()
        unique_BU = grouped_data['Business unit child'].unique()
        
    
        fig = go.Figure(
            
            layout=dict(
            #xaxis=dict(categoryorder="category ascending"),
            #yaxis=dict(range=[0, nbr_y]),
            yaxis=dict(range=[0, 5]),
            scattermode="group",
            legend=dict(groupclick="toggleitem"),
            title=f'{client_name}   <br>Average of Score and Target by Category',
        )
        )
        for each_bu in unique_BU:
            df_select = grouped_data.query(
            " `Business unit child` == @each_bu"
            )
            fig.add_trace(
            go.Bar(
                x=df_select['Category'],
                y=df_select['Score Value'],
                text=round(df_select['Score Value'],2),
                name=f"{each_bu} Score",
                offsetgroup=each_bu,
                legendgroup=each_bu,
                textfont_color=data['theme']['textColor'],
                textposition='outside',
                #legendgrouptitle_text=each_doa,
            )
            )
            fig.add_trace(
            go.Scatter(
                x=df_select['Category'],
                y=df_select['Subcategory target score'],
                text=round(df_select['Subcategory target score'],2),
                textposition='top center',
                textfont_color=data['theme']['textColor'],
                mode="markers+text",
                marker_symbol='hexagon-dot',
                name=f"{each_bu} Target",
                marker=dict(size=10 ),
                offsetgroup=each_bu,
                legendgroup=each_bu,
            )
            )
            # Update layout for dual y-axes
        
        fig.update_layout(
            yaxis=dict(title='Score'),
            yaxis2=dict(title='Subcategory target score', overlaying='y', side='right'),
            legend=dict(x=0.9, y=1),
            height=500,
            width=1200,
            margin=dict(b=200, r=20),
            xaxis={'categoryorder':'category ascending'},
            
            
            #height=450,
        )
        #img_bytes = fig.to_image(format="png", width=800, height=450, scale=1)
        st.plotly_chart(fig,use_container_width=True)
        try:
            figs = go.Figure(
            )
            scores = np.append(df_select['Score Value'],df_select['Score Value'][0])
            target_scores = np.append(df_select['Subcategory target score'],df_select['Subcategory target score'][0])
            categories = np.append(df_select['Category'],df_select['Category'][0])

            #cats =pd.concat([cats, new_record], ignore_index=True)
        # for each_bu in unique_BU:
                
            figs.add_trace(go.Scatterpolar(
                name = f"{each_bu} Score",
                r = scores,
                theta = categories,
                ))
            figs.add_trace(go.Scatterpolar(
                name = f'{each_bu} Target',
                text=target_scores,
                r = target_scores,
                theta = categories,
                ))
            figs.update_traces(fill='toself')
        
        # Update layout for dual y-axes

            figs.update_layout(
                title=f'{client_name} - {each_bu}  <br>Average of Score and Target by Category',
                polar = dict(
                radialaxis_angle = 0,
                bgcolor=data['theme']['spiderWeb'],
                radialaxis = dict(range=[0, 5]),
                angularaxis = dict(
                direction = "clockwise",
                
                #margin=dict(r=20),
                period = df_select['Category'].nunique()) #df_select['Category'].nunique()
                ))
            st.plotly_chart(figs,use_container_width=True)
        except:
            st.subheader("To get a spiderweb chart, select only 1 business unit")
    
    except:
        st.subheader("Can not display anything until data has been uploaded")
    


if selected == "Category/ Subcategory":
    try:
        df = st.session_state.df
        st.sidebar.header("Please filter here:")
        bunit = st.sidebar.multiselect(
            "Select Business unit:",
            options=df["Business unit child"].unique(),
            default=df["Business unit child"].unique()
        )
        # filter df with previous seletec items
        df = df.query('`Business unit child` == @bunit')
        categorySel = st.sidebar.multiselect(
            "Select Category:",
            options=df["Category"].unique(),
            default=sorted(df["Category"].unique())
        )
        # filter df with previous seletec items
        df = df.query('Category == @categorySel')
        subCategorySel = st.sidebar.multiselect(
            "Select Subcategory:",
            options=df["Subcategory"].unique(),
            default=sorted(df["Subcategory"].unique())
            
        )

        df_selection = df.query(
            " Subcategory == @subCategorySel"
        )
        #shows the df in a table
            #st.dataframe(df_selection)

        #st.title(":bar_chart: Dashboard for categories and their subcategories")
        st.markdown("##")

        #----- KPI-------
        total_sales = round(df_selection["Score Value"].mean(),2)
        score_max = df_selection["Score Value"].max()
        target_max = df_selection["Subcategory target score"].max()
        average_sales = round(df_selection["Subcategory target score"].mean(),2)
        total_Na = df_selection["Score Value"].isna().sum()
        if score_max >= target_max:
            nbr_y = score_max   
        else:
            nbr_y = target_max

        left_column, middle_column, right_column = st.columns(3)
        with left_column:
            st.subheader("Mean Score Category:")
            st.subheader(f"{total_sales:,}".replace(",","."))

        with middle_column:
            st.subheader("Mean Target Score:")
            st.subheader(f"{average_sales:,}".replace(",","."))
        
        with right_column:
            st.subheader("Numbers of N/A:")
            st.subheader(f"{total_Na}")

        st.markdown("---")

        #---- charts-----

        df_cols= df_selection[["Business unit child", "Category","Subcategory", "Subcategory target score", "Score Value"]]
        #grouped_data = df_cols.groupby('Subcategory').mean().reset_index()
        # Create a figure with bar and line traces


        grouped_data = df_cols.groupby([  "Business unit child","Category","Subcategory"]).mean().reset_index()
        client_name = df['Client'].unique()
        client_name = client_name[0]
        unique_count = grouped_data['Business unit child'].nunique()
        unique_BU = grouped_data['Business unit child'].unique()
        
        fig = go.Figure(
            
        layout=dict(
            #xaxis=dict(categoryorder="category ascending"),
            #yaxis=dict(range=[0, nbr_y]),
            yaxis=dict(range=[0, 5]),
            scattermode="group",
            legend=dict(groupclick="toggleitem"),
            
            title=f'{client_name}  <br>Average Score and Target by Subcategory',
        )
        )
        for each_bu in unique_BU:
            df_select = grouped_data.query(
            " `Business unit child` == @each_bu"
            )
            fig.add_trace(
            go.Bar(
                x=[df_select['Category'],df_select['Subcategory']],
                y=df_select['Score Value'],
                text=round(df_select['Score Value'],2),
                name=f"{each_bu} Score",
                offsetgroup=each_bu,
                legendgroup=each_bu,
                textfont_color=data['theme']['textColor'],
                textposition='outside',
                #legendgrouptitle_text=each_doa,
            )
            )
            fig.add_trace(
            go.Scatter(
                x=[df_select['Category'],df_select['Subcategory']],
                y=df_select['Subcategory target score'],
                text=round(df_select['Subcategory target score'],2),
                textposition='top center',
                textfont_color=data['theme']['textColor'],
                mode="markers+text",
                marker_symbol='hexagon-dot',
                name=f"{each_bu} Target",
                marker=dict(size=10 ),
                offsetgroup=each_bu,
                legendgroup=each_bu,
            )
            )
            # Update layout for dual y-axes
        
        fig.update_layout(
            yaxis=dict(title='Score'),
            yaxis2=dict(title='Subcategory target score', overlaying='y', side='right'),
            legend=dict(x=0.9, y=1),
            height=500,
            width=1200,
            margin=dict(b=200, r=20),
            xaxis={'categoryorder':'category ascending'},
            
            
            #height=450,
        )
        #img_bytes = fig.to_image(format="png", width=800, height=450, scale=1)
        st.plotly_chart(fig,use_container_width=True)
    except:
        st.write("Can not display anything until data has been uploaded")

#----------------------------------------------------Business unit over time----------------------------------------------------------------------
if selected == "Business unit, over time":
    try:
        df = st.session_state.df
        #add column with formatted date
        df['DOA'] = df['End date'].dt.strftime('%Y-%m')

        st.sidebar.header("Please filter here:")
        bunit = st.sidebar.selectbox(
            "Select Business unit:",
            options=df["Business unit child"].unique()
        )
        # filter df with previous seletec items
        df = df.query('`Business unit child` == @bunit')
        endDate = st.sidebar.multiselect(
            "Select date:",
            options=df["DOA"].unique(),
            default=df["DOA"].unique()
        )
        # filter df with previous seletec items
        df = df.query('`DOA` == @endDate')
        categorySel = st.sidebar.multiselect(
            "Select Category:",
            options=df["Category"].unique(),
            default=sorted(df["Category"].unique())
        )
        # filter df with previous seletec items
        df = df.query('Category == @categorySel')
        subCategorySel = st.sidebar.multiselect(
            "Select Subcategory:",
            options=df["Subcategory"].unique(),
            default=sorted(df["Subcategory"].unique())
            
        )

        df_selection = df.query(
            " Subcategory == @subCategorySel"
        )
        #shows the df in a table
            #st.dataframe(df_selection)

        #st.title(":bar_chart: Dashboard for categories and their subcategories")
        st.markdown("##")

        #----- KPI-------
        total_sales = round(df_selection["Score Value"].mean(),2)
        score_max = df_selection["Score Value"].max()
        target_max = df_selection["Subcategory target score"].max()
        average_sales = round(df_selection["Subcategory target score"].mean(),2)
        total_Na = df_selection["Score Value"].isna().sum()
        if score_max >= target_max:
            nbr_y = score_max   
        else:
            nbr_y = target_max

        left_column, middle_column, right_column = st.columns(3)
        with left_column:
            st.subheader("Mean Score Category:")
            st.subheader(f"{total_sales:,}".replace(",","."))

        with middle_column:
            st.subheader("Mean Target Score:")
            st.subheader(f"{average_sales:,}".replace(",","."))
        
        with right_column:
            st.subheader("Numbers of N/A:")
            st.subheader(f"{total_Na}")

        st.markdown("---")

        #---- charts-----

        df_cols= df_selection[["Business unit child","DOA", "Category","Subcategory", "Subcategory target score", "Score Value"]]
        grouped_data = df_cols.groupby([  "Business unit child","DOA","Category","Subcategory"]).mean().reset_index()
        client_name = df['Client'][0]
        #grouped_data = grouped_data.sort_values(by = "Subcategory")
        unique_count = grouped_data['DOA'].nunique()
        unique_DOA = grouped_data['DOA'].unique()

        fig = go.Figure(
        layout=dict(
            xaxis=dict(categoryorder="category descending"),
            #yaxis=dict(range=[0, nbr_y]),
            yaxis=dict(range=[0, 5]),
            scattermode="group",
            legend=dict(groupclick="toggleitem"),
            title=f'{client_name} - {bunit} <br>Average Score and Target by Subcategory pr. date',
        )
        )
        for each_doa in unique_DOA:
            df_select = grouped_data.query(
            " DOA == @each_doa"
            )
            fig.add_trace(
            go.Bar(
                x=[df_select['Category'],df_select['Subcategory']],
                y=df_select['Score Value'],
                text=round(df_select['Score Value'],2),
                name=f"{each_doa} Score",
                #marker_color='rgba(150,150,10,0.4)',
                offsetgroup=each_doa,
                legendgroup=each_doa,
                textfont_color=data['theme']['textColor'],
                textposition='outside',
                #legendgrouptitle_text=each_doa,
            )
            )
            fig.add_trace(
            go.Scatter(
                x=[df_select['Category'],df_select['Subcategory']],
                y=df_select['Subcategory target score'],
                text=round(df_select['Subcategory target score'],2),
                textposition='top center',
                mode="markers+text",
                marker_symbol='hexagon-dot',
                textfont_color=data['theme']['textColor'],
                name=f"{each_doa} Target",
                marker=dict(size=10 ),
                offsetgroup=each_doa,
                legendgroup=each_doa,
            )
            )
        
            # Update layout for dual y-axes
        fig.update_layout(
            yaxis=dict(title='Score'),
            yaxis2=dict(title='Subcategory target score', overlaying='y', side='right'),
            legend=dict(x=0.90, y=1),
            margin=dict(r=20),
            
            width=1200,
            xaxis={'categoryorder':'category ascending'},
        )
        st.plotly_chart(fig,use_container_width=True)   
    except:
        st.write("Can not display anything until data has been uploaded")

#----------------------------------------------------------Overview Category / Subcategory-----------------------------------------------------------------
if selected == "Overview pr Category/ Subcategory":
    try:
        df = st.session_state.df
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

        for index,each_bu in enumerate(grouped_data['Business unit child'].unique()):
            
            df_unit= grouped_data[grouped_data['Business unit child'] == each_bu]
            cats = grouped_data["Category"].unique() #maybe use df_unit
            legends = grouped_data['Category'].unique()
            
            # Calculate rows based on the length of data and the number of columns you want
            cols = 2
            rows = int(np.ceil(len(cats) / cols))

            # Create subplots
            fig = make_subplots(rows=rows, cols=cols, subplot_titles=legends)

            #df_unit= grouped_data[grouped_data['Business unit child'] == 'Shift Mngr B']

            st.write(each_bu)
            # Add traces (plots) to the subplots
            for index, (dataset,legend) in enumerate(zip(cats,legends)):
                df_sel = df_unit[df_unit['Category'] == dataset]
                row = (index // cols) + 1
                col = (index % cols) + 1
                
                #fig.add_trace(go.Scatter(y=df_sel['Score Value'], mode='markers'), row=row, col=col)
                fig.add_trace(go.Bar(x=df_sel['Subcategory'], y=df_sel['Score Value'],text=round(df_sel['Score Value'],2), showlegend=False)
                            , row=row, col=col)
                fig.add_trace(go.Line(x=df_sel['Subcategory'], y=df_sel['Subcategory target score'],text=round(df_sel['Subcategory target score'],2),showlegend=False)
                            , row=row, col=col)
                fig.update_yaxes(range=[0,5])
                fig.update_layout(
                    #yaxis=dict(range=[0, 5]),
                    #yaxis2=dict(range=[0, 5]),
                    #yaxis3=dict(range=[0,5]),
                    #yaxis4=dict(range=[0,5]),
                    
                    height=(rows * 400),
                    width=800,
                    #margin=dict(r=20),
                    xaxis={'categoryorder':'category ascending'},
                )
            st.plotly_chart(fig, use_container_width=True)

    except:
        st.write("Can not display anything until data has been uploaded, or proper items have been selected")
# ---------------------------------------------------------Organisational chart ----------------------------------------------------------------------------
if selected == "Organisational chart":
    try:
        st.sidebar.header("Sidebar shows filters in other tabs")
        df = st.session_state.df
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

            #fig.show()
            st.plotly_chart(fig,use_container_width=True)

        df_cols = df[["Business unit parent","Business unit parent tier","Business unit child","Business unit child tier"]]
        # Convert DataFrame rows into tuples for the function
        #rows = [tuple(row) for _, row in df.iterrows()]
        rows = [tuple(row) for _, row in df_cols.iterrows()]
        build_organizational_chart(rows)
    except:
        st.write("Can not display anything until data has been uploaded")