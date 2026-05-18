import json
import random
import os
import subprocess
from datetime import datetime, timedelta

# Thai review templates
positive_reviews = [
    "ดีมากครับ ส่งไวมาก",
    "ของแท้แน่นอน แนะนำร้านนี้เลย",
    "คุ้มค่าคุ้มราคา คุณภาพดีมาก",
    "ใช้ดีบอกต่อ เพื่อนชอบมาก",
    "แพ็คมาดีมาก ไม่มีรอยบุบเลย",
    "สีสวยตรงปก ชอบมากครับ",
    "จัดส่งรวดเร็ว บริการดีเยี่ยม",
    "สินค้าคุณภาพดีมาก ประทับใจสุดๆ"
]

negative_reviews = [
    "ส่งช้ามาก ไม่แนะนำ",
    "ของไม่ตรงปก ผิดหวังมาก",
    "คุณภาพแย่ ใช้แป๊บเดียวพัง",
    "แพ็คมาไม่ดี กล่องบุบเสียหาย",
    "ติดต่อร้านยากมาก ไม่ตอบแชทเลย",
    "แพงเกินไป ไม่คุ้มค่า",
    "สินค้ามีรอยตำหนิ แย่มาก",
    "ไม่อยากให้ดาวเลย บริการแย่"
]

categories = ["เครื่องสำอาง", "อิเล็กทรอนิกส์", "แฟชั่น", "อาหารและเครื่องดื่ม"]
products = {
    "เครื่องสำอาง": ["เซรั่มหน้าใส", "ลิปสติกแมตต์", "ครีมกันแดด", "แป้งพัฟ"],
    "อิเล็กทรอนิกส์": ["หูฟังบลูทูธ", "พาวเวอร์แบงค์", "สายชาร์จไว", "ลำโพงไร้สาย"],
    "แฟชั่น": ["เสื้อยืด Oversize", "กางเกงยีนส์ขากระบอก", "กระเป๋าสะพายข้าง", "หมวกแก๊ป"],
    "อาหารและเครื่องดื่ม": ["กาแฟดริป", "ชาไทยพรีเมียม", "ขนมคลีน", "เวย์โปรตีน"]
}

def generate_data(num_records=10000):
    data = []
    start_date = datetime(2024, 1, 1)
    
    for i in range(num_records):
        cat = random.choice(categories)
        prod = random.choice(products[cat])
        is_pos = random.random() > 0.3 # 70% positive
        text = random.choice(positive_reviews if is_pos else negative_reviews)
        rating = random.randint(4, 5) if is_pos else random.randint(1, 2)
        
        # Add some random noise to text
        if random.random() > 0.8:
            text += "!!!"
            
        record = {
            "review_id": f"REV-{i:06d}",
            "product_name": prod,
            "category": cat,
            "review_text": text,
            "rating": rating,
            "sales_count": random.randint(1, 500),
            "timestamp": (start_date + timedelta(days=random.randint(0, 120))).isoformat()
        }
        data.append(record)
    return data

def main():
    print("Generating synthetic Thai shop data...")
    records = generate_data(20000) # Start with 20k for testing, can scale up
    
    local_file = "c:/HDFS/scenarios/thai_shop_reviews/data/thai_shop_reviews.json"
    os.makedirs(os.path.dirname(local_file), exist_ok=True)
    
    with open(local_file, 'w', encoding='utf-8') as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            
    print(f"Generated {len(records)} records at {local_file}")
    
    # Upload to HDFS
    print("Uploading to HDFS...")
    subprocess.run("docker exec namenode hdfs dfs -mkdir -p /data/thai_shop", shell=True)
    # Since the scenarios directory is mounted as a volume in the namenode container,
    # we can upload it directly to HDFS without a temporary docker cp!
    subprocess.run("docker exec namenode hdfs dfs -put -f /scenarios/thai_shop_reviews/data/thai_shop_reviews.json /data/thai_shop/", shell=True)
    print("Success! Data is in HDFS at /data/thai_shop/thai_shop_reviews.json")

if __name__ == "__main__":
    main()
