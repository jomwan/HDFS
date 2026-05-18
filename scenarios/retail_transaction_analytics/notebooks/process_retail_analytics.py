from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when, sum as _sum, countDistinct, avg, to_timestamp, to_date, year, month, dayofmonth, hour, round as _round
import os

def main():
    print("[INFO] Initializing Spark Session for Retail Transaction Analytics...")
    
    # 1. Initialize Spark Session with Hive & MongoDB
    spark = SparkSession.builder \
        .appName("RetailBigDataPipeline") \
        .config("spark.sql.warehouse.dir", "/user/hive/warehouse") \
        .config("hive.metastore.uris", "thrift://hive-metastore:9083") \
        .config("spark.mongodb.output.uri", "mongodb://admin:admin123@mongodb:27017/retail_analytics.summary?authSource=admin") \
        .enableHiveSupport() \
        .getOrCreate()
        
    print("[SUCCESS] Spark Session Initialized.")

    # 2. Path resolution for local exports
    script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else '/home/jovyan/work/retail_transaction_analytics/notebooks'
    print(f"[INFO] Script output directory: {script_dir}")

    # 3. Load Data from HDFS
    hdfs_path = "hdfs://namenode:9000/retail_lab/OnlineRetail.csv"
    print(f"[INFO] Reading retail data from HDFS: {hdfs_path}")
    df = spark.read.option("header", "true").option("inferSchema", "true").csv(hdfs_path)
    
    total_raw_records = df.count()
    print(f"[SUCCESS] Loaded {total_raw_records:,} raw records.")
    
    # Explore Data / Show schema
    df.printSchema()
    
    # Identify Dirty Data / Null Counts
    print("[ANALYSIS] Checking for missing values (null counts)...")
    null_counts = df.select([count(when(col(c).isNull(), c)).alias(c) for c in df.columns])
    null_counts.show()

    # 4. Data Cleaning and Feature Engineering
    print("[CLEANING] Filtering out invalid rows and missing customer IDs...")
    # Drop rows where CustomerID is null
    df_clean = df.dropna(subset=["CustomerID"])
    # Filter positive quantities and unit prices
    df_clean = df_clean.filter(col("Quantity") > 0)
    df_clean = df_clean.filter(col("UnitPrice") > 0)
    
    # Feature Engineering: TotalAmount
    df_clean = df_clean.withColumn("TotalAmount", col("Quantity") * col("UnitPrice"))
    
    # CRITICAL OPTIMIZATION: Cache df_clean to prevent HDFS CSV re-reads
    df_clean.cache()
    
    total_cleaned_records = df_clean.count()
    print(f"[CLEANING] Finished cleaning. Kept {total_cleaned_records:,} valid transaction lines.")

    # 5. SPARK ANALYTICS PROCESSING
    
    # C1 — Sales by Country
    print("[ANALYSIS] Computing total sales by country...")
    sales_by_country = df_clean.groupBy("Country") \
        .agg(_round(_sum("TotalAmount"), 2).alias("TotalSales")) \
        .orderBy(col("TotalSales").desc())
    sales_by_country.show(20, truncate=False)
    
    # Export locally
    sales_by_country.toPandas().to_csv(os.path.join(script_dir, "sales_by_country.csv"), index=False)
    print("[FILE] Exported sales_by_country.csv")

    # C2 — Top Products by Quantity and Revenue
    print("[ANALYSIS] Computing top products by units sold...")
    top_products = df_clean.groupBy("StockCode", "Description") \
        .agg(
            _sum("Quantity").alias("TotalUnitsSold"),
            _round(_sum("TotalAmount"), 2).alias("TotalRevenue"),
            count("*").alias("TransactionCount")
        ) \
        .orderBy(col("TotalUnitsSold").desc())
    top_products.show(10, truncate=False)
    
    # Export locally
    top_products.limit(100).toPandas().to_csv(os.path.join(script_dir, "top_products.csv"), index=False)
    print("[FILE] Exported top_products.csv")

    # C3 — Customer Behavior
    print("[ANALYSIS] Computing customer activity and high spenders...")
    highest_spending_customers = df_clean.groupBy("CustomerID") \
        .agg(
            _round(_sum("TotalAmount"), 2).alias("TotalSpent"),
            countDistinct("InvoiceNo").alias("UniqueInvoices")
        ) \
        .orderBy(col("TotalSpent").desc())
    highest_spending_customers.show(10, truncate=False)
    
    # Export locally
    highest_spending_customers.limit(100).toPandas().to_csv(os.path.join(script_dir, "highest_spending_customers.csv"), index=False)
    print("[FILE] Exported highest_spending_customers.csv")

    # C4 — Time-Based Analysis
    print("[ANALYSIS] Parsing InvoiceDate and doing time-based analytics...")
    # Clean the date and time parsing. Handle formats like "d/M/yyyy H:mm"
    df_time = df_clean.withColumn("InvoiceTimestamp", to_timestamp(col("InvoiceDate"), "d/M/yyyy H:mm"))
    
    # Fallback to handle alternative date formats if needed
    df_time = df_time.withColumn("InvoiceTimestamp", 
        when(col("InvoiceTimestamp").isNull(), to_timestamp(col("InvoiceDate"), "M/d/yyyy H:mm"))
        .otherwise(col("InvoiceTimestamp"))
    )
    
    df_time = df_time.withColumn("InvoiceDay", to_date(col("InvoiceTimestamp"))) \
                     .withColumn("Year", year(col("InvoiceTimestamp"))) \
                     .withColumn("Month", month(col("InvoiceTimestamp"))) \
                     .withColumn("Day", dayofmonth(col("InvoiceTimestamp"))) \
                     .withColumn("Hour", hour(col("InvoiceTimestamp")))
                     
    # CRITICAL OPTIMIZATION: Cache df_time
    df_time.cache()
                     
    # A. Daily Sales
    daily_sales = df_time.filter(col("InvoiceDay").isNotNull()) \
        .groupBy("InvoiceDay") \
        .agg(
            _round(_sum("TotalAmount"), 2).alias("DailySales"),
            count("*").alias("TransactionLines")
        ) \
        .orderBy("InvoiceDay")
    daily_sales.show(20, truncate=False)
    
    # Export locally
    daily_sales.toPandas().to_csv(os.path.join(script_dir, "daily_sales.csv"), index=False)
    print("[FILE] Exported daily_sales.csv")

    # B. Monthly Sales
    monthly_sales = df_time.filter(col("InvoiceDay").isNotNull()) \
        .groupBy("Year", "Month") \
        .agg(
            _round(_sum("TotalAmount"), 2).alias("MonthlySales"),
            count("*").alias("TransactionLines")
        ) \
        .orderBy("Year", "Month")
    monthly_sales.show(20, truncate=False)
    
    # Export locally
    monthly_sales.toPandas().to_csv(os.path.join(script_dir, "monthly_sales.csv"), index=False)
    print("[FILE] Exported monthly_sales.csv")

    # C. Hourly sales
    hourly_pattern = df_time.filter(col("Hour").isNotNull()) \
        .groupBy("Hour") \
        .agg(
            count("*").alias("TransactionLines"),
            _round(_sum("TotalAmount"), 2).alias("HourlySales")
        ) \
        .orderBy("Hour")
    hourly_pattern.show(24, truncate=False)
    
    # Export locally
    hourly_pattern.toPandas().to_csv(os.path.join(script_dir, "hourly_pattern.csv"), index=False)
    print("[FILE] Exported hourly_pattern.csv")

    # C5 — Fraud Simulation / Suspicious Transactions
    print("[ANALYSIS] Running anomaly detection / suspicious transaction flagger...")
    # A transaction line is suspicious if Quantity >= 500 OR TotalAmount >= 10000
    df_suspicious = df_time.withColumn(
        "SuspiciousFlag",
        when((col("Quantity") >= 500) | (col("TotalAmount") >= 10000), 1).otherwise(0)
    )
    
    # A. Suspicious Summary
    suspicious_summary = df_suspicious.groupBy("SuspiciousFlag").count().orderBy("SuspiciousFlag")
    suspicious_summary.show()
    
    # B. Suspicious Transactions list
    suspicious_transactions = df_suspicious.filter(col("SuspiciousFlag") == 1) \
        .select(
            "InvoiceNo", "CustomerID", "StockCode", "Description",
            "Quantity", "UnitPrice", "TotalAmount", "Country",
            "InvoiceTimestamp", "SuspiciousFlag"
        ) \
        .orderBy(col("TotalAmount").desc())
    suspicious_transactions.show(20, truncate=False)
    
    # Export locally
    suspicious_transactions.limit(100).toPandas().to_csv(os.path.join(script_dir, "suspicious_transactions.csv"), index=False)
    print("[FILE] Exported suspicious_transactions.csv")
    
    # Export cleaned transactional data with flags (first 10000 rows to prevent host-size overhead, or write to HDFS)
    print("[CLEANING] Exporting sample of clean retail with flags...")
    df_suspicious.limit(10000).toPandas().to_csv(os.path.join(script_dir, "clean_retail_with_flags.csv"), index=False)
    print("[FILE] Exported clean_retail_with_flags.csv")

    # C. Suspicious Transactions by Country
    suspicious_by_country = df_suspicious.groupBy("Country") \
        .agg(
            count(when(col("SuspiciousFlag") == 1, True)).alias("SuspiciousCount"),
            count("*").alias("TotalTransactions")
        ) \
        .orderBy(col("SuspiciousCount").desc())
    suspicious_by_country.show(20, truncate=False)
    
    # Export locally
    suspicious_by_country.toPandas().to_csv(os.path.join(script_dir, "suspicious_by_country.csv"), index=False)
    print("[FILE] Exported suspicious_by_country.csv")

    # 6. SAVE TO HIVE
    print("[SAVING] Saving processed dataset to Hive (retail_db.clean_retail)...")
    try:
        spark.sql("CREATE DATABASE IF NOT EXISTS retail_db")
        df_suspicious.write.mode("overwrite").saveAsTable("retail_db.clean_retail")
        print("[SUCCESS] Successfully saved dataset to Hive.")
    except Exception as e:
        print(f"[WARNING] Hive write failed: {e}")

    # 7. SAVE TO MONGODB
    print("[SAVING] Exporting overall sales summary metrics to MongoDB...")
    try:
        sales_by_country.write.format("mongodb").mode("append").save()
        print("[SUCCESS] Successfully uploaded metrics to MongoDB.")
    except Exception as e:
        print(f"[WARNING] MongoDB write failed: {e}")

    # Clean up cache
    df_clean.unpersist()
    df_time.unpersist()

    spark.stop()
    print("[SUCCESS] PySpark Processing Pipeline Completed!")

if __name__ == "__main__":
    main()
