from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, sum, avg, when, desc
import os

# 1. Initialize Spark
spark = SparkSession.builder \
    .appName("FraudDetection_PaySim") \
    .config("spark.sql.warehouse.dir", "/user/hive/warehouse") \
    .config("hive.metastore.uris", "thrift://hive-metastore:9083") \
    .config("spark.mongodb.output.uri", "mongodb://admin:admin123@mongodb:27017/fraud_detection.alerts?authSource=admin") \
    .enableHiveSupport() \
    .getOrCreate()

print("Spark Session Initialized for Fraud Analysis.")

# 2. Load Data from HDFS
df = spark.read.csv("hdfs://namenode:9000/data/paysim/paysim_data.csv", header=True, inferSchema=True)
print(f"Loaded PaySim dataset with {df.count()} records.")

# 3. Basic Analysis: Fraud by Transaction Type
fraud_types = df.groupBy("type") \
    .agg(
        count("*").alias("total_trans"),
        sum(when(col("isFraud") == 1, 1).otherwise(0)).alias("fraud_count"),
        avg("amount").alias("avg_amount")
    ).orderBy(desc("fraud_count"))

print("Fraud Distribution by Type:")
fraud_types.show()

# 4. Feature Engineering: Balance Discrepancy
# For fraudulent transactions, often the destination balance doesn't update correctly or amount is 0
df_enriched = df.withColumn("dest_diff", col("newbalanceDest") - col("oldbalanceDest")) \
                .withColumn("is_suspicious", when((col("amount") > 0) & (col("dest_diff") == 0), 1).otherwise(0))

# 5. Extract "High Alert" Transactions (Confirmed Fraud)
high_alert = df_enriched.filter(col("isFraud") == 1) \
    .select("step", "type", "amount", "nameOrig", "nameDest", "is_suspicious") \
    .orderBy(desc("amount"))

# 6. SAVE TO HIVE
print("Saving full analysis to Hive...")
try:
    spark.sql("CREATE DATABASE IF NOT EXISTS fraud_db")
    df_enriched.limit(100000).write.mode("overwrite").saveAsTable("fraud_db.paysim_processed") # Limiting for speed in this demo
    print("Success: Saved to Hive.")
except Exception as e:
    print(f"Warning: Hive save failed ({e})")

# 7. SAVE TO MONGODB (Only Fraud Alerts)
print("Saving alerts to MongoDB...")
try:
    high_alert.write.format("mongo").mode("overwrite").save()
    print("Success: Saved Alerts to MongoDB.")
except Exception as e:
    print(f"Warning: MongoDB save failed ({e})")

# 8. EXPORT FOR PLOTLY
print("Exporting stats for Plotly...")
script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else '/home/jovyan/work/fraud_detection/notebooks'
fraud_types.toPandas().to_csv(os.path.join(script_dir, "fraud_summary.csv"), index=False)
high_alert.limit(500).toPandas().to_csv(os.path.join(script_dir, "fraud_alerts.csv"), index=False)

print("Fraud Analysis Pipeline Complete!")
