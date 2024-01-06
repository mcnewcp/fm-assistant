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
        "Select roles for scoring",
        all_roles,
        "DLR-Inverted Wing Back Su",
        placeholder="Choose a role",
    )

    # display columns selection
    selectable_cols = ["Age", "Personality", "Height", "Left Foot", "Right Foot"]
    selected_cols = st.multiselect(
        "Select additional display columns",
        selectable_cols,
        ["Age", "Personality"],
        placeholder="Choose display columns",
    )

    # squad file upload
    uploaded_file = st.file_uploader("Choose an HTML file", type="html")

# load squad df
if uploaded_file is not None:
    # Check if the uploaded file has an HTML extension
    if not uploaded_file.name.endswith(".html"):
        st.error("Error: Please upload a valid HTML file.")
    else:
        # Read HTML file
        df_squad = read_html_file(uploaded_file)

        if len(roles) > 0:
            # generate scored df
            df_squad_scores, primary_attributes, secondary_attributes = score_players(
                roles, df_squad, selected_cols
            )

            if df_squad_scores is not None:
                # Display the DataFrame in an interactive table
                st.dataframe(df_squad_scores, use_container_width=True)
