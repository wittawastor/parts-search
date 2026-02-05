import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Parts Search",
    layout="wide"
)

st.title("🔍 Parts Search Engine")

# ---------------- LOAD DATA (FAST & SAFE) ----------------
@st.cache_data
def load_data():
    df = pd.read_excel("Guide Data 20260122.xlsx")

    # Select only needed columns: A B C D E F G I
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

    # Convert to string
    df = df.astype(str)

    # 🔥 Create ONE combined search column (speed boost)
    df["SEARCH"] = (
        df["Brand"] + " " +
        df["Model"] + " " +
        df["Year"] + " " +
        df["PartNumber"] + " " +
        df["Category"] + " " +
        df["EN_Name"] + " " +
        df["TH_Name"]
    ).str.lower()

    return df

df = load_data()

st.caption(f"📦 Total parts: {len(df):,}")

# ---------------- SEARCH UI ----------------
search = st.text_input(
    "Search by part number or keyword",
    placeholder="Example: ZETA, TMAX, 5VX-2586A, brake, ผ้าเบรก"
)

if search:
    keyword = search.lower()

    # ⚡ FAST SEARCH
    result = df[df["SEARCH"].str.contains(keyword, na=False)]

    st.success(f"Found {len(result):,} results")

    # ---------------- PIVOT SUMMARY ----------------
    st.subheader("📊 Summary")

    pivot = (
        result
        .groupby(["Brand", "Model", "Year", "Category"])
        .size()
        .reset_index(name="Parts")
        .sort_values("Parts", ascending=False)
    )

    st.dataframe(pivot, use_container_width=True)

    # ---------------- DETAIL TABLE ----------------
    st.subheader("📄 Part Details")

    display_df = result[[
        "Brand",
        "Model",
        "Year",
        "PartNumber",
        "Category",
        "EN_Name",
        "TH_Name",
        "URL"
    ]].copy()

    st.dataframe(display_df, use_container_width=True)

    # ---------------- CLICKABLE PRODUCT BUTTONS ----------------
    st.subheader("🔗 Open Product Page")

    # Limit buttons for mobile usability
    for _, row in display_df.head(20).iterrows():
        cols = st.columns([2, 4, 2, 2])
        cols[0].markdown(f"**{row['Brand']}**")
        cols[1].markdown(row["PartNumber"])
        cols[2].markdown(row["Year"])
        cols[3].link_button("Open", row["URL"])

else:
    st.info("Start typing to search your parts")
