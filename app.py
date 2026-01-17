import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
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
body {
    background-color: #f6f7fb;
}
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
    margin-top: 10px;
    color: #2c3e50;
}
.small {
    color: #6c757d;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("final_product_dataset.csv")

df = load_data()

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown("<h1>🛒 Amazon Review Intelligence Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p class='small' style='text-align:center;'>Cross-Domain Sentiment • Summaries • Buying Guide</p>", unsafe_allow_html=True)
st.markdown("---")

# --------------------------------------------------
# SEARCH + FILTER
# --------------------------------------------------
c1, c2 = st.columns([3, 1])

with c1:
    query = st.text_input("🔍 Search product", placeholder="Search books, phones, clothing...")

with c2:
    domain = st.selectbox("Category", ["All", "Books", "Electronics", "Clothing"])

filtered = df.copy()

if domain != "All":
    filtered = filtered[filtered["domain"] == domain]

if query:
    filtered = filtered[filtered["product_title"].str.contains(query, case=False, na=False)]

# --------------------------------------------------
# RESULTS
# --------------------------------------------------
st.subheader("🔎 Search Results")

if filtered.empty:
    st.warning("No products found.")
else:
    for _, row in filtered.iterrows():

        st.markdown("<div class='card'>", unsafe_allow_html=True)

        # Title + Rating
        tcol, rcol = st.columns([4, 1])
        with tcol:
            st.markdown(f"### {row['product_title']}")
        with rcol:
            st.metric("⭐ Rating", round(row["avg_rating"], 2))

        # Summary
        st.markdown("<div class='section'>📘 Review Summary</div>", unsafe_allow_html=True)
        st.write(row["review_summary"])

        # Sentiment Meter
        st.markdown("<div class='section'>🎛 Sentiment Meter</div>", unsafe_allow_html=True)
        meter = (row["avg_sentiment_score"] + 1) / 2
        st.progress(meter)

        # Buying Guide
        st.markdown("<div class='section'>🎯 Buying Recommendation</div>", unsafe_allow_html=True)
        if row["buying_recommendation"] == "Must Buy":
            st.success("Must Buy")
        elif row["buying_recommendation"] == "Avoid":
            st.error("Avoid")
        else:
            st.warning("Think Again")

        # Charts
        chart_df = pd.DataFrame({
            "Sentiment": ["Positive", "Neutral", "Negative"],
            "Count": [
                row["positive_reviews"],
                row["neutral_reviews"],
                row["negative_reviews"]
            ]
        })

        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(
                px.pie(chart_df, values="Count", names="Sentiment"),
                use_container_width=True
            )
        with c2:
            st.plotly_chart(
                px.bar(chart_df, x="Sentiment", y="Count", text="Count"),
                use_container_width=True
            )

        st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# CHATBOT (RULE-BASED)
# --------------------------------------------------
st.markdown("---")
st.subheader("🤖 Smart Recommendation Assistant")

user_q = st.text_input(
    "Ask something like:",
    placeholder="Best phone • Good book for mindset • Comfortable clothing"
)

if user_q:
    q = user_q.lower()

    if "phone" in q or "mobile" in q:
        subset = df[df["domain"] == "Electronics"]
    elif "book" in q:
        subset = df[df["domain"] == "Books"]
    elif "cloth" in q or "shirt" in q or "dress" in q:
        subset = df[df["domain"] == "Clothing"]
    else:
        subset = df

    best = subset.sort_values("avg_rating", ascending=False).iloc[0]

    st.success(
        f"### ✅ Recommended: {best['product_title']}\n\n"
        f"**Why:** {best['review_summary']}"
    )
