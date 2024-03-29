import pandas as pd


# function for reading table from html
def read_html_file(uploaded_file):
    # Read the HTML table with utf-8 encoding
    df_list = pd.read_html(uploaded_file, encoding="utf-8")

    # Select the relevant DataFrame from the list of DataFrames if there are multiple tables
    df = df_list[0]

    # drop any rows that are all NAs
    return df.dropna(how="all")


# function to score players on one or more roles
def score_players(
    roles: list,
    df: pd.DataFrame,
    selected_cols: list,
):
    # load role config
    df_role = pd.read_csv("role-config.csv")
    all_attributes = df_role.drop(columns=["Role"]).columns.to_list()

    # instantiate objects
    primary_attributes = []
    secondary_attributes = []
    df_scores = pd.DataFrame(df["Name"]).set_index("Name")

    for role in roles:
        # generate weight dict for role
        role_dict = df_role.query("Role==@role")[all_attributes].to_dict("records")[0]

        # list primary and secondary attributes
        primary_attributes_role = [
            attr for attr, weight in role_dict.items() if weight == 1
        ]
        secondary_attributes_role = [
            attr for attr, weight in role_dict.items() if weight > 0 and weight < 1
        ]

        # score squad members
        scores = df.set_index("Name")[all_attributes].mul(role_dict).sum(axis=1)
        total_weight = 0
        for attr, weight in role_dict.items():
            if pd.notna(weight):
                total_weight += weight
        norm_scores = scores / total_weight

        # update objects
        primary_attributes = primary_attributes + primary_attributes_role
        secondary_attributes = secondary_attributes + secondary_attributes_role
        df_scores = df_scores.join(pd.DataFrame({role: norm_scores}))

    # get unique attribute lists
    primary_attributes = list(set(primary_attributes))
    secondary_attributes = list(set(secondary_attributes))
    secondary_attributes = [
        attr for attr in secondary_attributes if attr not in primary_attributes
    ]

    # compile score df and return
    df_scores = df_scores.join(
        df.set_index("Name")[selected_cols + primary_attributes + secondary_attributes]
    )

    return df_scores, primary_attributes, secondary_attributes


# function for summarizing scouting ranges by either mean, min, or max
def summarize_scouting_ranges(
    df_players: pd.DataFrame, summarization_method: str = "mean"
):
    # load a list of all attributes
    df_role = pd.read_csv("role-config.csv")
    all_attributes = df_role.drop(columns=["Role"]).columns.to_list()

    # Function to convert string ranges to mean values
    def summarize_range(value: str, summarization_method: str = "mean"):
        if value == "-":
            return 0
        elif "-" in value:
            start, end = map(int, value.split("-"))
            if summarization_method == "mean":
                return (start + end) / 2
            elif summarization_method == "min":
                return float(start)
            elif summarization_method == "max":
                return float(end)
        else:
            return float(value)

    # Apply the conversion function to all attribute columns
    df_players_fun = df_players.set_index("Name")
    df_attr = df_players_fun[all_attributes]
    df_attr = df_attr.map(summarize_range, summarization_method=summarization_method)

    # re-join and return
    df_out = df_players_fun.drop(columns=all_attributes).join(df_attr)
    df_out.reset_index(inplace=True)
    return df_out
