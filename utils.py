import pandas as pd
import streamlit as st
from streamlit import session_state as ss


# load df_squad into session state
def load_squad():
    squad_db = pd.read_csv("data/squad.csv", parse_dates=["Date"])
    recent_date = squad_db.Date.max()
    df_squad = squad_db[squad_db["Date"] == recent_date]
    ss.df_squad = df_squad


# load df_squad_plan into session state
def load_squad_plan():
    squad_plan_db = pd.read_csv("data/squad_plan.csv", parse_dates=["date"])
    recent_date = squad_plan_db.date.max()
    df_squad_plan = squad_plan_db[squad_plan_db["date"] == recent_date]
    ss.df_squad_plan = df_squad_plan


# load role config into session state
def load_role_config():
    ss.df_role_config = pd.read_csv("role-config.csv")


# attach name and updated age
def attach_player_cols(df):
    """
    Attach player name and age to the squad plan based on UID.
    """
    # Drop age column prior to updating
    df_out = df.drop(columns="age", errors="ignore")

    # Merge squad plan with squad to get name and age
    df_out = df_out.merge(ss.df_squad[["UID", "Name", "Age"]], on="UID", how="left")

    # Rename the columns to match the expected output
    df_out.rename(columns={"Name": "name", "Age": "age"}, inplace=True)

    return df_out


# attach ratings to squad plan df
def attach_rating(df):
    df_out = df.drop(columns="rating", errors="ignore")

    # Apply the rating calculation to each row in the squad plan
    df_out["rating"] = df_out.apply(
        lambda row: _calculate_rating(row["UID"], row["role"]), axis=1
    )

    return df_out


# calculate a player's rating for a role
def _calculate_rating(uid: str, role: str):
    # Fetch weights for role
    role_weights = ss.df_role_config[ss.df_role_config["Role"] == role].iloc[0][1:]

    # Fetch player attributes
    player_attributes = ss.df_squad[ss.df_squad["UID"] == uid].iloc[0]
    player_attributes = player_attributes[role_weights.index].fillna(0)

    # Calculate the rating
    weighted_attributes = player_attributes * role_weights
    rating = weighted_attributes.sum() / role_weights.sum()

    return rating


# pivot squad plan wide for display
def pivot_squad_plan_wide(df_long: pd.DataFrame, depth: int):
    # Initialize an empty list to store the wide format data
    wide_data = []

    # Get the unique combinations of position and role
    unique_positions_roles = df_long[["position", "role"]].drop_duplicates()

    # Iterate over each unique position and role
    for _, pos_role in unique_positions_roles.iterrows():
        position = pos_role["position"]
        role = pos_role["role"]

        # Filter the squad plan for the current position and role
        df_filtered = df_long[
            (df_long["position"] == position) & (df_long["role"] == role)
        ]

        # Initialize a dictionary to store the wide format data for the current position and role
        wide_row = {"position": position, "role": role}

        # Iterate over the range from 1 to depth to populate the name, age, and rating columns
        for i in range(1, depth + 1):
            choice_row = df_filtered[df_filtered["choice"] == i]
            if not choice_row.empty:
                wide_row[f"name_{i}"] = choice_row.iloc[0]["name"]
                wide_row[f"age_{i}"] = choice_row.iloc[0]["age"]
                wide_row[f"rating_{i}"] = choice_row.iloc[0]["rating"]
            else:
                wide_row[f"name_{i}"] = None
                wide_row[f"age_{i}"] = None
                wide_row[f"rating_{i}"] = None

        # Append the wide format row to the list
        wide_data.append(wide_row)

    # Convert the list of dictionaries to a DataFrame
    df_wide = pd.DataFrame(wide_data)

    return df_wide


# apply pandas styling to wide squad plan
def style_squad_plan(df: pd.DataFrame):
    # fetch col names
    age_cols = [col for col in df.columns if "age" in col]
    rating_cols = [col for col in df.columns if "rating" in col]

    # apply styling
    df_styled = df.style.pipe(_pd_styler, rating_cols=rating_cols, age_cols=age_cols)
    return df_styled


# pandas styler function
def _pd_styler(styler, rating_cols: list, age_cols: list):
    styler.format(precision=2, subset=rating_cols)
    styler.format(precision=0, subset=age_cols)
    styler.background_gradient(axis=None, cmap="RdYlGn", subset=rating_cols)
    return styler


# define config for data_editor display
def get_column_config(depth: int, all_roles: list, all_names: list):
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
        column_config[f"name_{i}"] = st.column_config.SelectboxColumn(
            "Name", help="Select player name", options=all_names
        )
        column_config[f"age_{i}"] = st.column_config.NumberColumn(
            "Age", help="Age of player", disabled=True
        )
        column_config[f"rating_{i}"] = st.column_config.NumberColumn(
            "Rating", help="Rating of player in chosen role", disabled=True
        )
    return column_config


# # function for reading table from html
# def read_html_file(uploaded_file):
#     # Read the HTML table with utf-8 encoding
#     df_list = pd.read_html(uploaded_file, encoding="utf-8")

#     # Select the relevant DataFrame from the list of DataFrames if there are multiple tables
#     df = df_list[0]

#     # drop any rows that are all NAs
#     return df.dropna(how="all")


# # function to score players on one or more roles
# def score_players(
#     roles: list,
#     df: pd.DataFrame,
#     selected_cols: list,
# ):
#     # load role config
#     df_role = pd.read_csv("role-config.csv")
#     all_attributes = df_role.drop(columns=["Role"]).columns.to_list()

#     # instantiate objects
#     df_scores = pd.DataFrame(df["UID"]).set_index("UID")

#     for role in roles:
#         # generate weight dict for role
#         role_dict = df_role.query("Role==@role")[all_attributes].to_dict("records")[0]

#         # score players
#         scores = df.set_index("UID")[all_attributes].mul(role_dict).sum(axis=1)
#         total_weight = 0
#         for attr, weight in role_dict.items():
#             if pd.notna(weight):
#                 total_weight += weight
#         norm_scores = scores / total_weight

#         # update objects
#         df_scores = df_scores.join(pd.DataFrame({role: norm_scores}))

#     # compile score df and return
#     df_scores = df_scores.join(df.set_index("UID")[selected_cols])

#     return df_scores


# # function for summarizing scouting ranges by either mean, min, or max
# def summarize_scouting_ranges(
#     df_players: pd.DataFrame, summarization_method: str = "mean"
# ):
#     # load a list of all attributes
#     df_role = pd.read_csv("role-config.csv")
#     all_attributes = df_role.drop(columns=["Role"]).columns.to_list()

#     # Function to convert string ranges to mean values
#     def summarize_range(value: str, summarization_method: str = "mean"):
#         if value == "-":
#             return 0
#         elif "-" in value:
#             start, end = map(int, value.split("-"))
#             if summarization_method == "mean":
#                 return (start + end) / 2
#             elif summarization_method == "min":
#                 return float(start)
#             elif summarization_method == "max":
#                 return float(end)
#         else:
#             return float(value)

#     # Apply the conversion function to all attribute columns
#     df_players_fun = df_players.set_index("Name")
#     df_attr = df_players_fun[all_attributes]
#     df_attr = df_attr.map(summarize_range, summarization_method=summarization_method)

#     # re-join and return
#     df_out = df_players_fun.drop(columns=all_attributes).join(df_attr)
#     df_out.reset_index(inplace=True)
#     return df_out
