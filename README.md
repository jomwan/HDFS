# 🚀 Enterprise Big Data Infrastructure & Analytics Portfolio

Welcome to my distributed big data engineering and analytics portfolio. This repository hosts a fully integrated, multi-container **Hadoop-Spark-Hive-NoSQL cluster** built with Docker/WSL2, alongside production-grade analytic workflows across retail transactions, linguistic sentiment patterns, and financial anomalies.

```
       [ Client / BI Dashboard ]
                   │
                   ▼ (JDBC / Pandas)
            [ Apache Hive ]
                   │ (Schema Meta)
                   ▼
  [ Spark Master ] ───► [ Spark Workers ] (In-Memory Processing)
         │                    │
         ▼                    ▼
   [ HDFS NameNode ] ◄───► [ HDFS DataNodes ] (Distributed Storage)
```

---

## 🛠️ Section 1: Shared Cluster Infrastructure (`ecosystem`)

The core environment leverages **12 containerized services** coordinated via `docker-compose.yml` to simulate an enterprise-scale distributed deployment.

### 🗄️ System Architecture Services:
*   **Storage Core (HDFS)**: NameNode (`9870`) + DataNode (`9864`) to handle replica block storage.
*   **Compute Engine (Apache Spark 3.1.2)**: Spark Master (`8080`) + Spark Worker (`8081`) for low-latency, in-memory DAG executions.
*   **Warehouse Engine (Apache Hive 2.3.2)**: Hive Server (`10000`) + Metastore (`9083`) + PostgreSQL catalog database for structured schemas over HDFS Parquet/CSV backends.
*   **Data Lake Pipeline Orchestrator**: Jupyter Notebook (`8888`) pre-configured with PySpark core linkages.
*   **NoSQL Infrastructure**: MongoDB (`27017`) + Mongo Express UI (`8082`) for document parsing and JSON metrics ingestion.

### ⚡ Quickstart Deployment:
To spin up the cluster, navigate to the ecosystem folder and start the services:
```bash
cd ecosystem
docker-compose up -d
```

### 📂 Portal Map to Web Interfaces:
Enter the direct WSL network adapter IP or host loopback to access the running dashboards:

*   👉 **Jupyter Notebook**: [http://127.0.0.1:8888/?token=analytics](http://127.0.0.1:8888/?token=analytics) *(Static Token: `analytics`)*
*   👉 **HDFS NameNode**: [http://127.0.0.1:9870](http://127.0.0.1:9870) *(Requires Windows `hosts` configuration for file browsing)*
*   👉 **Spark Master UI**: [http://127.0.0.1:8080](http://127.0.0.1:8080)
*   👉 **YARN ResourceManager**: [http://127.0.0.1:8088](http://127.0.0.1:8088)
*   👉 **Mongo Express**: [http://127.0.0.1:8082](http://127.0.0.1:8082)

---

## 📊 Section 2: Big Data Analytics Scenarios

This repository contains fully implemented data pipelines in the `scenarios/` directory:

### 🛍️ 1. Retail Transaction Analytics (`scenarios/retail_transaction_analytics`)
*   **Objectives**: Load real-world UCI transaction logs (~500,000 lines), clean missing user IDs/corrupt metrics, execute temporal waves, detect bulk purchase anomalies, and export production datasets.
*   **Key Scripts**:
    *   [process_retail_analytics.py](file:///c:/HDFS/scenarios/retail_transaction_analytics/notebooks/process_retail_analytics.py): PySpark cleaning and statistical aggregations using **DataFrame caching (`.cache()`)** for memory optimization.
    *   [visualize_retail_analytics.py](file:///c:/HDFS/scenarios/retail_transaction_analytics/notebooks/visualize_retail_analytics.py): Generates interactive visual metrics from summaries.
*   **Interactive Asset**: [retail_analytics_dashboard.html](file:///c:/HDFS/scenarios/retail_transaction_analytics/notebooks/retail_analytics_dashboard.html) — A self-contained, high-performance HTML/JS **glassmorphic business intelligence dashboard**.
*   **Executive Report**: [lab_interpretation.md](file:///c:/HDFS/scenarios/retail_transaction_analytics/lab_interpretation.md) (Thoroughly answers Spark lazy evaluation vs MapReduce differences, peak hour optimizations, and geographical market expansion strategies).

### ✈️ 2. Airline Sentiment NLP Analysis (`scenarios/airline_sentiment`)
*   **Objectives**: Ingest social feed streams, structure unstructured linguistic text using PySpark, perform data understanding, extract sentiment classifications, and visualize consumer response matrices.
*   **Key Scripts**:
    *   [process_airline_sentiment.py](file:///c:/HDFS/scenarios/airline_sentiment/notebooks/process_airline_sentiment.py): Structures tweet metadata and categorizes text patterns.
    *   [visualize_airline_sentiment.py](file:///c:/HDFS/scenarios/airline_sentiment/notebooks/visualize_airline_sentiment.py): Renders the linguistic metrics.
*   **Executive Report**: [lab_interpretation.md](file:///c:/HDFS/scenarios/airline_sentiment/lab_interpretation.md) (Covers language tokenizations, sentiment matrices, and customer service recommendations).

---

## 📤 Section 3: Publishing to GitHub

To push this entire big data portfolio to your GitHub account:

1.  **Initialize Git**:
    ```bash
    git init
    ```
2.  **Add Files**:
    *(Note: Our custom `.gitignore` will automatically prevent huge datasets like Tweets.csv or OnlineRetail.csv from uploading)*
    ```bash
    git add .
    ```
3.  **Commit Code**:
    ```bash
    git commit -m "feat: complete big data HDFS-Spark cluster portfolio with retail & sentiment scenarios"
    ```
4.  **Add Remote and Push**:
    Create a new repository on [GitHub](https://github.com/) named `Hadoop-Spark-Big-Data-Analytics-Portfolio` (leave it empty without initializing README or gitignore), then run:
    ```bash
    git branch -M main
    git remote add origin https://github.com/YOUR_GITHUB_USERNAME/Hadoop-Spark-Big-Data-Analytics-Portfolio.git
    git push -u origin main
    ```
