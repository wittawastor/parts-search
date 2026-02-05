import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Parts Search", layout="wide")
st.title("🔍 Parts Search Engine")

# ---------------- NORMALIZE TEXT ----------------

def normalize(text):
    text = str(text).lower()
    text = re.sub(r"[-_/]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

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

    # 🔑 GOOGLE-LIKE SEARCH TEXT  ✅ INSIDE FUNCTION
    df["SEARCH"] = (
        df["PartNumber"] + " " +
        df["Brand"] + " " +
        df["Model"] + " " +
        df["Category"] + " " +
        df["EN_Name"] + " " +
        df["TH_Name"]
    ).apply(normalize)

    return df

    return df

df = load_data()
st.caption(f"📦 Total parts: {len(df):,}")

# ---------------- SEARCH ----------------
query = st.text_input(
    "Smart search (Google-style)",
    placeholder="SX3 bar black, 5VX2586A, zeta tmax brake"
)

if query:
    q = normalize(query)
keywords = [k for k in q.split(" ") if k]

    # ⚡ FAST filtering (contains ALL keywords)
    mask = df["SEARCH"].apply(
        lambda x: all(k in x for k in keywords)
    )

    result = df[mask].copy()

    # If too many or zero → fallback fuzzy
    if len(result) == 0 or len(result) > 2000:
        from rapidfuzz import process, fuzz

        matches = process.extract(
            q,
            df["SEARCH"],
            scorer=fuzz.WRatio,
            limit=300
        )

        idx = [m[2] for m in matches if m[1] > 55]
        result = df.iloc[idx].copy()
        result["Score"] = [m[1] for m in matches[:len(result)]]
    else:
        # Score by number of matched keywords
        result["Score"] = result["SEARCH"].apply(
            lambda x: sum(k in x for k in keywords)
        )

    result = result.sort_values("Score", ascending=False)

    st.success(f"Found {len(result):,} results")

    # ---------------- SUMMARY ----------------
    st.subheader("📊 Summary")

    pivot = (
        result
        .groupby(["Brand", "Model", "Year", "Category"])
        .size()
        .reset_index(name="Parts")
        .sort_values("Parts", ascending=False)
    )

    st.dataframe(pivot, use_container_width=True)

    # ---------------- DETAILS ----------------
    st.subheader("📄 Matching Parts")

    st.dataframe(
        result[[
            "Brand", "Model", "Year", "PartNumber",
            "Category", "EN_Name", "TH_Name",
            "Price", "URL"
        ]],
        use_container_width=True
    )

    # ---------------- PRODUCT LINKS ----------------
    st.subheader("🔗 Open Product Page")

    for _, row in result.head(20).iterrows():
        cols = st.columns([3, 4, 2, 2, 2])
        cols[0].markdown(f"**{row['Brand']}**")
        cols[1].markdown(row["PartNumber"])
        cols[2].markdown(row["Year"])
        cols[3].markdown(f"฿{row['Price']}")
        cols[4].link_button("Open", row["URL"])

else:
    st.info("Type anything — dash, typo, spacing doesn’t matter")
