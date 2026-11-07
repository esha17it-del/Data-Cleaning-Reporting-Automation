
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Data Cleaning Automation",
    page_icon="🧹",
    layout="wide"
)

st.title("🧹 Data Cleaning & Reporting Automation")
st.write("Automatically clean datasets and generate data quality reports.")

# Upload file
uploaded_file = st.file_uploader(
    "Upload CSV or Excel File",
    type=["csv", "xlsx"]
)

# Load data
if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Unable to read file: {e}")
        st.stop()
else:
    df = pd.read_csv("sample_data.csv")

if df.empty:
    st.error("The uploaded dataset is empty.")
    st.stop()

# Create original copy
original_df = df.copy()

st.subheader("1. Original Dataset")
st.dataframe(original_df, use_container_width=True)

# Original data quality
missing_before = int(original_df.isnull().sum().sum())
duplicates_before = int(original_df.duplicated().sum())

st.subheader("2. Data Quality Overview")

c1, c2, c3 = st.columns(3)

c1.metric("Total Rows", len(original_df))
c2.metric("Missing Values", missing_before)
c3.metric("Duplicate Rows", duplicates_before)

# Cleaning options
st.subheader("3. Data Cleaning Options")

missing_method = st.selectbox(
    "Handle missing values",
    [
        "Fill with Mean/Mode",
        "Fill with Zero",
        "Drop rows with missing values"
    ]
)

remove_duplicates = st.checkbox(
    "Remove duplicate rows",
    value=True
)

clean_text = st.checkbox(
    "Remove extra spaces and standardize text",
    value=True
)

# Clean data button
if st.button("🧹 Clean My Data", type="primary"):

    cleaned_df = original_df.copy()

    # Standardize text columns
    if clean_text:
        for col in cleaned_df.select_dtypes(include=["object"]).columns:
            cleaned_df[col] = cleaned_df[col].apply(
                lambda x: x.strip() if isinstance(x, str) else x
            )

            cleaned_df[col] = cleaned_df[col].apply(
                lambda x: x.title() if isinstance(x, str) else x
            )

    # Convert blank cells into missing values
    cleaned_df = cleaned_df.replace(
        r"^\s*$", np.nan, regex=True
    )

    # Handle missing values
    if missing_method == "Fill with Mean/Mode":
        for col in cleaned_df.columns:
            if cleaned_df[col].isnull().any():
                if pd.api.types.is_numeric_dtype(cleaned_df[col]):
                    value = cleaned_df[col].mean()
                else:
                    mode = cleaned_df[col].mode()
                    value = mode.iloc[0] if not mode.empty else "Unknown"

                cleaned_df[col] = cleaned_df[col].fillna(value)

    elif missing_method == "Fill with Zero":
        cleaned_df = cleaned_df.fillna(0)

    elif missing_method == "Drop rows with missing values":
        cleaned_df = cleaned_df.dropna()

    # Remove duplicate rows
    if remove_duplicates:
        cleaned_df = cleaned_df.drop_duplicates()

    # Store cleaned data
    st.session_state["cleaned_df"] = cleaned_df

# Show results
if "cleaned_df" in st.session_state:

    result = st.session_state["cleaned_df"]

    st.subheader("4. Cleaned Dataset")
    st.dataframe(result, use_container_width=True)

    # Cleaning report
    st.subheader("5. Before and After Report")

    missing_after = int(result.isnull().sum().sum())
    duplicates_after = int(result.duplicated().sum())

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Rows Remaining",
        len(result),
        delta=len(result) - len(original_df)
    )

    col2.metric(
        "Missing Values",
        missing_after,
        delta=missing_after - missing_before
    )

    col3.metric(
        "Duplicate Rows",
        duplicates_after,
        delta=duplicates_after - duplicates_before
    )

    # Missing value chart
    st.subheader("6. Missing Values Analysis")

    fig, ax = plt.subplots(figsize=(9, 4))

    values = [
        original_df.isnull().sum().sum(),
        result.isnull().sum().sum()
    ]

    ax.bar(
        ["Before Cleaning", "After Cleaning"],
        values
    )

    ax.set_ylabel("Missing Values")
    ax.set_title("Data Quality Comparison")

    st.pyplot(fig)
    plt.close(fig)

    # Download CSV
    st.subheader("7. Download Cleaned Report")

    csv_data = result.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Download Cleaned CSV",
        data=csv_data,
        file_name="cleaned_data.csv",
        mime="text/csv"
    )

    # Download Excel
    import io

    excel_buffer = io.BytesIO()

    with pd.ExcelWriter(
        excel_buffer,
        engine="openpyxl"
    ) as writer:
        result.to_excel(
            writer,
            index=False,
            sheet_name="Cleaned Data"
        )

    st.download_button(
        "⬇️ Download Cleaned Excel",
        data=excel_buffer.getvalue(),
        file_name="cleaned_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.success("Data cleaning and reporting completed successfully!")
