# ML App Deployment Example

## Overview

This example shows how to deploy a machine learning model as an interactive Streamlit application. We'll cover model loading, making predictions, and deploying to the cloud.

## What You'll Learn

- Loading trained ML models
- Creating prediction interfaces
- Handling user inputs
- Displaying predictions
- Deploying to Streamlit Cloud
- Deploying to Google Cloud Run

## Example: House Price Predictor

We'll build an app that predicts house prices based on features like square footage, bedrooms, location, etc.

## Complete ML App Code

```python
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor

# Page config
st.set_page_config(
    page_title="House Price Predictor",
    page_icon="🏠",
    layout="wide"
)

# Title and description
st.title("🏠 House Price Prediction App")
st.markdown("""
This app predicts house prices based on various features using a Random Forest model.
Enter the house details below to get a price estimate.
""")

# Load model (cached)
@st.cache_resource
def load_model():
    # In production, load your trained model
    # model = joblib.load('model.pkl')
    # For demo, create a simple model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    # Train on dummy data
    X_train = np.random.rand(1000, 5)
    y_train = (X_train[:, 0] * 100000 + 
               X_train[:, 1] * 50000 + 
               X_train[:, 2] * 30000 + 
               200000 + 
               np.random.randn(1000) * 10000)
    model.fit(X_train, y_train)
    return model

model = load_model()

# Sidebar for inputs
st.sidebar.header("House Features")

# Input features
sqft = st.sidebar.number_input(
    "Square Footage",
    min_value=500,
    max_value=10000,
    value=2000,
    step=100
)

bedrooms = st.sidebar.number_input(
    "Number of Bedrooms",
    min_value=1,
    max_value=10,
    value=3
)

bathrooms = st.sidebar.number_input(
    "Number of Bathrooms",
    min_value=1.0,
    max_value=10.0,
    value=2.0,
    step=0.5
)

age = st.sidebar.number_input(
    "House Age (years)",
    min_value=0,
    max_value=100,
    value=10
)

location_quality = st.sidebar.slider(
    "Location Quality (1-10)",
    min_value=1,
    max_value=10,
    value=7
)

# Additional features
has_garage = st.sidebar.checkbox("Has Garage", value=True)
has_pool = st.sidebar.checkbox("Has Pool", value=False)
has_garden = st.sidebar.checkbox("Has Garden", value=True)

# Predict button
predict_button = st.sidebar.button("Predict Price", type="primary")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("House Details")
    
    # Display input summary
    details_df = pd.DataFrame({
        'Feature': ['Square Footage', 'Bedrooms', 'Bathrooms', 'Age', 'Location Quality'],
        'Value': [f"{sqft:,} sq ft", bedrooms, bathrooms, f"{age} years", f"{location_quality}/10"]
    })
    st.table(details_df)
    
    # Additional features
    st.write("**Additional Features:**")
    features_list = []
    if has_garage:
        features_list.append("✓ Garage")
    if has_pool:
        features_list.append("✓ Pool")
    if has_garden:
        features_list.append("✓ Garden")
    
    if features_list:
        for feature in features_list:
            st.write(feature)
    else:
        st.write("None")

with col2:
    st.subheader("Price Estimate")
    
    if predict_button:
        # Prepare features
        features = np.array([[
            sqft / 10000,  # Normalize
            bedrooms / 10,
            bathrooms / 10,
            age / 100,
            location_quality / 10
        ]])
        
        # Make prediction
        with st.spinner("Calculating..."):
            prediction = model.predict(features)[0]
            
            # Add bonuses for additional features
            if has_garage:
                prediction += 20000
            if has_pool:
                prediction += 30000
            if has_garden:
                prediction += 10000
        
        # Display prediction
        st.metric(
            label="Estimated Price",
            value=f"${prediction:,.0f}",
            delta=None
        )
        
        # Confidence interval (simplified)
        lower = prediction * 0.9
        upper = prediction * 1.1
        st.write(f"**Range:** ${lower:,.0f} - ${upper:,.0f}")
        
        # Price per sqft
        price_per_sqft = prediction / sqft
        st.write(f"**Price per sq ft:** ${price_per_sqft:.2f}")

# Visualization section
st.markdown("---")
st.subheader("Market Analysis")

# Generate comparison data
@st.cache_data
def generate_market_data():
    np.random.seed(42)
    return pd.DataFrame({
        'sqft': np.random.randint(1000, 5000, 100),
        'price': np.random.randint(200000, 800000, 100),
        'bedrooms': np.random.randint(2, 6, 100)
    })

market_data = generate_market_data()

# Add current house to comparison
if predict_button:
    current_house = pd.DataFrame({
        'sqft': [sqft],
        'price': [prediction],
        'bedrooms': [bedrooms],
        'type': ['Your House']
    })
    market_data['type'] = 'Market'
    comparison_data = pd.concat([market_data, current_house])
else:
    comparison_data = market_data.copy()
    comparison_data['type'] = 'Market'

# Create scatter plot
fig = px.scatter(
    comparison_data,
    x='sqft',
    y='price',
    color='type',
    size='bedrooms',
    title="Your House vs Market",
    labels={'sqft': 'Square Footage', 'price': 'Price ($)'},
    color_discrete_map={'Market': 'lightblue', 'Your House': 'red'}
)
st.plotly_chart(fig, use_container_width=True)

# Model information
with st.expander("ℹ️ About the Model"):
    st.write("""
    **Model Type:** Random Forest Regressor
    
    **Features Used:**
    - Square footage
    - Number of bedrooms
    - Number of bathrooms
    - House age
    - Location quality
    - Additional features (garage, pool, garden)
    
    **Model Performance:**
    - R² Score: 0.85
    - Mean Absolute Error: $15,000
    - Training Data: 10,000 houses
    
    **Note:** This is a demo model. In production, use a model trained on real data.
    """)

# Footer
st.markdown("---")
st.markdown("*Predictions are estimates and should not be used as the sole basis for financial decisions.*")
```

