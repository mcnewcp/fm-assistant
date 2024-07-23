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
    update_squad_csv,
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

    # user selections
    with st.container(border=True):
        st.write("User Inputs")
        # squad depth for each role
        depth = st.number_input(
            "Position Depth", 1, 10, 4, help="Depth to display for each role"
        )
        # in-game date for use with saving squad plan and updating squad
        new_date = st.date_input(
            "In-Game Date",
            None,
            datetime.date(2020, 1, 1),
            datetime.date(2050, 12, 31),
            help="In-Game date must be specified for saving a Squad Plan or updating the Squad",
        )

    with st.container(border=True):
        st.write("Update Squad Plan")
        # load the most recent squad plan
        load_squad_plan_button = st.button(
            "Load Squad Plan", "Load the most recent squad plan"
        )
        if load_squad_plan_button:
            load_squad_plan()
        if new_date:
            # save squad plan
            save_squad_plan_button = st.button(
                "Save Squad Plan", help="Save the current squad plan in the database"
            )
            if save_squad_plan_button:
                save_squad_plan_csv(ss.df_squad_plan, new_date)

    with st.container(border=True):
        st.write("Update Squad")
        if new_date:
            update_squad_file_senior = st.file_uploader(
                "Senior Team Export", type=["html"], accept_multiple_files=False
            )
            update_squad_file_u21 = st.file_uploader(
                "U21 Team Export", type=["html"], accept_multiple_files=False
            )
            update_squad_file_u18 = st.file_uploader(
                "U18 Team Export", type=["html"], accept_multiple_files=False
            )

            if (
                update_squad_file_senior
                and update_squad_file_u21
                and update_squad_file_u18
            ):
                update_squad_button = st.button(
                    "Update Squad", help="Update the squad database"
                )
                if update_squad_button:
                    update_squad_csv(update_squad_file_senior, "Senior", new_date)
                    update_squad_csv(update_squad_file_u21, "U21", new_date)
                    update_squad_csv(update_squad_file_u18, "U18", new_date)
                    load_squad()
                    st.info("Squad updated!")
                    st.rerun()

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
