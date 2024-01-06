import pandas as pd


# function for reading table from html
def read_html_file(uploaded_file):
    # Read the HTML table with utf-8 encoding
    df_list = pd.read_html(uploaded_file, encoding="utf-8")

    # Select the relevant DataFrame from the list of DataFrames if there are multiple tables
    return df_list[0] if df_list else None


# function to score squad on a role
def score_squad(
    role: str,
    df_role: pd.DataFrame,
    df_squad: pd.DataFrame,
    selected_cols: list,
    all_attributes: list,
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
