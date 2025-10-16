import os
import pandas as pd
import numpy as np
import streamlit as st
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense
from tensorflow.keras.callbacks import EarlyStopping

# =========================
# File Paths
# =========================
MODEL_PATH = "salary_model.h5"
PREPROCESSOR_PATH = "salary_preprocessor.pkl"
DATA_PATH = "Churn_Modelling.csv"   # using same dataset for assignment

# =========================
# Load Dataset
# =========================
@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

# =========================
# Preprocessing
# =========================
def build_preprocessor(df):
    # Remove ID columns
    df = df.drop(columns=["RowNumber", "CustomerId", "Surname"])

    # Target variable for regression: EstimatedSalary
    y = df["EstimatedSalary"]
    X = df.drop(columns=["EstimatedSalary"])

    categorical_cols = X.select_dtypes(include=["object"]).columns.tolist()
    numeric_cols = X.select_dtypes(exclude=["object"]).columns.tolist()

    categorical_transformer = OneHotEncoder(drop="first", handle_unknown="ignore")
    numeric_transformer = StandardScaler()

    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", categorical_transformer, categorical_cols),
            ("numeric", numeric_transformer, numeric_cols)
        ]
    )

    return X, y, preprocessor

# =========================
# Model Creation
# =========================
def create_model(input_dim):
    model = Sequential()
    model.add(Dense(64, activation='relu', input_dim=input_dim))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(1))  # regression output (no activation)
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model

# =========================
# Train Model (1x) + 50 Tests, Early Stopping 10
# =========================
def train_and_save_best_model():
    df = load_data()
    X, y, preprocessor = build_preprocessor(df)

    X_processed = preprocessor.fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(
        X_processed, y, test_size=0.2, random_state=42
    )

    best_model = None
    best_loss = float('inf')

    for i in range(50):   # 50 training tests
        model = create_model(input_dim=X_train.shape[1])

        early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

        history = model.fit(
            X_train,
            y_train,
            validation_data=(X_test, y_test),
            epochs=100,
            batch_size=32,
            callbacks=[early_stop],
            verbose=0
        )

        final_loss = min(history.history['val_loss'])
        if final_loss < best_loss:
            best_loss = final_loss
            best_model = model

    # Save best model and preprocessor
    best_model.save(MODEL_PATH)
    joblib.dump(preprocessor, PREPROCESSOR_PATH)
    st.sidebar.success(f"Model trained 50 times. Best val_loss: {best_loss:.4f}")

# =========================
# Load Model + Preprocessor
# =========================
def load_model_and_preprocessor():
    model = load_model(MODEL_PATH)
    preprocessor = joblib.load(PREPROCESSOR_PATH)
    return model, preprocessor

# =========================
# Streamlit UI
# =========================
st.set_page_config(page_title="Salary Regression using ANN", layout="wide")
st.title("Salary Regression Prediction (ANN)")

# Train automatically on first run
if not (os.path.exists(MODEL_PATH) and os.path.exists(PREPROCESSOR_PATH)):
    with st.spinner("Training salary regression model..."):
        train_and_save_best_model()

# Load model and preprocessor
model, preprocessor = load_model_and_preprocessor()

# Load dataset for sliders
df = load_data()
df = df.drop(columns=["RowNumber", "CustomerId", "Surname"])
X = df.drop(columns=["EstimatedSalary"])

st.subheader("Enter Customer Details for Salary Prediction")

# =========================
# 3 COLUMN LAYOUT
# =========================
col1, col2, col3 = st.columns(3)
input_data = {}

# -------------------------
# COLUMN 1
# -------------------------
gender_val = col1.selectbox("Gender", options=df["Gender"].unique())
input_data["Gender"] = gender_val

age_val = col1.slider("Age", min_value=15, max_value=80, value=int(X["Age"].mean()))
input_data["Age"] = age_val

has_card = col1.selectbox("Has Credit Card", options=["Yes", "No"])
input_data["HasCrCard"] = 1 if has_card == "Yes" else 0

balance_val = col1.number_input(
    "Balance",
    min_value=float(X["Balance"].min()),
    max_value=float(X["Balance"].max()),
    value=float(X["Balance"].mean())
)
input_data["Balance"] = balance_val

# -------------------------
# COLUMN 2
# -------------------------
geo_val = col2.selectbox("Geography", options=df["Geography"].unique())
input_data["Geography"] = geo_val

tenure_val = col2.slider("Tenure (Years)", min_value=0, max_value=35, value=int(X["Tenure"].mean()))
input_data["Tenure"] = tenure_val

active_val = col2.selectbox("Is Active Member", options=["Yes", "No"])
input_data["IsActiveMember"] = 1 if active_val == "Yes" else 0

# -------------------------
# COLUMN 3
# -------------------------
num_products_val = col3.number_input(
    "Number of Products",
    min_value=int(X["NumOfProducts"].min()),
    max_value=int(X["NumOfProducts"].max()),
    value=int(X["NumOfProducts"].mean()),
    step=1
)
input_data["NumOfProducts"] = int(num_products_val)

credit_min = int(X["CreditScore"].min())
credit_max = int(X["CreditScore"].max())
credit_val = col3.slider(
    "Credit Score",
    min_value=credit_min,
    max_value=credit_max,
    value=int(X["CreditScore"].mean())
)
input_data["CreditScore"] = credit_val

exited_val = col3.selectbox("Exited", options=["Not known", "Yes", "No"])
if exited_val == "Yes":
    input_data["Exited"] = 1
elif exited_val == "No":
    input_data["Exited"] = 0
else:
    input_data["Exited"] = 0  # default for 'Not known'

# =========================
# PREDICTION
# =========================
if st.button("Predict Salary"):
    input_df = pd.DataFrame([input_data])

    # ✅ Match preprocessor columns (avoid missing Exited error)
    expected_cols = list(preprocessor.feature_names_in_)
    input_df = input_df.reindex(columns=expected_cols, fill_value=0)

    input_processed = preprocessor.transform(input_df)
    prediction = model.predict(input_processed)[0][0]
    st.write(f"### Predicted Salary: {prediction:,.2f}")
