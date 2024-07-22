import streamlit as st
import pandas as pd
import datetime


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
