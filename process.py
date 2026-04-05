import pandas as pd
from azure.storage.blob import BlobServiceClient
import os, io

# ML imports
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# ===============================
# 1. CONNECT TO AZURE
# ===============================
conn_str = os.environ["AZURE_CONN_STR"]
client = BlobServiceClient.from_connection_string(conn_str)

# ===============================
# 2. LOAD DATA FROM BLOB
# ===============================
blob = client.get_blob_client("projectcontainerinput", "globalAirQuality.csv")
data = blob.download_blob().readall()
df = pd.read_csv(io.BytesIO(data))

# ===============================
# 3. PREPARE DATA
# ===============================
# Drop missing values (important for ML)
df = df.dropna()

# Features and target
X = df[["pm25", "temperature"]]
y = df["aqi"]

# ===============================
# 4. TRAIN MODELS
# ===============================

# ---- Linear Regression ----
lr = LinearRegression()
lr.fit(X, y)
y_pred_lr = lr.predict(X)

# ---- Decision Tree ----
dt = DecisionTreeRegressor(max_depth=5)
dt.fit(X, y)
y_pred_dt = dt.predict(X)

# ===============================
# 5. EVALUATION
# ===============================
mae_lr = mean_absolute_error(y, y_pred_lr)
r2_lr = r2_score(y, y_pred_lr)

mae_dt = mean_absolute_error(y, y_pred_dt)
r2_dt = r2_score(y, y_pred_dt)

print("=== MODEL PERFORMANCE ===")
print(f"Linear Regression → MAE: {mae_lr:.2f}, R2: {r2_lr:.2f}")
print(f"Decision Tree     → MAE: {mae_dt:.2f}, R2: {r2_dt:.2f}")

# ===============================
# 6. ADD PREDICTIONS
# ===============================
df["predicted_aqi_lr"] = y_pred_lr
df["predicted_aqi_dt"] = y_pred_dt

# ===============================
# 7. AGGREGATE RESULTS
# ===============================
result = df.groupby("country")[[
    "aqi",
    "predicted_aqi_lr",
    "predicted_aqi_dt"
]].mean().round(2)

result.columns = [
    "avg_actual_aqi",
    "avg_predicted_lr",
    "avg_predicted_dt"
]

# ===============================
# 8. SAVE RESULTS TO AZURE
# ===============================
out_blob = client.get_blob_client("projectcontaineroutput", "results.csv")
out_blob.upload_blob(result.to_csv(), overwrite=True)

print(f"\nDone. Processed {len(df)} rows, {result.shape[0]} countries.")
