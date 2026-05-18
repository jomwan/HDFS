import os
import shutil

def main():
    print("[INFO] Organizing Retail Transaction Analytics Scenario...")
    
    base_dir = r"c:\HDFS\scenarios\retail_transaction_analytics"
    data_dir = os.path.join(base_dir, "data")
    notebooks_dir = os.path.join(base_dir, "notebooks")
    
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(notebooks_dir, exist_ok=True)
    
    src_csv = os.path.join(base_dir, "OnlineRetail.csv")
    dest_csv = os.path.join(data_dir, "OnlineRetail.csv")
    
    if os.path.exists(src_csv):
        print(f"[MOVE] Moving {src_csv} to {dest_csv}")
        shutil.move(src_csv, dest_csv)
        print("[SUCCESS] OnlineRetail.csv moved successfully.")
    elif os.path.exists(dest_csv):
        print("[INFO] OnlineRetail.csv is already in the data directory.")
    else:
        print("[ERROR] OnlineRetail.csv not found!")

if __name__ == "__main__":
    main()
