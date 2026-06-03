# Interactive Dashboard Example

## Overview

This example demonstrates how to build a complete interactive dashboard with Streamlit. We'll create a data analytics dashboard with multiple visualizations, filters, and interactive elements.

## What You'll Learn

- Building multi-page layouts
- Creating interactive filters
- Displaying multiple visualizations
- Implementing real-time updates
- Using session state for interactivity
- Organizing complex applications

## Dashboard Features

Our example dashboard includes:
- Data upload and preview
- Interactive filters (date range, categories, etc.)
- Multiple visualization types
- Summary statistics and KPIs
- Export functionality
- Responsive layout

## Complete Dashboard Code

```python
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.metric-card {
    background-color: #f0f2f6;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# Title
st.title("📈 Sales Analytics Dashboard")
st.markdown("---")

# Sidebar filters
st.sidebar.header("Filters")

# Date range filter
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(datetime.now() - timedelta(days=30), datetime.now()),
    max_value=datetime.now()
)

# Category filter
categories = st.sidebar.multiselect(
    "Select Categories",
    options=["Electronics", "Clothing", "Food", "Books", "Toys"],
    default=["Electronics", "Clothing"]
)

# Region filter
region = st.sidebar.selectbox(
    "Select Region",
    options=["All", "North", "South", "East", "West"]
)

# Load data (cached)
@st.cache_data
def load_data():
    # In real app, load from database or file
    import numpy as np
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    data = pd.DataFrame({
        'date': dates,
        'sales': np.random.randint(1000, 10000, len(dates)),
        'category': np.random.choice(['Electronics', 'Clothing', 'Food', 'Books', 'Toys'], len(dates)),
        'region': np.random.choice(['North', 'South', 'East', 'West'], len(dates)),
        'profit': np.random.randint(100, 1000, len(dates))
    })
    return data

df = load_data()

# Filter data based on selections
filtered_df = df[
    (df['date'] >= pd.to_datetime(date_range[0])) &
    (df['date'] <= pd.to_datetime(date_range[1])) &
    (df['category'].isin(categories))
]

if region != "All":
    filtered_df = filtered_df[filtered_df['region'] == region]

# KPI Metrics
st.subheader("Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_sales = filtered_df['sales'].sum()
    st.metric(
        label="Total Sales",
        value=f"${total_sales:,.0f}",
        delta=f"{(total_sales / df['sales'].sum() * 100):.1f}% of total"
    )

with col2:
    avg_sales = filtered_df['sales'].mean()
    st.metric(
        label="Average Daily Sales",
        value=f"${avg_sales:,.0f}",
        delta=f"{((avg_sales - df['sales'].mean()) / df['sales'].mean() * 100):.1f}%"
    )

with col3:
    total_profit = filtered_df['profit'].sum()
    st.metric(
        label="Total Profit",
        value=f"${total_profit:,.0f}",
        delta=f"{(total_profit / total_sales * 100):.1f}% margin"
    )

with col4:
    num_transactions = len(filtered_df)
    st.metric(
        label="Transactions",
        value=f"{num_transactions:,}",
        delta=f"{(num_transactions / len(df) * 100):.1f}% of total"
    )

st.markdown("---")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Sales Trend")
    daily_sales = filtered_df.groupby('date')['sales'].sum().reset_index()
    fig1 = px.line(
        daily_sales,
        x='date',
        y='sales',
        title="Daily Sales Over Time"
    )
    fig1.update_layout(height=400)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Sales by Category")
    category_sales = filtered_df.groupby('category')['sales'].sum().reset_index()
    fig2 = px.pie(
        category_sales,
        values='sales',
        names='category',
        title="Sales Distribution by Category"
    )
    fig2.update_layout(height=400)
    st.plotly_chart(fig2, use_container_width=True)

# Second row of charts
col3, col4 = st.columns(2)

with col3:
    st.subheader("Sales by Region")
    region_sales = filtered_df.groupby('region')['sales'].sum().reset_index()
    fig3 = px.bar(
        region_sales,
        x='region',
        y='sales',
        title="Sales by Region",
        color='sales',
        color_continuous_scale='Blues'
    )
    fig3.update_layout(height=400)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Profit vs Sales")
    fig4 = px.scatter(
        filtered_df,
        x='sales',
        y='profit',
        color='category',
        title="Profit vs Sales Relationship",
        trendline="ols"
    )
    fig4.update_layout(height=400)
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# Data table
with st.expander("📊 View Detailed Data"):
    st.dataframe(
        filtered_df.sort_values('date', ascending=False),
        use_container_width=True,
        height=400
    )
    
    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download Data as CSV",
        data=csv,
        file_name=f"sales_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.markdown("Dashboard last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
```

## Key Concepts Demonstrated

### 1. Layout Organization
- Wide layout for better use of screen space
- Columns for side-by-side content
- Expanders for optional content
- Sidebar for filters

### 2. Interactive Filters
- Date range selection
- Multi-select for categories
- Dropdown for single selection
- Filters update all visualizations

### 3. KPI Metrics
- Summary statistics at the top
- Delta indicators for changes
- Clear, concise presentation
- Responsive to filters

### 4. Multiple Visualizations
- Line charts for trends
- Pie charts for distributions
- Bar charts for comparisons
- Scatter plots for relationships

### 5. Data Management
- Caching for performance
- Filtering based on user input
- Aggregations for summaries
- Export functionality

## Running the Dashboard

1. Save the code as `dashboard.py`
2. Install requirements:
```bash
uv pip install streamlit pandas plotly
```

3. Run the app:
```bash
streamlit run dashboard.py
```

## Customization Ideas

- Add more filter options (price range, customer segments)
- Include time-based comparisons (YoY, MoM)
- Add forecasting visualizations
- Implement drill-down capabilities
- Add real-time data updates
- Include export to PDF/PowerPoint

## Best Practices

1. **Performance**: Cache data loading and expensive computations
2. **UX**: Provide clear labels and helpful tooltips
3. **Responsiveness**: Use `use_container_width=True` for charts
4. **Feedback**: Show loading states for slow operations
5. **Organization**: Group related content logically
6. **Accessibility**: Use clear colors and readable fonts

## Common Patterns

### Dynamic Filtering
```python
# Apply multiple filters
mask = (
    (df['date'] >= start_date) &
    (df['date'] <= end_date) &
    (df['category'].isin(selected_categories))
)
filtered_df = df[mask]
```

### Conditional Display
```python
if len(filtered_df) > 0:
    st.plotly_chart(fig)
else:
    st.warning("No data matches your filters")
```

### Responsive Metrics
```python
# Calculate delta from baseline
current = filtered_df['sales'].sum()
baseline = df['sales'].sum()
delta = ((current - baseline) / baseline * 100)
st.metric("Sales", f"${current:,.0f}", f"{delta:.1f}%")
```

## Next Steps

- Add authentication for multi-user dashboards
- Implement database connections for real data
- Add more advanced analytics (forecasting, anomaly detection)
- Create drill-down views for detailed analysis
- Export dashboard as PDF report

## Resources

- [Plotly Documentation](https://plotly.com/python/)
- [Streamlit Layout Guide](https://docs.streamlit.io/library/api-reference/layout)
- [Dashboard Design Best Practices](https://www.tableau.com/learn/articles/dashboard-design-principles)
