import streamlit as st
import pandas as pd
from utils import *

# Parameters - these should be converted to user selections
selected_cols = ["Age", "Personality", "Height"]


st.title("Football Manager Assistant")

# load roles
df_role = pd.read_csv("role-config.csv")
all_roles = df_role["Role"].unique()
all_attributes = df_role.drop(columns=["Role"]).columns.to_list()

# sidebar
with st.sidebar:
    # role selection
    roles = st.multiselect(
        "Select roles for scoring",
        all_roles,
        "DLR-Inverted Wing Back Su",
        max_selections=1,
        placeholder="Choose a role",
    )
    # choose first, and only, in list
    # this should be modified to work with multiple roles
    role = roles[0]

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

        # generate scored df
        df_squad_scores = score_squad(
            role, df_role, df_squad, selected_cols, all_attributes
        )

        if df_squad_scores is not None:
            # Display the DataFrame in an interactive table
            st.dataframe(df_squad_scores, use_container_width=True, hide_index=True)
