import streamlit as st
from streamlit import session_state as ss
import pandas as pd
import datetime
from utils import (
    load_squad,
    load_squad_plan,
    load_role_config,
    update_squad_plan,
    pivot_squad_plan_wide,
    style_squad_plan,
    get_column_config,
    pivot_squad_plan_long,
    attach_uid,
    save_squad_plan_csv,
)


st.title("Football Manager Assistant ⚽️🤖")
st.subheader("Squad Planner")

# Initialize dataframes
# TODO: these should connect to supabase databases
if "df_role_config" not in ss:
    load_role_config()
if "df_squad" not in ss:
    load_squad()
if "df_squad_plan" not in ss:
    load_squad_plan()

# load lists
all_roles = ss.df_role_config["Role"].unique()
all_names = ss.df_squad["Name"].unique()
all_teams = ss.df_squad["Team"].unique()

# sidebar
with st.sidebar:
    # squad depth for each role
    depth = st.number_input("Depth", 1, 10, 4, help="Depth to display for each role")

    # load the most recent squad plan
    load_squad_plan_button = st.button(
        "Load Squad Plan", "Load the most recent squad plan"
    )
    if load_squad_plan_button:
        load_squad_plan()

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
        save_squad_plan_button = st.button(
            "Save Squad Plan", help="Save the current squad plan in the database"
        )
        if save_squad_plan_button:
            save_squad_plan_csv(ss.df_squad_plan, new_date)

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

# pivot wide for display
df_display = pivot_squad_plan_wide(ss.df_squad_plan, depth)

# display formatted squad planner
column_config = get_column_config(depth, all_roles, all_names)
df_display_edited = st.data_editor(
    style_squad_plan(df_display),
    column_config=column_config,
    num_rows="fixed",
    hide_index=True,
)

# check for changes
if not df_display_edited.equals(df_display):
    st.write("CHANGES!")
    # pivot long, update age & rating, overwrite ss squad plan
    ss.df_squad_plan = (
        df_display_edited.pipe(
            pivot_squad_plan_long, depth=depth
        )  # pivot long for calc
        .pipe(attach_uid)  # attach UID for attribute lookup
        .pipe(update_squad_plan)  # update age, rating
    )
    st.rerun()
