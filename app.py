import streamlit as st
import pandas as pd


# function for reading table from html
def read_html_file(uploaded_file):
    # Read the HTML table with utf-8 encoding
    df_list = pd.read_html(uploaded_file, encoding="utf-8")

    # Select the relevant DataFrame from the list of DataFrames if there are multiple tables
    return df_list[0] if df_list else None


st.title("Football Manager Assistant")

# sidebar
with st.sidebar:
    uploaded_file = st.file_uploader("Choose an HTML file", type="html")

if uploaded_file is not None:
    # Check if the uploaded file has an HTML extension
    if not uploaded_file.name.endswith(".html"):
        st.error("Error: Please upload a valid HTML file.")
    else:
        # Read HTML file and display DataFrame
        df = read_html_file(uploaded_file)

        if df is not None:
            # Display the DataFrame in an interactive table
            st.dataframe(df)
