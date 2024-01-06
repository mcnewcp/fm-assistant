import streamlit as st
import pandas as pd

# Parameters - these should be converted to user selections
role = "CM-Mezzala At"
selected_cols = ["Age", "Personality", "Height"]


# function for reading table from html
def read_html_file(uploaded_file):
    # Read the HTML table with utf-8 encoding
    df_list = pd.read_html(uploaded_file, encoding="utf-8")

    # Select the relevant DataFrame from the list of DataFrames if there are multiple tables
    return df_list[0] if df_list else None


# function to score squad on a role
def score_squad(
    role: str, df_role: pd.DataFrame, df_squad: pd.DataFrame, selected_cols: list
):
    # generate weight dict for role
    role_dict = df_role.query("Role==@role")[all_attributes].to_dict("records")[0]

    # list primary and secondary attributes
    primary_attributes = [attr for attr, weight in role_dict.items() if weight == 1]
    secondary_attributes = [
        attr for attr, weight in role_dict.items() if weight > 0 and weight < 1
    ]

    # score squad members
    scores = df_squad.set_index("Name")[all_attributes].mul(role_dict).sum(axis=1)
    total_weight = 0
    for attr, weight in role_dict.items():
        if pd.notna(weight):
            total_weight += weight
    norm_scores = scores / total_weight

    # compile score df and return
    df_squad_scores = pd.DataFrame({role: norm_scores})
    df_squad_scores = df_squad_scores.join(
        df_squad.set_index("Name")[
            selected_cols + primary_attributes + secondary_attributes
        ]
    ).reset_index()
    return df_squad_scores


st.title("Football Manager Assistant")

# load roles
df_role = pd.read_csv("role-config.csv")
all_attributes = df_role.drop(columns=["Role"]).columns.to_list()

# sidebar
with st.sidebar:
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
        df_squad_scores = score_squad(role, df_role, df_squad, selected_cols)

        if df_squad_scores is not None:
            # Display the DataFrame in an interactive table
            st.dataframe(df_squad_scores, use_container_width=True, hide_index=True)
