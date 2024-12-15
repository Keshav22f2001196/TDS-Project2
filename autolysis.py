# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pandas",
#     "seaborn",
#     "matplotlib",
#     "requests",
#     "python-dotenv",
#     "scikit-learn",
#     "tenacity",
#     "chardet",
# ]
# ///

import os
import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import requests
import numpy as np
from dotenv import load_dotenv
from sklearn.impute import SimpleImputer
from tenacity import retry, stop_after_attempt, wait_fixed
import chardet
import base64

# Load environment variables
load_dotenv()
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")
if not AIPROXY_TOKEN:
    print("Error: AIPROXY_TOKEN not set.")
    sys.exit(1)

HEADERS = {"Authorization": f"Bearer {AIPROXY_TOKEN}"}
LLM_URL = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def call_llm(prompt, images=None):
    """Call the LLM API for text or image analysis."""
    payload = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "max_tokens": 1000}
    if images:
        payload["messages"].append({"role": "user", "content": [{"type": "image_url", "image_url": {"url": images}}]})
    response = requests.post(LLM_URL, headers=HEADERS, json=payload, timeout=60)
    response.raise_for_status()
    return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")

def detect_encoding(file_path):
    """Detect file encoding dynamically."""
    with open(file_path, "rb") as f:
        result = chardet.detect(f.read())
    return result.get("encoding", "utf-8")

def load_data(file_path):
    """Load and clean data with robust error handling."""
    try:
        # Detect encoding and load data
        encoding = detect_encoding(file_path)
        print(f"Detected encoding: {encoding}")
        data = pd.read_csv(file_path, encoding=encoding)

        # Replace infinite or excessively large values
        for col in data.columns:
            if np.issubdtype(data[col].dtype, np.number):
                # Convert invalid numbers to NaN
                data[col] = pd.to_numeric(data[col], errors="coerce")
                # Cap extremely large values
                upper_limit = 1e9  # Adjust as needed
                data[col] = data[col].apply(lambda x: np.nan if abs(x) > upper_limit else x)

        # Replace inf and -inf with NaN
        data.replace([np.inf, -np.inf], np.nan, inplace=True)

        # Drop columns with no valid values
        data.dropna(axis=1, how="all", inplace=True)

        # Handle missing values dynamically
        for col in data.columns:
            if data[col].isnull().any():
                strategy = "mean" if np.issubdtype(data[col].dtype, np.number) else "most_frequent"
                imputer = SimpleImputer(strategy=strategy)
                try:
                    data[col] = imputer.fit_transform(data[[col]]).ravel()
                except Exception as e:
                    print(f"Skipping imputation for {col}: {e}")

        print("Data loaded and cleaned successfully.")
        return data

    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)


def generate_visualizations(data, output_dir):
    """Generate meaningful visualizations."""
    os.makedirs(output_dir, exist_ok=True)

    numeric_data = data.select_dtypes(include=[np.number])
    categorical_data = data.select_dtypes(include=["object"])

    # Correlation Heatmap
    if numeric_data.shape[1] > 1:
        plt.figure(figsize=(6, 6))
        sns.heatmap(numeric_data.corr(), annot=True, cmap="coolwarm")
        plt.title("Correlation Heatmap")
        heatmap_path = os.path.join(output_dir, "correlation_heatmap.png")
        plt.savefig(heatmap_path)
        plt.close()

    # Generate one relevant chart (numeric or categorical)
    if not numeric_data.empty:
        plt.figure(figsize=(6, 4))
        sns.histplot(numeric_data.iloc[:, 0], bins=20, kde=True)
        plt.title(f"Distribution of {numeric_data.columns[0]}")
        numeric_path = os.path.join(output_dir, "numeric_distribution.png")
        plt.savefig(numeric_path)
        plt.close()
    elif not categorical_data.empty:
        plt.figure(figsize=(6, 4))
        data[categorical_data.columns[0]].value_counts().head(5).plot(kind="bar")
        plt.title(f"Top Categories in {categorical_data.columns[0]}")
        category_path = os.path.join(output_dir, "top_categories.png")
        plt.savefig(category_path)
        plt.close()

    return [heatmap_path, numeric_path if 'numeric_path' in locals() else category_path]

import base64

def generate_readme(data_summary, insights, image_paths, output_dir):
    """Generate a README.md file with results."""
    try:
        # Encode images for LLM vision capability
        image_base64 = []
        for path in image_paths:
            with open(path, "rb") as img_file:
                encoded_image = base64.b64encode(img_file.read()).decode("utf-8")
                image_base64.append(f"data:image/png;base64,{encoded_image}")

        # Call LLM for summary with multiple images
        llm_prompt = f"""
        Write an engaging analysis report using the following:
        1. Data Summary: {data_summary}
        2. Insights: {insights}
        3. PNG Images: Visualizations included for better insights.

        Structure:
        - The data you received, briefly.
        - The analysis you carried out.
        - The insights you discovered.
        - The implications of your findings (i.e., what to do with the insights).

        Make it engaging and interesting, with a clear narrative and actionable outcomes.
        Highlight key findings from visualizations.
        """
        # Send prompt and first image to the LLM
        response = call_llm(llm_prompt)

        # Validate response
        if not response:
            response = "Error: LLM could not generate insights. Please check the API or input."

        # Write output to README with UTF-8 encoding
        with open(os.path.join(output_dir, "README.md"), "w", encoding="utf-8") as f:
            f.write("# Dataset Analysis\n\n")
            f.write("## Analysis and Insights\n\n")
            f.write(response)
            f.write("\n\n## Visualizations\n")
            for path in image_paths:
                f.write(f"![Visualization]({os.path.basename(path)})\n")

        print("README.md generated successfully with insights and visualizations.")

    except Exception as e:
        print(f"Error generating README: {e}")


def main():
    if len(sys.argv) != 2:
        print("Usage: uv run autolysis.py <dataset.csv>")
        sys.exit(1)

    file_path = sys.argv[1]
    output_dir = os.path.splitext(os.path.basename(file_path))[0]

    data = load_data(file_path)
    data_summary = data.describe(include="all").to_dict()
    insights = {"missing_values": data.isnull().sum().to_dict()}

    image_paths = generate_visualizations(data, output_dir)
    generate_readme(data_summary, insights, image_paths, output_dir)
    print(f"Analysis complete. Outputs saved in {output_dir}/")

if __name__ == "__main__":
    main()
