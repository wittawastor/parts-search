import streamlit as st
import pandas as pd

st.set_page_config(page_title="Parts Search", layout="wide")

st.title("🔍 Parts Search Engine")

@st.cache_data
def load_data():
    df = pd.read_excel("Guide Data 20260122.xlsx")

    # Show real columns (for safety)
    df = df.iloc[:, [0, 1, 2, 3, 4, 5, 6, 8]]

    df.columns = [
        "Brand",
        "Model",
        "Year",
        "PartNumber",
        "Category",
        "EN_Name",
        "TH_Name",
        "URL",
    ]

    df = df.astype(str)
    return df

df = load_data()

st.caption(f"Total records: {len(df):,}")

search = st.text_input(
    "Search by part number, brand, model, or description",
    placeholder="Example: ZETA, 5VX-2586A, brake, ผ้าเบรก"
)

if search:
    result = df[
        df["PartNumber"].str.contains(search, case=False, na=False)
        | df["Brand"].str.contains(search, case=False, na=False)
        | df["Model"].str.contains(search, case=False, na=False)
        | df["Category"].str.contains(search, case=False, na=False)
        | df["EN_Name"].str.contains(search, case=False, na=False)
        | df["TH_Name"].str.contains(search, case=False, na=False)
    ]

    st.subheader(f"Results: {len(result):,}")

    st.dataframe(
        result[
            [
                "Brand",
                "Model",
                "Year",
                "PartNumber",
                "Category",
                "EN_Name",
                "TH_Name",
                "URL",
            ]
        ],
        use_container_width=True,
    )
else:
    st.info("Start typing to search your parts")
