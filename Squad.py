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
    roles_squad = st.multiselect(
        "Select roles for scoring squad",
        all_roles,
        "DLR-Inverted Wing Back Su",
        placeholder="Choose one or more roles",
    )

    # display columns selection
    selectable_cols_squad = ["Age", "Personality", "Height", "Left Foot", "Right Foot"]
    selected_cols_squad = st.multiselect(
        "Select additional display columns",
        selectable_cols_squad,
        ["Age", "Personality"],
        placeholder="Choose display columns",
    )

    # squad file upload
    uploaded_file_squad = st.file_uploader("Choose an exported squad HTML", type="html")

# load squad df
if uploaded_file_squad is not None:
    # Check if the uploaded file has an HTML extension
    if not uploaded_file_squad.name.endswith(".html"):
        st.error("Error: Please upload a valid HTML file.")
    else:
        # Read HTML file
        df_squad = read_html_file(uploaded_file_squad)

        if len(roles_squad) > 0:
            # generate scored df
            df_squad_scores, primary_attributes, secondary_attributes = score_players(
                roles_squad, df_squad, selected_cols_squad
            )

            if df_squad_scores is not None:
                # Display the DataFrame in an interactive table
                st.dataframe(df_squad_scores, use_container_width=True)
