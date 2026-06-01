# Streamlit Basics

## Overview

This example covers the fundamental concepts of Streamlit - the framework we'll use to build interactive data applications. Streamlit lets you create web apps using pure Python, with no frontend development required.

## What is Streamlit?

Streamlit is an open-source Python framework for building data applications. It's designed specifically for data scientists and machine learning engineers who want to create interactive apps without learning web development.

**Key Philosophy**: Your app is just a Python script that runs from top to bottom every time something changes.

## Installation

```bash
uv pip install streamlit
```

## Running a Streamlit App

```bash
streamlit run app.py
```

This starts a local web server and opens your app in a browser.

## Basic Components

### 1. Text Elements

```python
import streamlit as st

# Title
st.title("My Data App")

# Header
st.header("This is a header")

# Subheader
st.subheader("This is a subheader")

# Text
st.text("This is plain text")

# Markdown
st.markdown("**Bold** and *italic* text")

# Code
st.code("print('Hello, World!')", language="python")

# LaTeX
st.latex(r"\sum_{i=1}^{n} x_i")
```

### 2. Data Display

```python
import pandas as pd
import numpy as np

# DataFrame
df = pd.DataFrame({
    'Column A': [1, 2, 3, 4],
    'Column B': [10, 20, 30, 40]
})

st.dataframe(df)  # Interactive table
st.table(df)      # Static table

# Metrics
st.metric(label="Temperature", value="70 °F", delta="1.2 °F")

# JSON
st.json({'foo': 'bar', 'baz': [1, 2, 3]})
```

### 3. Charts and Visualizations

```python
# Line chart
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['a', 'b', 'c']
)
st.line_chart(chart_data)

# Area chart
st.area_chart(chart_data)

# Bar chart
st.bar_chart(chart_data)

# Map (requires lat/lon columns)
map_data = pd.DataFrame(
    np.random.randn(100, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon']
)
st.map(map_data)
```

### 4. Input Widgets

```python
# Text input
name = st.text_input("Enter your name")

# Number input
age = st.number_input("Enter your age", min_value=0, max_value=120)

# Slider
value = st.slider("Select a value", 0, 100, 50)

# Select box
option = st.selectbox(
    "Choose an option",
    ["Option 1", "Option 2", "Option 3"]
)

# Multi-select
options = st.multiselect(
    "Choose multiple options",
    ["A", "B", "C", "D"]
)

# Checkbox
agree = st.checkbox("I agree")

# Radio buttons
choice = st.radio("Pick one", ["Option A", "Option B"])

# Date input
import datetime
date = st.date_input("Pick a date", datetime.date.today())

# Time input
time = st.time_input("Pick a time", datetime.time(8, 45))

# File uploader
uploaded_file = st.file_uploader("Choose a file")

# Color picker
color = st.color_picker("Pick a color", "#00f900")
```

### 5. Buttons and Forms

```python
# Button
if st.button("Click me"):
    st.write("Button clicked!")

# Form (groups inputs together)
with st.form("my_form"):
    name = st.text_input("Name")
    age = st.number_input("Age")
    submitted = st.form_submit_button("Submit")
    
    if submitted:
        st.write(f"Hello {name}, you are {age} years old")

# Download button
data = "Hello, World!"
st.download_button(
    label="Download data",
    data=data,
    file_name="data.txt",
    mime="text/plain"
)
```

## Layout and Containers

### Columns

```python
col1, col2, col3 = st.columns(3)

with col1:
    st.header("Column 1")
    st.write("Content for column 1")

with col2:
    st.header("Column 2")
    st.write("Content for column 2")

with col3:
    st.header("Column 3")
    st.write("Content for column 3")
```

### Expander

```python
with st.expander("Click to expand"):
    st.write("Hidden content that appears when expanded")
    st.image("https://example.com/image.jpg")
```

### Sidebar

```python
# Add widgets to sidebar
st.sidebar.title("Sidebar")
option = st.sidebar.selectbox("Choose", ["A", "B", "C"])
slider_val = st.sidebar.slider("Value", 0, 100)
```

### Tabs

```python
tab1, tab2, tab3 = st.tabs(["Tab 1", "Tab 2", "Tab 3"])

with tab1:
    st.write("Content for tab 1")

with tab2:
    st.write("Content for tab 2")

with tab3:
    st.write("Content for tab 3")
```

### Container

```python
container = st.container()
container.write("This is inside a container")

# You can add to it later
container.write("This is also in the container")
```

