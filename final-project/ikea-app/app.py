from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).parent

st.set_page_config(
    page_title="Furniture Product Launch Advisor",
    layout="wide"
)

model = joblib.load(BASE_DIR / "ikea_interest_model.pkl")
data = pd.read_csv(BASE_DIR / "ikea_model_dataset.csv")

st.title("Furniture Product Launch Advisor")

st.write(
    "This tool helps product teams estimate whether a furniture product is likely to receive high consumer interest. "
    "It uses IKEA product data including category, price, rating, and product page information."
)

st.divider()

st.sidebar.header("Product Inputs")

category = st.sidebar.selectbox(
    "Product category",
    sorted(data["category"].unique())
)

price = st.sidebar.number_input(
    "Planned price ($)",
    min_value=1.0,
    value=99.0,
    step=10.0
)

rating = st.sidebar.slider(
    "Expected customer rating",
    min_value=1.0,
    max_value=5.0,
    value=4.5,
    step=0.1
)

detail_level = st.sidebar.selectbox(
    "Product information level",
    ["Basic", "Standard", "Detailed", "Rich"],
    index=1,
    help="This represents how much information is available on the product page."
)

detail_map = {
    "Basic": 1000,
    "Standard": 2000,
    "Detailed": 3000,
    "Rich": 4000,
}

page_text_length = detail_map[detail_level]
name_length = int(data["name_length"].median())

input_df = pd.DataFrame([
    {
        "category": category,
        "price": price,
        "rating": rating,
        "name_length": name_length,
        "page_text_length": page_text_length,
    }
])

category_data = data[data["category"] == category]

category_avg_price = category_data["price"].mean()
category_avg_rating = category_data["rating"].mean()
category_median_reviews = category_data["review_count"].median()

prediction = model.predict(input_df)[0]
probability = model.predict_proba(input_df)[0][1]
interest_score = round(probability * 100)

left, right = st.columns([1.1, 1])

with left:
    st.subheader("Prediction Result")

    if prediction == 1:
        st.success("Likely High Interest")
    else:
        st.warning("Likely Low Interest")

    st.metric("Predicted Interest Score", f"{interest_score}/100")
    st.progress(probability)

    if interest_score >= 70:
        st.write("This product has strong launch potential based on the model.")
    elif interest_score >= 50:
        st.write("This product has moderate potential and may need stronger positioning.")
    else:
        st.write("This product may face launch risk and should be improved before launch.")

with right:
    st.subheader("Category Benchmark")

    c1, c2, c3 = st.columns(3)
    c1.metric("Category Avg Price", f"${category_avg_price:.0f}")
    c2.metric("Category Avg Rating", f"{category_avg_rating:.2f}")
    c3.metric("Median Reviews", f"{int(category_median_reviews)}")

st.divider()

st.subheader("Business Recommendation")

recommendations = []

if price < category_avg_price:
    recommendations.append(
        "Price is below the category average, which may support stronger customer interest."
    )
elif price > category_avg_price * 1.2:
    recommendations.append(
        "Price is significantly above the category average. The product may need stronger differentiation."
    )
else:
    recommendations.append(
        "Price is close to the category average, suggesting balanced positioning."
    )

if rating >= category_avg_rating:
    recommendations.append(
        "Expected rating is above the category average, which supports customer trust."
    )
else:
    recommendations.append(
        "Expected rating is below the category average, so quality perception may be a risk."
    )

if page_text_length >= data["page_text_length"].median():
    recommendations.append(
        "Product information is relatively rich, which may help customers evaluate the product."
    )
else:
    recommendations.append(
        "Product information is limited. Adding more product details may improve customer confidence."
    )

for item in recommendations:
    st.write("- " + item)

if interest_score >= 70:
    st.success("Recommended Action: Launch with current positioning.")
elif interest_score >= 50:
    st.info("Recommended Action: Launch carefully and improve product messaging.")
else:
    st.error("Recommended Action: Reconsider pricing, rating assumptions, or product page quality before launch.")

st.divider()

st.subheader("Pricing What-if Analysis")

scenario_prices = {
    "10% Lower Price": price * 0.9,
    "Current Price": price,
    "10% Higher Price": price * 1.1,
}

scenario_rows = []

for scenario, scenario_price in scenario_prices.items():
    scenario_df = input_df.copy()
    scenario_df["price"] = scenario_price
    scenario_prob = model.predict_proba(scenario_df)[0][1]

    scenario_rows.append({
        "Scenario": scenario,
        "Price": round(scenario_price, 2),
        "Interest Score": round(scenario_prob * 100),
    })

scenario_df = pd.DataFrame(scenario_rows)

st.dataframe(scenario_df, use_container_width=True)

best_row = scenario_df.sort_values("Interest Score", ascending=False).iloc[0]

st.write(
    f"Best scenario in this test: **{best_row['Scenario']}** with an interest score of **{best_row['Interest Score']}/100**."
)

st.divider()

st.subheader("Price Sensitivity Analysis")

price_points = [
    max(1, price * 0.5),
    price * 0.75,
    price,
    price * 1.25,
    price * 1.5,
]

sensitivity_rows = []

for test_price in price_points:
    test_df = input_df.copy()
    test_df["price"] = test_price

    test_prob = model.predict_proba(test_df)[0][1]

    sensitivity_rows.append({
        "Price": round(test_price, 2),
        "Interest Score": round(test_prob * 100, 1),
    })

sensitivity_df = pd.DataFrame(sensitivity_rows)

st.line_chart(
    sensitivity_df.set_index("Price")
)

st.write(
    "This chart shows how the predicted interest score changes under different launch price assumptions."
)

st.divider()

st.subheader("Dataset Used")

d1, d2, d3, d4 = st.columns(4)
d1.metric("Products", len(data))
d2.metric("Categories", data["category"].nunique())
d3.metric("Median Review Count", int(data["review_count"].median()))
d4.metric("Model", "Random Forest")

with st.expander("View sample IKEA product data"):
    st.dataframe(
        data[
            ["name", "category", "price", "rating", "review_count", "high_interest"]
        ].head(20),
        use_container_width=True
    )
