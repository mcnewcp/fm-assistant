import streamlit as st
import pandas as pd
from utils import *


st.title("Football Manager Assistant")

# load roles
df_role = pd.read_csv("role-config.csv")
all_roles = df_role["Role"].unique()

# sidebar
with st.sidebar:
    # role selection
    roles = st.multiselect(
        "Select roles for scoring squad",
        all_roles,
        "DLR-Inverted Wing Back Su"
        if "roles_scout" not in st.session_state
        else st.session_state["roles_scout"],
        placeholder="Choose one or more roles",
    )

    # display columns selection
    selectable_cols = ["Age", "Personality", "Height", "Left Foot", "Right Foot"]
    selected_cols = st.multiselect(
        "Select additional display columns",
        selectable_cols,
        ["Age", "Personality"]
        if "selected_cols_scout" not in st.session_state
        else st.session_state["selected_cols_scout"],
        placeholder="Choose display columns",
    )

    # scouting file upload
    uploaded_file = st.file_uploader("Choose an exported squad HTML", type="html")

# update session state
st.session_state["roles_scout"] = roles
st.session_state["selected_cols_scout"] = selected_cols

# load players df
if uploaded_file is not None:
    # Check if the uploaded file has an HTML extension
    if not uploaded_file.name.endswith(".html"):
        st.error("Error: Please upload a valid HTML file.")
    else:
        # Read HTML file
        st.session_state["df_players_scout"] = read_html_file(uploaded_file)

if len(roles) > 0 and "df_players_scout" in st.session_state:
    # generate scored df
    df_scores, primary_attributes, secondary_attributes = score_players(
        roles, st.session_state["df_players_scout"], selected_cols
    )

    # display table
    st.dataframe(df_scores, use_container_width=True)
