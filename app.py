import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz

st.set_page_config(page_title="Parts Search", layout="wide")
st.title("🔍 Parts Search Engine")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_excel("Guide Data 20260122.xlsx")

    # A B C D E F G H I
    df = df.iloc[:, [0, 1, 2, 3, 4, 5, 6, 7, 8]]
    df.columns = [
        "Brand", "Model", "Year", "PartNumber",
        "Category", "EN_Name", "TH_Name",
        "Price", "URL"
    ]

    df = df.astype(str)

    # Search text for fuzzy matching
    df["SEARCH"] = (
        df["PartNumber"] + " " +
        df["Brand"] + " " +
        df["Model"] + " " +
        df["Category"] + " " +
        df["EN_Name"] + " " +
        df["TH_Name"]
    )

    return df

df = load_data()

st.caption(f"📦 Total parts: {len(df):,}")

# ---------------- SEARCH ----------------
query = st.text_input(
    "Smart search (Google-like)",
    placeholder="5VX 2586A, zta, tmax brake, ผ้าเบรค"
)

if query:
    # ⚡ Fuzzy ranking
    matches = process.extract(
        query,
        df["SEARCH"],
        scorer=fuzz.WRatio,
        limit=200
    )

    # Keep good matches only
    scores = [m[1] for m in matches]
    idx = [m[2] for m in matches if m[1] > 60]

    result = df.iloc[idx].copy()
    result["Score"] = scores[:len(result)]

    result = result.sort_values("Score", ascending=False)

    st.success(f"Top matches (ranked)")

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

    # ---------------- DETAIL ----------------
    st.subheader("📄 Best Matches")

    st.dataframe(
        result[[
            "Brand", "Model", "Year", "PartNumber",
            "Category", "EN_Name", "TH_Name",
            "Price", "Score", "URL"
        ]],
        use_container_width=True
    )

    # ---------------- PRODUCT BUTTONS ----------------
    st.subheader("🔗 Open Product Page")

    for _, row in result.head(20).iterrows():
        cols = st.columns([3, 4, 2, 2, 2])
        cols[0].markdown(f"**{row['Brand']}**")
        cols[1].markdown(row["PartNumber"])
        cols[2].markdown(row["Year"])
        cols[3].markdown(f"฿{row['Price']}")
        cols[4].link_button("Open", row["URL"])

else:
    st.info("Type anything — typo is OK")
