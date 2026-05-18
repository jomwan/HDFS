# HDFS MapReduce and Analytics Lab Report: Airline Sentiment Analysis

This report documents the end-to-end Big Data pipeline for the **Twitter US Airline Sentiment** dataset. It covers distributed storage in **HDFS**, summarization using **MapReduce WordCount**, advanced analytics with **PySpark SQL**, and premium **Plotly dashboards**.

---

## 🚀 1. End-to-End Pipeline Summary

1. **Local Host Setup**: Downloaded the real dataset `Tweets.csv` (3.26 MB) and prepared simplified files:
   - `sentiment_labels.txt` (One sentiment label per line)
   - `negative_reasons.txt` (One complaint reason per line)
   - `airline_analytics_subset.csv` (Tabular subset for structured analysis)
2. **Distributed Storage (HDFS)**: Uploaded all datasets to HDFS folder `/airline_lab` under NameNode.
3. **Distributed Ingestion (MapReduce)**: Executed parallel WordCount MapReduce jobs on HDFS `/airline_lab/sentiment_labels.txt` and `/airline_lab/negative_reasons.txt` to count raw token frequencies.
4. **Structured Advanced Analytics (PySpark)**: Read HDFS data via Spark, processed cross-tabulations, persisted tables to **Apache Hive** (`airline_db.tweets_processed`) and **MongoDB** (`airline_sentiment.summary`), and exported localized aggregate summaries.
5. **Interactive Visualization**: Rendered a premium glassmorphic Plotly HTML dashboard showing key insights.

---

## 📈 2. MapReduce WordCount Results

### A. Sentiment Label Frequencies (`output_sentiment`)
The MapReduce job counted 14,640 records with the following distribution:
```text
negative    9,178
neutral     3,099
positive    2,363
```

### B. Complaint Reasons Token Frequencies (`output_reasons`)
The raw WordCount MapReduce job tokenized fields by space. Key word counts are:
```text
Flight       4,102 (From "Late Flight", "Bad Flight", "Flight Booking Problems", etc.)
Customer     2,910 (From "Customer Service Issue")
Service      2,910 (From "Customer Service Issue")
Issue        2,910 (From "Customer Service Issue")
Late         1,665 (From "Late Flight")
Can't        1,190 (From "Can't Tell")
Tell         1,190 (From "Can't Tell")
Luggage        798 (From "Lost Luggage", "Damaged Luggage")
Cancelled      847 (From "Cancelled Flight")
```

> [!NOTE]
> **MapReduce vs. PySpark Parsing**: 
> Basic MapReduce splits words based on white space, counting individual words (e.g. "Customer", "Service", "Issue" separately as 2,910). 
> PySpark SQL preserves CSV parsing structures, allowing us to keep multi-word categories intact (e.g., "Customer Service Issue" as a single entity).

---

## 🧠 3. Advanced Analytics Metrics (PySpark)

### Sentiment Frequencies by Airline (Cross-tabulation)
| Airline | Negative | Neutral | Positive | Total Tweets |
| :--- | :---: | :---: | :---: | :---: |
| **United** | **2,633** | 697 | 492 | 3,822 |
| **US Airways** | **2,263** | 381 | 269 | 2,913 |
| **American** | **1,960** | 463 | 336 | 2,759 |
| **Southwest** | 1,186 | 664 | 570 | 2,420 |
| **Delta** | 955 | 723 | 544 | 2,222 |
| **Virgin America** | 181 | 171 | 152 | 504 |
| **Total** | **9,178** | **3,099** | **2,363** | **14,640** |

---

## 💡 4. Exercise Submission Questions & Answers

### Q1: What is the main sentiment trend in the dataset?
*   **Answer**: The main sentiment trend is **overwhelmingly negative**. Of the 14,640 passenger tweets analyzed, **62.7% (9,178 tweets)** are negative. Neutral feedback accounts for **21.2% (3,099 tweets)**, and positive feedback is only **16.1% (2,363 tweets)**. This baseline illustrates a severe systemic operational or customer relation deficit across domestic carriers during this window.

### Q2: What is the most common customer complaint?
*   **Answer**: The most common passenger complaint is **"Customer Service Issue"**, which accounts for **2,910 complaints** (representing **31.7%** of all negative reviews). This is followed closely by **"Late Flight" (1,665 complaints / 18.1%)** and **"Can't Tell" (1,190 complaints / 13.0%)**. 

### Q3: What is one operational recommendation for airlines based on these insights?
*   **Answer**: **Drastically Scale and Optimize Digital Customer Service Channels.**
    *   *Rationale*: Because the primary driver of passenger frustration is "Customer Service Issue" (2,910 incidents) rather than physical flight delays themselves (1,665 incidents), passenger anger spikes *not* just because a flight is late, but because they are unable to get helpful or timely assistance.
    *   *Action Plan*: Airlines should deploy real-time automated AI chatbots to handle basic re-bookings, increase front-line human agent capacities during operational peak hours, and implement active social media response loops to resolve complaints while passengers are still at the airport.
    *   *Dynamic Staffing*: As shown in the daily volume analysis, traffic peaked at **3,515 tweets on Feb 23**, which likely aligned with severe weather or high cancellation rates. Airlines must design dynamic staff-alert buffers so customer care teams scale up instantly when daily volumes exceed a baseline threshold.

---

## 🎨 5. Interactive Dashboard
Your interactive visual dashboard is generated and saved locally at:
📁 **[airline_sentiment_dashboard.html](file:///c:/HDFS/scenarios/airline_sentiment/notebooks/airline_sentiment_dashboard.html)**

It uses glassmorphism design layouts, and displays:
1.  **Donut Chart**: Overall Sentiment Distribution.
2.  **Grouped Bar Chart**: Sentiment comparison across all 6 major airlines.
3.  **Horizontal Bar Chart**: Most frequent complaint reasons.
4.  **Daily Volume Area Line**: Trends in passenger tweeting frequency.
