import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

def main():
    print("Loading data for visualization...")
    script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else '/home/jovyan/work/thai_shop_reviews/notebooks'
    trends_file = os.path.join(script_dir, "thai_trends_summary.csv")
    leaderboard_file = os.path.join(script_dir, "thai_leaderboard.csv")
    
    if not os.path.exists(trends_file):
        print(f"Error: {trends_file} not found. Run Spark job first.")
        return

    df_trends = pd.read_csv(trends_file)
    df_leader = pd.read_csv(leaderboard_file)

    # 1. Bar Chart: Sentiment by Category
    fig1 = px.bar(df_trends, x="category", y="review_count", color="sentiment",
                 title="Thai Market Sentiment by Category",
                 barmode="group",
                 labels={"review_count": "Number of Reviews", "category": "Product Category"},
                 color_discrete_map={"Positive": "#2ecc71", "Negative": "#e74c3c", "Neutral": "#95a5a6"})
    
    # 2. Sunburst Chart: Category & Sentiment distribution
    fig2 = px.sunburst(df_trends, path=['category', 'sentiment'], values='review_count',
                      title="Market Share Distribution",
                      color='avg_rating', color_continuous_scale='RdYlGn')

    # 3. Horizontal Bar: Leaderboard
    fig3 = px.bar(df_leader, x="positive_reviews", y="product_name", 
                 orientation='h', title="Top 10 Viral Products (Positive Sentiment)",
                 color="avg_rating", color_continuous_scale='Viridis')
    fig3.update_layout(yaxis={'categoryorder':'total ascending'})

    # Save to HTML
    output_html = os.path.join(script_dir, "thai_shop_dashboard.html")
    
    # Combine into a single dashboard using HTML
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write("<html><head><title>Thai Shop Analytics Dashboard</title>")
        f.write("<style>body { font-family: 'Inter', sans-serif; background: #f8f9fa; margin: 20px; }")
        f.write(".chart { background: white; padding: 20px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }</style>")
        f.write("</head><body>")
        f.write("<h1>🇹🇭 Thai Shop Analytics Dashboard</h1>")
        f.write("<div class='chart'>" + fig1.to_html(full_html=False, include_plotlyjs='cdn') + "</div>")
        f.write("<div class='chart'>" + fig2.to_html(full_html=False, include_plotlyjs=False) + "</div>")
        f.write("<div class='chart'>" + fig3.to_html(full_html=False, include_plotlyjs=False) + "</div>")
        f.write("</body></html>")

    print(f"Success! Dashboard generated at {output_html}")

if __name__ == "__main__":
    main()
