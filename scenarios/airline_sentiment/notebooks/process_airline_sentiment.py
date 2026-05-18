from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, to_date, desc
import os

def main():
    print("[INFO] Initializing Spark Session for Airline Sentiment Analytics...")
    
    # 1. Initialize Spark Session with Hive & MongoDB
    spark = SparkSession.builder \
        .appName("AirlineSentimentAnalytics") \
        .config("spark.sql.warehouse.dir", "/user/hive/warehouse") \
        .config("hive.metastore.uris", "thrift://hive-metastore:9083") \
        .config("spark.mongodb.output.uri", "mongodb://admin:admin123@mongodb:27017/airline_sentiment.summary?authSource=admin") \
        .enableHiveSupport() \
        .getOrCreate()
        
    print("[SUCCESS] Spark Session Initialized.")

    # 2. Path resolution for local exports
    script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else '/home/jovyan/work/airline_sentiment/notebooks'
    print(f"[INFO] Script output directory: {script_dir}")

    # 3. Load Data from HDFS
    hdfs_path = "hdfs://namenode:9000/airline_lab/airline_analytics_subset.csv"
    print(f"[INFO] Reading airline data from HDFS: {hdfs_path}")
    df = spark.read.option("header", "true").option("inferSchema", "true").csv(hdfs_path)
    
    df.cache()
    total_records = df.count()
    print(f"[SUCCESS] Loaded {total_records} records.")

    # 4. Aggregation 1: Overall Sentiment Distribution
    print("[ANALYSIS] Computing overall sentiment distribution...")
    sentiment_dist = df.groupBy("airline_sentiment").agg(count("*").alias("count")).orderBy(desc("count"))
    sentiment_dist.show()
    
    # Export locally
    sentiment_dist_pd = sentiment_dist.toPandas()
    sentiment_dist_pd.to_csv(os.path.join(script_dir, "sentiment_distribution.csv"), index=False)
    
    # Aggregation 2: Sentiment by Airline (Cross-tab)
    print("[ANALYSIS] Computing sentiment distribution by airline...")
    airline_sentiment = df.groupBy("airline", "airline_sentiment").agg(count("*").alias("count")).orderBy("airline", "airline_sentiment")
    airline_sentiment.show()
    
    # Export locally
    airline_sentiment_pd = airline_sentiment.toPandas()
    # Pivot for clean visualization compatibility
    airline_pivot = airline_sentiment_pd.pivot(index='airline', columns='airline_sentiment', values='count').fillna(0).reset_index()
    airline_pivot.to_csv(os.path.join(script_dir, "airline_sentiment.csv"), index=False)

    # Aggregation 3: Top Negative Reasons
    print("[ANALYSIS] Computing top negative complaint reasons...")
    neg_reasons = df.filter(col("airline_sentiment") == "negative") \
        .filter(col("negativereason").isNotNull()) \
        .groupBy("negativereason") \
        .agg(count("*").alias("count")) \
        .orderBy(desc("count"))
    neg_reasons.show(15, truncate=False)
    
    # Export locally
    neg_reasons_pd = neg_reasons.toPandas()
    neg_reasons_pd.to_csv(os.path.join(script_dir, "top_negativereasons.csv"), index=False)

    # Aggregation 4: Daily Tweet Volume
    print("[ANALYSIS] Computing daily tweet volume trends...")
    # Convert 'tweet_created' column to Date type (handles ISO 8601 like 2015-02-24 11:35:52 -0800)
    # Extracts substring or converts directly
    daily_volume = df.withColumn("date", to_date(col("tweet_created"))) \
        .filter(col("date").isNotNull()) \
        .groupBy("date") \
        .agg(count("*").alias("count")) \
        .orderBy("date")
    daily_volume.show()
    
    # Export locally
    daily_volume_pd = daily_volume.toPandas()
    daily_volume_pd.to_csv(os.path.join(script_dir, "daily_tweet_volume.csv"), index=False)

    # 5. Save to HIVE
    print("[SAVING] Saving processed dataset to Hive (airline_db.tweets_processed)...")
    try:
        spark.sql("CREATE DATABASE IF NOT EXISTS airline_db")
        df.write.mode("overwrite").saveAsTable("airline_db.tweets_processed")
        print("[SUCCESS] Successfully saved dataset to Hive.")
    except Exception as e:
        print(f"[WARNING] Hive write failed: {e}")

    # 6. Save to MONGODB
    print("[SAVING] Exporting sentiment summary metrics to MongoDB...")
    try:
        sentiment_dist.write.format("mongodb").mode("append").save()
        print("[SUCCESS] Successfully uploaded metrics to MongoDB.")
    except Exception as e:
        print(f"[WARNING] MongoDB write failed: {e}")

    spark.stop()
    print("[SUCCESS] PySpark Processing Pipeline Completed!")

if __name__ == "__main__":
    main()
