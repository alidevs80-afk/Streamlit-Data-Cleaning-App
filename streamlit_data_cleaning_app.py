import streamlit as st
import os
import pandas as pd
import io
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Data Cleaning App")

# Get file extension
def get_file_extension(file):
    return os.path.splitext(file.name)[1].lower() if file else None

# Load data
def load_data(file):
    if file is None:
        return None

    ext = get_file_extension(file)

    try:
        if ext == ".csv":
            df = pd.read_csv(file)
        elif ext == ".json":
            df = pd.read_json(file)
        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(file)
        elif ext == ".parquet":
            df = pd.read_parquet(file)
        else:
            st.warning("Unsupported file type")
            return None

        st.success("Data loaded successfully!")
        return df

    except Exception as e:
        st.error(f"Error: {e}")
        return None


st.title("Mini Data Cleaning & Visualization WebApp")

uploaded_file = st.file_uploader(
    "Upload your dataset",
    type=["csv", "xlsx", "xls", "json", "parquet"]
)

df = load_data(uploaded_file)

# Initialize session state
if df is not None:
    if "original_df" not in st.session_state:
        st.session_state.original_df = df.copy()
    if "df" not in st.session_state:
        st.session_state.df = df.copy()

if "df" in st.session_state:
    df = st.session_state.df

    # Preview
    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    # Info
    st.subheader("Dataset Info")
    colA, colB = st.columns(2)
    colA.write(f"Shape: {df.shape}")
    colB.write(f"Columns: {list(df.columns)}")

    # Cleaning buttons
    st.subheader("Data Cleaning")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("Remove Nulls"):
            st.session_state.df = df.dropna()
            st.success("Null values removed")

    with col2:
        if st.button("Drop Duplicates"):
            st.session_state.df = df.drop_duplicates()
            st.success("Duplicates removed")

    with col3:
        if st.button("Fill Nulls"):
            st.session_state.df = df.fillna("N/A")
            st.success("Nulls filled")

    with col4:
        if st.button("Reset Data"):
            st.session_state.df = st.session_state.original_df.copy()
            st.success("Data reset")

    df = st.session_state.df

    # Detailed analysis
    with st.expander("Detailed Analysis"):
        if st.button("Dataset Info Detail"):
            buffer = io.StringIO()
            df.info(buf=buffer)
            st.text(buffer.getvalue())

        if st.button("Describe Dataset"):
            st.dataframe(df.describe())

        if st.button("Null Values Summary"):
            st.write(df.isnull().sum())

        if st.button("Data Types"):
            st.write(df.dtypes)

    # Visualization
    st.subheader("Data Visualization")

    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()

    if numeric_cols:
        col_choice = st.selectbox("Histogram Column", numeric_cols)

        fig, ax = plt.subplots()
        sns.histplot(df[col_choice], kde=True, ax=ax)
        st.pyplot(fig)
        plt.close(fig)

        st.write(f"Boxplot of {col_choice}")
        fig, ax = plt.subplots()
        sns.boxplot(x=df[col_choice], ax=ax)
        st.pyplot(fig)
        plt.close(fig)

    if len(numeric_cols) >= 2:
        x_axis = st.selectbox("X-axis", numeric_cols, index=0)
        y_axis = st.selectbox("Y-axis", numeric_cols, index=1)

        fig, ax = plt.subplots()
        sns.scatterplot(x=df[x_axis], y=df[y_axis], ax=ax)
        st.pyplot(fig)
        plt.close(fig)

    if st.checkbox("Show Correlation Heatmap"):
        if len(numeric_cols) > 1:
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.heatmap(df[numeric_cols].corr(), annot=True, cmap="coolwarm", ax=ax)
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.warning("Not enough numeric columns")

    if categorical_cols:
        cat_choice = st.selectbox("Categorical Column (Bar Chart)", categorical_cols)

        fig, ax = plt.subplots()
        df[cat_choice].value_counts().plot(kind="bar", ax=ax)
        st.pyplot(fig)
        plt.close(fig)

    if st.checkbox("Show Missing Values Heatmap"):
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(df.isnull(), cbar=False, cmap="viridis", ax=ax)
        st.pyplot(fig)
        plt.close(fig)

    if st.checkbox("Show Pairplot"):
        if len(numeric_cols) > 1:
            fig = sns.pairplot(df[numeric_cols])
            st.pyplot(fig)
            plt.close()
        else:
            st.warning("Not enough numeric columns")

    # Download cleaned dataset
    st.subheader("Download Cleaned Data")

    file_format = st.selectbox("Select format", ["CSV", "Excel", "JSON", "Parquet"])

    if file_format == "CSV":
        data = df.to_csv(index=False).encode("utf-8")
        file_name = "cleaned_data.csv"
        mime = "text/csv"

    elif file_format == "Excel":
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False)
        data = buffer.getvalue()
        file_name = "cleaned_data.xlsx"
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    elif file_format == "JSON":
        data = df.to_json(orient="records").encode("utf-8")
        file_name = "cleaned_data.json"
        mime = "application/json"

    elif file_format == "Parquet":
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False)
        data = buffer.getvalue()
        file_name = "cleaned_data.parquet"
        mime = "application/octet-stream"

    st.download_button(
        label=f"Download as {file_format}",
        data=data,
        file_name=file_name,
        mime=mime
    )

else:
    st.info("Please upload a dataset to begin.")
