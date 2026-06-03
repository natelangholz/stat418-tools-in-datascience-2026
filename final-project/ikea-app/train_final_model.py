import joblib
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix, ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

df = pd.read_csv("ikea_model_dataset.csv")

features = [
    "category",
    "price",
    "rating",
    "name_length",
    "page_text_length",
]

target = "high_interest"

X = df[features]
y = df[target]

categorical_features = ["category"]
numeric_features = [
    "price",
    "rating",
    "name_length",
    "page_text_length",
]

preprocess = ColumnTransformer(
    transformers=[
        ("category", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ("numeric", StandardScaler(), numeric_features),
    ]
)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y,
)

models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Random Forest": RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        max_depth=6,
    ),
}

results = []

for model_name, model in models.items():
    pipeline = Pipeline(
        steps=[
            ("preprocess", preprocess),
            ("model", model),
        ]
    )

    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)

    results.append({
        "model": model_name,
        "accuracy": accuracy_score(y_test, preds),
        "precision": precision_score(y_test, preds),
        "recall": recall_score(y_test, preds),
        "f1": f1_score(y_test, preds),
    })

    if model_name == "Random Forest":
        joblib.dump(pipeline, "ikea_interest_model.pkl")

results_df = pd.DataFrame(results)
results_df.to_csv("model_results.csv", index=False)

print(results_df)

plt.figure(figsize=(7, 4))
plt.bar(results_df["model"], results_df["f1"])
plt.title("Model Comparison by F1 Score")
plt.ylabel("F1 Score")
plt.ylim(0, 1)
plt.tight_layout()
plt.savefig("model_comparison_f1.png")
plt.close()

rf_pipeline = joblib.load("ikea_interest_model.pkl")
rf_model = rf_pipeline.named_steps["model"]
preprocessor = rf_pipeline.named_steps["preprocess"]

category_features = list(
    preprocessor.named_transformers_["category"].get_feature_names_out(["category"])
)

feature_names = category_features + numeric_features

importance_df = pd.DataFrame({
    "feature": feature_names,
    "importance": rf_model.feature_importances_,
}).sort_values("importance", ascending=False).head(12)

importance_df.to_csv("feature_importance.csv", index=False)

plt.figure(figsize=(8, 5))
plt.barh(importance_df["feature"][::-1], importance_df["importance"][::-1])
plt.title("Top Random Forest Feature Importances")
plt.xlabel("Importance")
plt.tight_layout()
plt.savefig("feature_importance.png")
plt.close()
# confusion matrix for Random Forest
rf_preds = rf_pipeline.predict(X_test)
cm = confusion_matrix(y_test, rf_preds)

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=["Low Interest", "High Interest"]
)

disp.plot()
plt.title("Random Forest Confusion Matrix")
plt.tight_layout()
plt.savefig("confusion_matrix.png")
plt.close()

print("saved model, results, and charts")
