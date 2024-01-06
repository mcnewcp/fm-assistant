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
    roles_scout = st.multiselect(
        "Select roles for scoring scouted players",
        all_roles,
        "DLR-Inverted Wing Back Su",
        placeholder="Choose one or more roles",
    )

    # display columns selection
    selectable_cols_scout = ["Age", "Personality", "Height", "Left Foot", "Right Foot"]
    selected_cols_scout = st.multiselect(
        "Select additional display columns",
        selectable_cols_scout,
        ["Age", "Personality"],
        placeholder="Choose display columns",
    )

    # scout file upload
    uploaded_file_scout = st.file_uploader("Choose an HTML file", type="html")

# load scout df
if uploaded_file_scout is not None:
    # Check if the uploaded file has an HTML extension
    if not uploaded_file_scout.name.endswith(".html"):
        st.error("Error: Please upload a valid HTML file.")
    else:
        # Read HTML file
        df_scout = read_html_file(uploaded_file_scout)

        if len(roles_scout) > 0:
            # generate scored df
            df_scout_scores, primary_attributes, secondary_attributes = score_players(
                roles_scout, df_scout, selected_cols_scout
            )

            if df_scout_scores is not None:
                # Display the DataFrame in an interactive table
                st.dataframe(df_scout_scores, use_container_width=True)
