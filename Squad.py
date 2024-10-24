import streamlit as st
from streamlit import session_state as ss
import pandas as pd
import datetime
from utils import (
    load_squad,
    load_squad_plan,
    load_role_config,
    reset_upload_keys,
    update_squad_plan,
    rate_squad_all_roles,
    pivot_squad_plan_wide,
    style_squad_plan,
    pd_styler,
    get_column_config,
    pivot_squad_plan_long,
    attach_uid,
    save_squad_plan_csv,
    update_squad_csv,
)

st.title("Football Manager Assistant ⚽️🤖")
st.subheader("Squad Planner")

# Load the CSV files into DataFrames in session_state
# TODO: these should connect to Deta Base databases
if "squad_db" not in st.session_state:
    st.session_state.squad_db = pd.read_csv("data/squad.csv", parse_dates=["Date"])
if "squad_plan_db" not in st.session_state:
    st.session_state.squad_plan_db = pd.read_csv(
        "data/squad_plan.csv", parse_dates=["date"]
    )
if "df_role_config" not in st.session_state:
    st.session_state.df_role_config = pd.read_csv("role-config.csv")

# load most recent dfs
squad_date = st.session_state.squad_db.Date.max()
df_squad = st.session_state.squad_db[st.session_state.squad_db["Date"] == squad_date]
squad_plan_date = st.session_state.squad_plan_db.date.max()
df_squad_plan = st.session_state.squad_plan_db[
    st.session_state.squad_plan_db["date"] == squad_plan_date
]

# load lists
all_roles = st.session_state.df_role_config["Role"].unique()
all_names = df_squad["Name"].unique()
all_teams = df_squad["Team"].unique()

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

st.data_editor(df_squad_plan)

# # set up squad planner df
# rating_cols = [f"rating_{i}" for i in range(1, depth + 1)]
# age_cols = [f"age_{i}" for i in range(1, depth + 1)]


# # apply conditional formatting to rating cols
# def pd_styler(styler, rating_cols: list, age_cols: list):
#     styler.format(precision=2, subset=rating_cols)
#     styler.format(precision=0, subset=age_cols)
#     styler.background_gradient(axis=None, cmap="RdYlGn", subset=rating_cols)
#     return styler


# df_squad_planner_styled = df_squad_planner.style.pipe(
#     pd_styler, rating_cols=rating_cols, age_cols=age_cols
# )

# # display squad planner df
# column_config = {
#     "position": st.column_config.TextColumn(
#         "Position",
#         help="Enter any position, doesn't affect calculations",
#     ),
#     "role": st.column_config.SelectboxColumn(
#         "Role", help="Select role to calculate ratings", options=all_roles
#     ),
# }
# # Add entries to column_config for each player depth
# for i in range(1, depth + 1):
#     column_config[f"name_{i}"] = st.column_config.SelectboxColumn(
#         "Name", help="Select player name", options=all_names
#     )
#     column_config[f"age_{i}"] = st.column_config.NumberColumn(
#         "Age", help="Age of player", disabled=True
#     )
#     column_config[f"rating_{i}"] = st.column_config.NumberColumn(
#         "Rating", help="Rating of player in chosen role", disabled=True
#     )
# st.data_editor(
#     df_squad_planner_styled,
#     disabled=rating_cols + age_cols,
#     column_config=column_config,
#     num_rows="fixed",
#     hide_index=True,
# )
# Initialize session state
# TODO: these should connect to supabase databases
if "df_role_config" not in ss:
    load_role_config()
if "df_squad" not in ss:
    load_squad()
if "df_squad_plan" not in ss:
    load_squad_plan()
if "upload_keys" not in ss:
    reset_upload_keys()

# load lists
all_roles = ss.df_role_config["Role"].unique()
all_names = ss.df_squad["Name"].unique()
all_teams = ss.df_squad["Team"].unique()
all_attributes = ss.df_role_config.drop(columns=["Role"]).columns.to_list()

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
            st.info("Squad plan loaded!")

        if new_date:
            # save squad plan
            save_squad_plan_button = st.button(
                "Save Squad Plan", help="Save the current squad plan in the database"
            )
            if save_squad_plan_button:
                save_squad_plan_csv(ss.df_squad_plan, new_date)
                st.info("Squad plan saved!")

    with st.container(border=True):
        st.write("Update Squad")
        if new_date:
            updloaded_squad_file_senior = st.file_uploader(
                "Senior Team Export",
                type=["html"],
                accept_multiple_files=False,
                key=ss.upload_keys[0],
            )
            uploaded_squad_file_u21 = st.file_uploader(
                "U21 Team Export",
                type=["html"],
                accept_multiple_files=False,
                key=ss.upload_keys[1],
            )
            uploaded_squad_file_u18 = st.file_uploader(
                "U18 Team Export",
                type=["html"],
                accept_multiple_files=False,
                key=ss.upload_keys[2],
            )

            if (
                updloaded_squad_file_senior
                and uploaded_squad_file_u21
                and uploaded_squad_file_u18
            ):
                update_squad_button = st.button(
                    "Update Squad", help="Update the squad database"
                )
                if update_squad_button:
                    update_squad_csv(
                        updloaded_squad_file_senior,
                        uploaded_squad_file_u21,
                        uploaded_squad_file_u18,
                        new_date,
                    )
                    load_squad()
                    ss.df_squad_plan = update_squad_plan(ss.df_squad_plan)
                    reset_upload_keys()
                    st.rerun()

# pivot wide for display
df_display = pivot_squad_plan_wide(ss.df_squad_plan, depth)

# display formatted squad planner
with st.container(border=True):
    st.markdown("## Squad Planner")
    column_config = get_column_config(depth, all_roles, all_names)
    df_display_edited = st.data_editor(
        style_squad_plan(df_display),
        column_config=column_config,
        num_rows="fixed",
        hide_index=True,
    )

# check for changes
if not df_display_edited.equals(df_display):
    # pivot long, update age & rating, overwrite ss squad plan
    ss.df_squad_plan = (
        df_display_edited.pipe(
            pivot_squad_plan_long, depth=depth
        )  # pivot long for calc
        .pipe(attach_uid)  # attach UID for attribute lookup
        .pipe(update_squad_plan)  # update age, rating
    )
    st.rerun()

# squad role ratings display
with st.container(border=True):
    st.markdown("## Squad Ratings")
    team_selection = st.multiselect("Teams Included", all_teams, all_teams)
    update_squad_roles_button = st.button("Update Calculations")
    if "df_squad_all_roles" not in ss:
        ss.df_squad_all_roles = rate_squad_all_roles(team_selection).drop(
            columns=all_attributes + ["UID"]
        )
    if update_squad_roles_button:
        ss.df_squad_all_roles = rate_squad_all_roles(team_selection).drop(
            columns=all_attributes + ["UID"]
        )

    st.dataframe(  # apply styling
        ss.df_squad_all_roles.style.pipe(
            pd_styler,
            rating_cols=list(ss.df_squad_plan.role.unique()) + ["best_rating"],
            age_cols=["Age"],
        )
    )
