import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# STREAMLIT PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Amazon Review Intelligence",
    page_icon="🛒",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM CSS (MODERN UI)
# --------------------------------------------------
st.markdown("""
<style>
body { background-color: #f6f7fb; }

h1 {
    text-align: center;
    color: #1f2c38;
}

.card {
    background: white;
    padding: 22px;
    border-radius: 14px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.08);
    margin-bottom: 22px;
}

.section {
    font-size: 18px;
    font-weight: 600;
    margin-top: 15px;
    color: #2c3e50;
}

.small { color: #6c757d; }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# LOAD DATASET
# --------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("final_product_dataset.csv")   # <-- Your correct dataset name

raw_df = load_data()

# --------------------------------------------------
# BUILD SENTIMENT LABELS
# --------------------------------------------------
raw_df["sentiment"] = raw_df["rating"].apply(
    lambda r: "Positive" if r >= 4 else "Neutral" if r == 3 else "Negative"
)

sentiment_map = {"Positive": 1, "Neutral": 0, "Negative": -1}
raw_df["sentiment_score"] = raw_df["sentiment"].map(sentiment_map)

# --------------------------------------------------
# AGGREGATE TO PRODUCT LEVEL
# --------------------------------------------------
product_df = raw_df.groupby(["product_title", "domain"]).agg(
    avg_rating=("rating", "mean"),
    review_count=("rating", "count"),
    avg_sentiment_score=("sentiment_score", "mean")
).reset_index()

# --------------------------------------------------
# TOP HEADER
# --------------------------------------------------
st.markdown("<h1>🛒 Amazon Review Intelligence Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p class='small' style='text-align:center;'>Cross-domain Sentiment • Review Summaries • Buying Guide • Smart AI Assistant</p>", unsafe_allow_html=True)
st.markdown("---")

# --------------------------------------------------
# SEARCH + CATEGORY FILTER
# --------------------------------------------------
c1, c2 = st.columns([3, 1])

with c1:
    query = st.text_input("🔍 Search product", placeholder="Search phones, books, shirts...")

with c2:
    domain_filter = st.selectbox("Category", ["All", "Books", "Electronics", "Clothing"])

filtered = product_df.copy()

if domain_filter != "All":
    filtered = filtered[filtered["domain"] == domain_filter]

if query:
    filtered = filtered[filtered["product_title"].str.contains(query, case=False, na=False)]

# --------------------------------------------------
# RESULTS AREA
# --------------------------------------------------
st.subheader("🔎 Search Results")

if filtered.empty:
    st.warning("No matching products found.")
else:
    for _, row in filtered.iterrows():

        st.markdown("<div class='card'>", unsafe_allow_html=True)

        # Title + Rating Block
        tcol, rcol = st.columns([4, 1])
        with tcol:
            st.markdown(f"### {row['product_title']}")
        with rcol:
            st.metric("⭐ Rating", round(row["avg_rating"], 2))

        st.caption(f"Total Reviews: {row['review_count']}")

        # Summary placeholder
        st.markdown("<div class='section'>📘 Review Summary</div>", unsafe_allow_html=True)
        st.write("Users shared mixed feedback based on overall sentiment signals extracted from review text.")

        # Sentiment Meter
        st.markdown("<div class='section'>🎛 Sentiment Meter</div>", unsafe_allow_html=True)
        meter_val = (row["avg_sentiment_score"] + 1) / 2
        st.progress(meter_val)

        # Buying Guide Logic
        st.markdown("<div class='section'>🎯 Buying Recommendation</div>", unsafe_allow_html=True)
        if row["avg_rating"] >= 4:
            st.success("Must Buy")
        elif row["avg_rating"] < 3:
            st.error("Avoid")
        else:
            st.warning("Think Again")

        # -------------------------------
        # SENTIMENT PIE & BAR CHARTS
        # -------------------------------
        product_reviews = raw_df[raw_df["product_title"] == row["product_title"]]

        pos = (product_reviews["sentiment"] == "Positive").sum()
        neu = (product_reviews["sentiment"] == "Neutral").sum()
        neg = (product_reviews["sentiment"] == "Negative").sum()

        sentiment_df = pd.DataFrame({
            "Sentiment": ["Positive", "Neutral", "Negative"],
            "Count": [pos, neu, neg]
        })

        st.markdown("<div class='section'>📊 Sentiment Breakdown</div>", unsafe_allow_html=True)

        # PIE
        fig_pie = px.pie(
            sentiment_df,
            values="Count",
            names="Sentiment",
            color="Sentiment",
            color_discrete_map={
                "Positive": "#4CAF50",
                "Neutral": "#FFC107",
                "Negative": "#F44336"
            }
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        # BAR
        fig_bar = px.bar(
            sentiment_df,
            x="Sentiment",
            y="Count",
            text="Count",
            color="Sentiment",
            color_discrete_map={
                "Positive": "#4CAF50",
                "Neutral": "#FFC107",
                "Negative": "#F44336"
            }
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# SMART CHATBOT
# --------------------------------------------------
st.markdown("---")
st.subheader("🤖 Smart Recommendation Assistant")

user_q = st.text_input(
    "Ask anything...",
    placeholder="Suggest me a good phone / book / comfortable clothing"
)

if user_q:
    q = user_q.lower()

    if "phone" in q or "mobile" in q:
        subset = product_df[product_df["domain"] == "Electronics"]
    elif "book" in q:
        subset = product_df[product_df["domain"] == "Books"]
    elif "cloth" in q or "shirt" in q or "dress" in q:
        subset = product_df[product_df["domain"] == "Clothing"]
    else:
        subset = product_df

    best = subset.sort_values("avg_rating", ascending=False).iloc[0]

    st.success(
        f"### ✅ Recommended Product\n\n"
        f"**{best['product_title']}**\n"
        f"- ⭐ Rating: {round(best['avg_rating'], 2)}\n"
        f"- 🛒 Category: {best[']()
