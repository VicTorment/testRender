import streamlit as st
from pathlib import Path

import toml
#import io
st.set_page_config(page_title="Whishlist", page_icon=":gift:", layout="wide")
#st.title("This is awsome!!!")


current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
css_file =  current_dir /"Styles" / "main.css"

with open(css_file) as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

data = toml.load(current_dir / ".streamlit" / "config.toml")

st.header('Basses ønskeliste')

whishes = {('En fin paraply', 'https://www.paraplybutik.dk/butik/klassisk-paraply/groen-paraply-traehaandtag/'),
           ('noget andet', 'www.somewhere.com')
           }

for whish in whishes:
    st.write(f'{whish[0]} se more at {whish[1]}')
