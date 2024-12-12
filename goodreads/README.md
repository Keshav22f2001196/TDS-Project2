# Dataset Analysis

## Narrative Insights

### Business Report: Analysis of Goodreads Dataset

#### Executive Summary:
This report presents an analysis of the Goodreads dataset, focusing on summary statistics, missing values, correlation metrics, and clusters found within the data. The primary goal is to extract actionable insights that can inform strategic decision-making in the book publishing and retail industry, enabling firms to enhance product offerings and improve customer engagement.

#### 1. Summary Statistics:
- **Dataset Overview**: The dataset consists of 10,000 entries detailing books, including essential attributes such as book IDs, authors, publication years, average ratings, and review counts.
- **Average Ratings**: The mean average rating across all books is approximately **4.00**, indicating a generally positive reception from readers. The ratings range from **2.47** to **4.82**.
- **Author Popularity**: The dataset has **4664 unique authors**, with significant representation from popular authors like **Stephen King**, who appears in **60 entries**.
- **Publication Trends**: The average original publication year is around **1981.99**, suggesting a large number of older literary works are well-represented in current collections.

#### 2. Missing Values:
- **Missing Entries**: Several fields have missing values which could impact data analysis, notably `ISBN` (700 missing), `ISBN13` (585 missing), and `original_publication_year` (21 missing). 
- **Actionable Recommendation**: Efforts should be made to clean this data or impute missing values to ensure comprehensive analysis. Gathering complete ISBN data would improve inventory accuracy and analytics capabilities.

#### 3. Correlation Analysis:
- **Key Findings**:
  - Strong negative correlation between `books_count` and `ratings_count` (r = -0.373) suggests that higher book counts for an author may not correlate with higher ratings for each book.
  - A robust negative correlation is observed between `work_text_reviews_count` and ratings across all score categories, hinting at a trend where books with fewer reviews could receive higher ratings.
- **Actionable Recommendation**: Marketing strategies should consider promoting individual titles by authors with extensive bibliographies to emphasize quality over quantity, particularly if the individual books have secured higher ratings.

#### 4. Outlier Identifications:
- **Outliers Detected**: The dataset highlights numerous outliers in specific attributes (e.g., `goodreads_book_id`, `best_book_id`). For example, entries such as 33288638 in `goodreads_book_id` represent exceptionally high popularity or historical significance.
- **Actionable Recommendation**: Target these outlier titles within marketing campaigns, focusing on building visibility through promotions and recommendations as they may appeal to niche audiences.

#### 5. Cluster Analysis:
- **Clusters Found**: The clustering analysis identified three distinct groups of books based on multiple features, including average ratings, publication year, and review counts.
  - **Cluster one**: Represents books with average ratings around **4.00** and a balanced number of reviews.
  - **Cluster two**: Books in this cluster show potential for growth in the market (high average ratings, high publication year, and less accessibility).
  - **Cluster three**: Contains older publications that continue to attract readers (high books count with relatively low average ratings).
- **Actionable Recommendation**: Develop targeted marketing strategies for each cluster. For example, promote newer works from Cluster two heavily to leverage their momentum and include classic older titles in recommendations for less familiar consumers.

#### 6. Conclusion:
The analysis of the Goodreads dataset presents a rich landscape of consumer preferences and behaviors. By addressing data quality issues, enhancing understanding of correlations between various attributes, and leveraging cluster trends, businesses can improve their product placements and marketing strategies. 

#### 7. Next Steps:
- Prioritize data cleaning efforts to mitigate missing values.
- Implement targeted marketing campaigns focused on high-popularity outliers and segmented clusters.
- Continuously monitor data trends to adapt to changing consumer preferences and industry standards.

By utilizing these actionable insights, businesses can better position themselves to meet consumer demands and enhance overall customer satisfaction and engagement.

## Key Visualizations

![cluster_visualization.png](cluster_visualization.png)
![correlation_heatmap.png](correlation_heatmap.png)