## Session State

Session state lets you store variables across reruns:

```python
# Initialize session state
if 'count' not in st.session_state:
    st.session_state.count = 0

# Increment counter
if st.button("Increment"):
    st.session_state.count += 1

st.write(f"Count: {st.session_state.count}")
```

## Caching

Caching prevents expensive computations from running on every rerun:

```python
@st.cache_data  # For data (DataFrames, lists, etc.)
def load_data():
    # Expensive data loading
    df = pd.read_csv("large_file.csv")
    return df

@st.cache_resource  # For resources (models, connections, etc.)
def load_model():
    # Expensive model loading
    model = load_my_ml_model()
    return model

# These only run once, then cache the result
df = load_data()
model = load_model()
```

## Progress and Status

```python
import time

# Progress bar
progress_bar = st.progress(0)
for i in range(100):
    time.sleep(0.01)
    progress_bar.progress(i + 1)

# Spinner
with st.spinner("Loading..."):
    time.sleep(2)
st.success("Done!")

# Status messages
st.success("Success!")
st.info("Info message")
st.warning("Warning!")
st.error("Error!")
st.exception(RuntimeError("This is an exception"))
```

## Complete Example App

```python
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Page config
st.set_page_config(
    page_title="My Data App",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 Interactive Data Explorer")

# Sidebar
st.sidebar.header("Settings")
num_points = st.sidebar.slider("Number of points", 10, 1000, 100)
chart_type = st.sidebar.selectbox("Chart type", ["Scatter", "Line", "Bar"])

# Generate data
@st.cache_data
def generate_data(n):
    return pd.DataFrame({
        'x': np.random.randn(n),
        'y': np.random.randn(n),
        'category': np.random.choice(['A', 'B', 'C'], n)
    })

df = generate_data(num_points)

# Display data
st.subheader("Data Preview")
st.dataframe(df.head())

# Statistics
col1, col2, col3 = st.columns(3)
col1.metric("Mean X", f"{df['x'].mean():.2f}")
col2.metric("Mean Y", f"{df['y'].mean():.2f}")
col3.metric("Total Points", len(df))

# Chart
st.subheader(f"{chart_type} Chart")
if chart_type == "Scatter":
    fig = px.scatter(df, x='x', y='y', color='category')
elif chart_type == "Line":
    fig = px.line(df.sort_values('x'), x='x', y='y', color='category')
else:
    fig = px.bar(df.groupby('category').size().reset_index(name='count'),
                 x='category', y='count')

st.plotly_chart(fig, use_container_width=True)

# Download data
csv = df.to_csv(index=False)
st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name="data.csv",
    mime="text/csv"
)
```

## Best Practices

1. **Use caching**: Cache expensive operations with `@st.cache_data` or `@st.cache_resource`
2. **Organize with containers**: Use columns, expanders, and tabs to organize content
3. **Provide feedback**: Use spinners and progress bars for long operations
4. **Handle errors**: Use try/except and display user-friendly error messages
5. **Keep it simple**: Don't overcomplicate the UI - simple is better
6. **Test locally**: Always test your app locally before deploying
7. **Use session state wisely**: Only store what you need between reruns

## Common Patterns

### Loading Data

```python
@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)

uploaded_file = st.file_uploader("Upload CSV")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.dataframe(df)
```

### Making Predictions

```python
@st.cache_resource
def load_model():
    return joblib.load('model.pkl')

model = load_model()

# Get user input
feature1 = st.number_input("Feature 1")
feature2 = st.number_input("Feature 2")

if st.button("Predict"):
    prediction = model.predict([[feature1, feature2]])
    st.write(f"Prediction: {prediction[0]}")
```

### API Integration

```python
import requests

url = st.text_input("API URL")
if st.button("Fetch Data"):
    with st.spinner("Fetching..."):
        response = requests.get(url)
        if response.status_code == 200:
            st.json(response.json())
        else:
            st.error(f"Error: {response.status_code}")
```

## Next Steps

- Explore the [interactive-dashboard](../interactive-dashboard/) example for a complete dashboard
- Learn about [ml-app-deployment](../ml-app-deployment/) for deploying ML models
- Check out [api-integration](../api-integration/) for connecting to APIs

## Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Gallery](https://streamlit.io/gallery)
- [Streamlit Cheat Sheet](https://docs.streamlit.io/library/cheatsheet)
- [Streamlit Components](https://streamlit.io/components)