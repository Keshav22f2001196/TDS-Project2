import sys
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import requests
from dotenv import load_dotenv
from sklearn.impute import SimpleImputer
from sklearn.cluster import KMeans

# Load environment variables
load_dotenv()
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")

if not AIPROXY_TOKEN:
    print("Error: AIPROXY_TOKEN not set. Please configure your environment variable.")
    sys.exit(1)

# Constants
LLM_URL = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
HEADERS = {"Authorization": f"Bearer {AIPROXY_TOKEN}"}

def load_data(file_path):
    """Load dataset from a CSV file with multiple encoding fallbacks."""
    encodings = ["utf-8", "ISO-8859-1", "latin1"]
    if not os.path.isfile(file_path):
        print(f"Error: File {file_path} does not exist.")
        sys.exit(1)
    
    for encoding in encodings:
        try:
            print(f"Attempting to load file: {file_path} with {encoding} encoding...")
            data = pd.read_csv(file_path, encoding=encoding)
            if data.empty:
                print(f"Warning: Dataset loaded with {encoding} encoding but is empty.")
            else:
                print(f"File loaded successfully with {encoding} encoding.")
            return data
        except (UnicodeDecodeError, pd.errors.ParserError) as e:
            print(f"{encoding} decoding/parsing failed for {file_path}: {e}. Trying next encoding...")
        except Exception as e:
            print(f"Error with {encoding} encoding for {file_path}: {e}")

    print("All encoding attempts failed. Please check the file.")
    sys.exit(1)

def preprocess_data(data):
    """Handle missing values in numeric columns by imputing with the column mean."""
    numeric_data = data.select_dtypes(include=["number"])
    imputer = SimpleImputer(strategy="mean")
    numeric_data_imputed = pd.DataFrame(imputer.fit_transform(numeric_data), columns=numeric_data.columns)
    return numeric_data_imputed

def analyze_data(data):
    """Perform basic analysis on the dataset."""
    analysis = {
        "summary_statistics": data.describe(include="all").to_dict(),
        "missing_values": data.isnull().sum().to_dict(),
    }
    numeric_data = data.select_dtypes(include=["number"])
    if not numeric_data.empty:
        analysis["correlation_matrix"] = numeric_data.corr().to_dict()
        analysis["outliers"] = detect_outliers(data)
        analysis["cluster_analysis"] = cluster_analysis(data)
    return analysis

def detect_outliers(data):
    """Detect outliers in numeric columns using the IQR method."""
    numeric_data = data.select_dtypes(include=["number"])
    outliers = {}
    for column in numeric_data.columns:
        q1 = numeric_data[column].quantile(0.25)
        q3 = numeric_data[column].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers[column] = numeric_data[(numeric_data[column] < lower_bound) | (numeric_data[column] > upper_bound)].index.tolist()
    return outliers

def cluster_analysis(data):
    """Perform clustering on numeric columns."""
    numeric_data_imputed = preprocess_data(data)
    if numeric_data_imputed.shape[1] < 2:
        return "Not enough numeric columns for clustering."
    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(numeric_data_imputed)
    return {
        "centroids": kmeans.cluster_centers_.tolist(),
        "labels": clusters.tolist()
    }

def visualize_data(data, output_dir):
    """Generate and save enhanced visualizations."""
    os.makedirs(output_dir, exist_ok=True)
    numeric_data = data.select_dtypes(include=["number"])
    if numeric_data.empty:
        print("No numeric data available for visualization.")
        return
    # Correlation Heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(numeric_data.corr(), annot=True, cmap="coolwarm")
    plt.title("Correlation Heatmap")
    plt.savefig(os.path.join(output_dir, "correlation_heatmap.png"))
    plt.close()
    # Cluster Visualization
    numeric_data_imputed = preprocess_data(data)
    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(numeric_data_imputed)
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=numeric_data_imputed.iloc[:, 0], y=numeric_data_imputed.iloc[:, 1], hue=clusters, palette="viridis")
    plt.title("Cluster Visualization")
    plt.savefig(os.path.join(output_dir, "cluster_visualization.png"))
    plt.close()

def generate_narrative(data, analysis, output_dir):
    """Generate a narrative using the LLM."""
    prompt = f"""
    The dataset titled "{os.path.basename(output_dir)}" provides insights into:
    - Summary Statistics: {analysis["summary_statistics"]}.
    - Missing Values: {analysis["missing_values"]}.
    - Correlation Matrix: {analysis.get("correlation_matrix", "Not available")}.
    - Outliers: {analysis.get("outliers", "Not available")}.
    - Cluster Analysis: {analysis.get("cluster_analysis", "Not performed")}.
    Craft a business-oriented report summarizing these findings and providing actionable recommendations.
    """
    try:
        response = requests.post(LLM_URL, headers=HEADERS, json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}]
        })
        if response.status_code == 200:
            narrative = response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            return narrative if narrative else "No narrative generated. Please review manually."
        print(f"LLM request failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error generating narrative: {e}")
    return "Fallback narrative: Unable to process insights. Check visualizations for details."

def save_readme(narrative, output_dir):
    """Save narrative and visualizations to README.md."""
    readme_path = os.path.join(output_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("# Dataset Analysis\n\n")
        f.write("## Narrative Insights\n\n")
        f.write(narrative)
        f.write("\n\n## Key Visualizations\n\n")
        for file in os.listdir(output_dir):
            if file.endswith(".png"):
                f.write(f"![{file}]({file})\n")

def main():
    if len(sys.argv) != 2:
        print("Usage: python autolysis.py <dataset.csv>")
        sys.exit(1)
    file_path = sys.argv[1]
    if not file_path.endswith(".csv"):
        print("Error: File is not a CSV.")
        sys.exit(1)
    output_dir = os.path.splitext(file_path)[0]
    os.makedirs(output_dir, exist_ok=True)
    data = load_data(file_path)
    analysis = analyze_data(data)
    visualize_data(data, output_dir)
    narrative = generate_narrative(data, analysis, output_dir)
    save_readme(narrative, output_dir)
    print(f"Analysis complete. Outputs saved in {output_dir}/")

if __name__ == "__main__":
    main()
