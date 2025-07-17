# task_duration_model.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ========== Step 1: Load and preprocess dataset ==========

print("🔄 Loading dataset...")
df = pd.read_csv("task_time_estimation_dataset.csv")

# Optional: use a smaller sample for quick testing
# df = df.sample(10000, random_state=42)

# Drop unused columns
df = df.drop(columns=["Task ID", "Timestamp", "Machine ID"])

# Separate features and target
X = df.drop(columns=["Estimated Duration (min)"])
y = df["Estimated Duration (min)"]

# Identify column types
numerical_cols = ["Temp (°C)"]
categorical_cols = [col for col in X.columns if col not in numerical_cols]

# ========== Step 2: Define preprocessing pipelines ==========

numerical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="mean")),
    ("scaler", StandardScaler())
])

categorical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer([
    ("num", numerical_pipeline, numerical_cols),
    ("cat", categorical_pipeline, categorical_cols)
])

# ========== Step 3: Create full ML pipeline ==========

pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("model", RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1))
])

# ========== Step 4: Train/Test Split ==========

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ========== Step 5: Train Model ==========

print("🧠 Training model...")
start = time.time()
pipeline.fit(X_train, y_train)
print(f"✅ Training completed in {time.time() - start:.2f} seconds.")

# ========== Step 6: Evaluate Model ==========

print("📊 Evaluating model...")
y_pred = pipeline.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print(f"✅ MAE: {mae:.2f}")
print(f"✅ RMSE: {rmse:.2f}")
print(f"✅ R² Score: {r2:.4f}")

# ========== Step 7: Feature Importance Plot ==========

print("📈 Plotting top 10 feature importances...")

# Extract feature names after one-hot encoding
ohe = pipeline.named_steps["preprocessor"].named_transformers_["cat"].named_steps["encoder"]
encoded_cat_features = ohe.get_feature_names_out(categorical_cols)
all_features = numerical_cols + list(encoded_cat_features)

# Get importance values
importances = pipeline.named_steps["model"].feature_importances_
feature_importance_series = pd.Series(importances, index=all_features)

# Plot
top_n = 10
feature_importance_series.nlargest(top_n).plot(kind="barh")
plt.title(f"Top {top_n} Feature Importances")
plt.xlabel("Importance Score")
plt.tight_layout()
plt.show()