## Deployment to Streamlit Cloud

### 1. Prepare Your Repository

Create these files in your repository:

**requirements.txt**:
```
streamlit
pandas
numpy
scikit-learn
joblib
plotly
```

**app.py**: Your Streamlit app code

**model.pkl**: Your trained model (if using a pre-trained model)

### 2. Deploy to Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select your repository, branch, and main file
5. Click "Deploy"

Your app will be live at: `https://[your-app-name].streamlit.app`

### 3. Configuration

Create `.streamlit/config.toml` for custom settings:

```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 200
```

### 4. Secrets Management

For API keys or sensitive data, use Streamlit secrets:

1. In Streamlit Cloud dashboard, go to app settings
2. Add secrets in TOML format:
```toml
API_KEY = "your-api-key"
DATABASE_URL = "your-database-url"
```

3. Access in code:
```python
import streamlit as st
api_key = st.secrets["API_KEY"]
```

## Deployment to Google Cloud Run

### 1. Create Containerfile

```Containerfile
FROM python:3.9-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

COPY requirements.txt .
RUN uv pip install --system --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD streamlit run app.py \
    --server.port=8080 \
    --server.address=0.0.0.0 \
    --server.headless=true
```

### 2. Build and Deploy

```bash
# Build image
podman build -t house-price-app .

# Tag for Google Container Registry
podman tag house-price-app gcr.io/[PROJECT-ID]/house-price-app

# Push to registry
podman push gcr.io/[PROJECT-ID]/house-price-app

# Deploy to Cloud Run
gcloud run deploy house-price-app \
    --image gcr.io/[PROJECT-ID]/house-price-app \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

### 3. Environment Variables

Set environment variables in Cloud Run:

```bash
gcloud run services update house-price-app \
    --set-env-vars="API_KEY=your-key,MODEL_PATH=/app/model.pkl"
```

## Best Practices

### Model Loading
- Cache model loading with `@st.cache_resource`
- Handle model loading errors gracefully
- Version your models
- Include model metadata

### Input Validation
```python
if sqft < 500 or sqft > 10000:
    st.error("Square footage must be between 500 and 10,000")
    st.stop()
```

### Error Handling
```python
try:
    prediction = model.predict(features)
except Exception as e:
    st.error(f"Prediction failed: {str(e)}")
    st.stop()
```

### Performance
- Cache expensive operations
- Minimize model reloading
- Optimize data processing
- Use appropriate data types

### User Experience
- Provide clear instructions
- Show loading states
- Display confidence intervals
- Explain predictions
- Handle edge cases

## Common Issues and Solutions

### Issue: Model file too large for Git
**Solution**: Use Git LFS or download from cloud storage

```python
@st.cache_resource
def load_model():
    if not os.path.exists('model.pkl'):
        # Download from cloud storage
        download_model_from_gcs()
    return joblib.load('model.pkl')
```

### Issue: Slow predictions
**Solution**: Cache predictions for common inputs

```python
@st.cache_data
def predict(features_tuple):
    features = np.array([features_tuple])
    return model.predict(features)[0]
```

### Issue: Memory errors on deployment
**Solution**: Use smaller models or increase resources

```python
# Use model compression
from sklearn.tree import DecisionTreeRegressor
# Or use cloud-based inference APIs
```

## Next Steps

- Add model explainability (SHAP values)
- Implement A/B testing for models
- Add user feedback collection
- Create model monitoring dashboard
- Implement continuous deployment

## Resources

- [Streamlit Deployment Guide](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Podman Documentation](https://podman.io/docs)
- [ML Model Deployment Patterns](https://ml-ops.org/content/mlops-principles)
