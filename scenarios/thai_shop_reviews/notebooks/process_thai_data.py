from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col, count, avg, desc
from pyspark.sql.types import StringType, ArrayType
from pythainlp import word_tokenize
import os

# 1. Initialize Spark Session with Hive and MongoDB support
spark = SparkSession.builder \
    .appName("ThaiShopAnalytics_Full") \
    .config("spark.sql.warehouse.dir", "/user/hive/warehouse") \
    .config("hive.metastore.uris", "thrift://hive-metastore:9083") \
    .config("spark.mongodb.output.uri", "mongodb://admin:admin123@mongodb:27017/thai_shop.leaderboard?authSource=admin") \
    .enableHiveSupport() \
    .getOrCreate()

print("Spark Session Initialized.")

# 2. Load Data from HDFS
df = spark.read.json("hdfs://namenode:9000/data/thai_shop/thai_shop_reviews.json")

# 3. Thai NLP UDFs
@udf(returnType=StringType())
def get_sentiment(text):
    if not text: return "Neutral"
    positive_words = ["ดี", "ชอบ", "คุ้ม", "ไว", "แนะนำ", "สวย"]
    negative_words = ["แย่", "ช้า", "ผิดหวัง", "พัง", "แพง", "ยาก"]
    tokens = word_tokenize(text, engine="newmm")
    pos_count = sum(1 for t in tokens if t in positive_words)
    neg_count = sum(1 for t in tokens if t in negative_words)
    if pos_count > neg_count: return "Positive"
    elif neg_count > pos_count: return "Negative"
    else: return "Neutral"

# 4. Apply Processing
processed_df = df.withColumn("sentiment", get_sentiment(col("review_text")))

# 5. Aggregate Trends
trends = processed_df.groupBy("category", "sentiment") \
    .agg(count("*").alias("review_count"), avg("rating").alias("avg_rating")) \
    .orderBy("category", "sentiment")

# 6. Top 10 Products Leaderboard
leaderboard = processed_df.filter(col("sentiment") == "Positive") \
    .groupBy("product_name", "category") \
    .agg(count("*").alias("positive_reviews"), avg("rating").alias("avg_rating")) \
    .orderBy(desc("positive_reviews")) \
    .limit(10)

# 7. SAVE TO HIVE
print("Saving to Hive...")
try:
    spark.sql("CREATE DATABASE IF NOT EXISTS thai_shop_db")
    processed_df.write.mode("overwrite").saveAsTable("thai_shop_db.reviews_processed")
    print("Success: Saved to Hive.")
except Exception as e:
    print(f"Warning: Hive save failed ({e}). Proceeding...")

# 8. SAVE TO MONGODB
print("Saving to MongoDB...")
try:
    # We use 'mongo' format which requires the connector jar
    leaderboard.write.format("mongo").mode("overwrite").save()
    print("Success: Saved to MongoDB.")
except Exception as e:
    print(f"Warning: MongoDB save failed ({e}). Check if connector is present.")

# 9. EXPORT TO CSV FOR PLOTLY
print("Exporting summary to CSV for Plotly...")
trends_pd = trends.toPandas()
script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else '/home/jovyan/work/thai_shop_reviews/notebooks'
trends_pd.to_csv(os.path.join(script_dir, "thai_trends_summary.csv"), index=False)
leaderboard.toPandas().to_csv(os.path.join(script_dir, "thai_leaderboard.csv"), index=False)

print("Pipeline execution complete!")
