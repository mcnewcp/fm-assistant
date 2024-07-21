import streamlit as st
import pandas as pd
import numpy as np
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
        (
            "Inverted Wing Back (A)"
            if "roles_squad" not in st.session_state
            else st.session_state["roles_squad"]
        ),
        placeholder="Choose one or more roles",
    )

    # display columns selection
    selectable_cols = ["Age", "Personality", "Height", "Left Foot", "Right Foot"]
    selected_cols = st.multiselect(
        "Select additional display columns",
        selectable_cols,
        (
            ["Age", "Personality"]
            if "selected_cols_squad" not in st.session_state
            else st.session_state["selected_cols_squad"]
        ),
        placeholder="Choose display columns",
    )

    # squad file upload
    uploaded_file = st.file_uploader("Choose an exported squad HTML", type="html")

# update session state
st.session_state["roles_squad"] = roles
st.session_state["selected_cols_squad"] = selected_cols

# load previous squad planner
df_squad_planner = pd.read_csv("data/squad_plan.csv")

# set up squad planner df
depth = 4  # squad depth per role
rating_cols = [f"rating_{i}" for i in range(1, depth + 1)]
age_cols = [f"age_{i}" for i in range(1, depth + 1)]


# apply conditional formatting to rating cols
def pd_styler(styler, rating_cols: list, age_cols: list):
    styler.format(precision=2, subset=rating_cols)
    styler.format(precision=0, subset=age_cols)
    styler.background_gradient(axis=None, cmap="RdYlGn", subset=rating_cols)
    return styler


df_squad_planner_styled = df_squad_planner.style.pipe(
    pd_styler, rating_cols=rating_cols, age_cols=age_cols
)

# display squad planner df
column_config = {
    "position": st.column_config.TextColumn(
        "Position",
        help="Enter any position, doesn't affect calculations",
    ),
    "role": st.column_config.SelectboxColumn(
        "Role", help="Select role to calculate ratings", options=all_roles
    ),
}
# Add entries to column_config for each player depth
for i in range(1, depth + 1):
    column_config[f"name_{i}"] = st.column_config.TextColumn(
        "Name", help="Select player name"
    )
    column_config[f"age_{i}"] = st.column_config.NumberColumn(
        "Age", help="Age of player", disabled=True
    )
    column_config[f"rating_{i}"] = st.column_config.NumberColumn(
        "Rating", help="Rating of player in chosen role", disabled=True
    )
st.data_editor(
    df_squad_planner_styled,
    disabled=rating_cols + age_cols,
    column_config=column_config,
    num_rows="fixed",
    hide_index=True,
)

# load players df
if uploaded_file is not None:
    # Check if the uploaded file has an HTML extension
    if not uploaded_file.name.endswith(".html"):
        st.error("Error: Please upload a valid HTML file.")
    else:
        # Read HTML file
        st.session_state["df_players_squad"] = read_html_file(uploaded_file)

if len(roles) > 0 and "df_players_squad" in st.session_state:
    # generate scored df
    df_scores = score_players(
        roles, st.session_state["df_players_squad"], selected_cols
    )

    # display table
    st.dataframe(df_scores, use_container_width=True)
