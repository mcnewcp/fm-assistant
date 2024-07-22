import streamlit as st
from streamlit import session_state as ss
import pandas as pd
import datetime
from utils import (
    load_squad,
    load_squad_plan,
    load_role_config,
    attach_player_cols,
    attach_rating,
    pivot_squad_plan_wide,
    style_squad_plan,
    get_column_config,
)


st.title("Football Manager Assistant ⚽️🤖")
st.subheader("Squad Planner")

# Initialize dataframes
# TODO: these should connect to supabase databases
if "df_squad" not in ss:
    load_squad()
if "df_squad_plan" not in ss:
    load_squad_plan()
if "df_role_config" not in ss:
    load_role_config()

# load lists
all_roles = ss.df_role_config["Role"].unique()
all_names = ss.df_squad["Name"].unique()
all_teams = ss.df_squad["Team"].unique()

# sidebar
with st.sidebar:
    # squad depth for each role
    depth = st.number_input("Depth", 1, 10, 4, help="Depth to display for each role")

    # load the most recent squad plan
    load_squad_plan = st.button("Load Squad Plan", "Load the most recent squad plan")

    # in-game date for use with saving squad plan and updating squad
    new_date = st.date_input(
        "In-Game Date",
        None,
        datetime.date(2020, 1, 1),
        datetime.date(2050, 12, 31),
        help="In-Game date must be specified for saving a Squad Plan or updating the Squad",
    )

    if new_date:
        # save squad plan
        save_squad_plan = st.button(
            "Save Squad Plan", help="Save the current squad plan in the database"
        )

        # update squad
        update_squad_file = st.file_uploader(
            "Upload Squad Export", type=["html"], accept_multiple_files=False
        )

        if update_squad_file:
            # team for uploaded file
            update_squad_team = st.radio(
                "Team",
                all_teams,
                None,
                help="Choose team associated with the squad update file",
            )

            if update_squad_team:
                update_squad = st.button(
                    "Update Squad", help="Update the squad database"
                )

# generate display df
df_display = (
    ss.df_squad_plan.pipe(attach_player_cols)  # lookup age, name
    .pipe(attach_rating)  # calculate rating
    .pipe(pivot_squad_plan_wide, depth=depth)  # pivot wide for display
    .pipe(style_squad_plan)  # style ratings, age
)

column_config = get_column_config(depth, all_roles, all_names)
st.data_editor(
    df_display, column_config=column_config, num_rows="fixed", hide_index=True
)
