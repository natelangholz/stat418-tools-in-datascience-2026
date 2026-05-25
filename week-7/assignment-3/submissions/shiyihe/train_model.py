import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

df = pd.read_csv("mtcars.csv")

# use median mpg to create a simple binary target
median_mpg = df["mpg"].median()
df["high_mpg"] = (df["mpg"] > median_mpg).astype(int)

features = ["wt", "hp", "cyl"]

X = df[features]
y = df["high_mpg"]

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

model_info = {
    "model": model,
    "features": features,
    "model_version": "v1.0",
    "target": "high_mpg"
}

joblib.dump(model_info, "model.pkl")

print("saved model.pkl")
print("features:", features)
print("target: high_mpg")
