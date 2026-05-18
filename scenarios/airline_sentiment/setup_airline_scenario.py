import os
import urllib.request
import pandas as pd

def main():
    print("[INFO] Setting up Airline Sentiment Scenario...")
    
    # Define directories
    base_dir = r"c:\HDFS\scenarios\airline_sentiment"
    data_dir = os.path.join(base_dir, "data")
    notebooks_dir = os.path.join(base_dir, "notebooks")
    
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(notebooks_dir, exist_ok=True)
    
    # Download dataset
    url = "https://raw.githubusercontent.com/ruchitgandhi/Twitter-Airline-Sentiment-Analysis/refs/heads/master/Tweets.csv"
    tweets_csv_path = os.path.join(data_dir, "Tweets.csv")
    
    print(f"[DOWNLOAD] Downloading dataset from: {url}")
    print(f"[DOWNLOAD] Saving to: {tweets_csv_path}")
    
    try:
        urllib.request.urlretrieve(url, tweets_csv_path)
        file_size_mb = os.path.getsize(tweets_csv_path) / (1024 * 1024)
        print(f"[SUCCESS] Download successful! File size: {file_size_mb:.2f} MB")
    except Exception as e:
        print(f"[ERROR] Error downloading file: {e}")
        return

    # Prepare simplified files
    print("\n[PREP] Preparing simplified files for MapReduce...")
    try:
        df = pd.read_csv(tweets_csv_path)
        
        # 1. sentiment_labels.txt
        sentiment_path = os.path.join(data_dir, "sentiment_labels.txt")
        df['airline_sentiment'].dropna().to_csv(sentiment_path, index=False, header=False)
        print(f"[FILE] Created sentiment labels file at: {sentiment_path}")
        
        # 2. negative_reasons.txt
        reasons_path = os.path.join(data_dir, "negative_reasons.txt")
        df['negativereason'].dropna().to_csv(reasons_path, index=False, header=False)
        print(f"[FILE] Created negative reasons file at: {reasons_path}")
        
        # 3. airline_analytics_subset.csv
        subset_path = os.path.join(data_dir, "airline_analytics_subset.csv")
        df[['airline', 'airline_sentiment', 'negativereason', 'tweet_created']].to_csv(subset_path, index=False)
        print(f"[FILE] Created analytics subset at: {subset_path}")
        
        print("\n[SUCCESS] Dataset setup and prep completed successfully!")
    except Exception as e:
        print(f"[ERROR] Error preparing files: {e}")

if __name__ == "__main__":
    main()
