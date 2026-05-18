import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

def main():
    print("[INFO] Loading Retail Transaction Analytics data...")
    
    # 1. Path Resolution
    script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else '/home/jovyan/work/retail_transaction_analytics/notebooks'
    
    country_file = os.path.join(script_dir, "sales_by_country.csv")
    products_file = os.path.join(script_dir, "top_products.csv")
    customers_file = os.path.join(script_dir, "highest_spending_customers.csv")
    daily_file = os.path.join(script_dir, "daily_sales.csv")
    monthly_file = os.path.join(script_dir, "monthly_sales.csv")
    hourly_file = os.path.join(script_dir, "hourly_pattern.csv")
    suspicious_file = os.path.join(script_dir, "suspicious_transactions.csv")
    suspicious_country_file = os.path.join(script_dir, "suspicious_by_country.csv")
    
    try:
        df_country = pd.read_csv(country_file)
        df_products = pd.read_csv(products_file)
        df_customers = pd.read_csv(customers_file)
        df_daily = pd.read_csv(daily_file)
        df_monthly = pd.read_csv(monthly_file)
        df_hourly = pd.read_csv(hourly_file)
        df_susp_tx = pd.read_csv(suspicious_file)
        df_susp_country = pd.read_csv(suspicious_country_file)
        print("[SUCCESS] Loaded all summary datasets.")
    except Exception as e:
        print(f"[ERROR] Failed to load summary datasets: {e}")
        print("Please ensure process_retail_analytics.py has run successfully first.")
        return

    # 2. Compute Key KPI Metrics
    total_revenue = df_country['TotalSales'].sum()
    total_transactions = df_daily['TransactionLines'].sum()
    uk_sales = df_country[df_country['Country'] == 'United Kingdom']['TotalSales'].values[0]
    uk_percentage = (uk_sales / total_revenue) * 100
    
    # Suspicious transaction statistics
    suspicious_count = df_susp_country['SuspiciousCount'].sum()
    suspicious_pct = (suspicious_count / total_transactions) * 100
    
    top_customer = df_customers.iloc[0]
    top_customer_id = int(top_customer['CustomerID'])
    top_customer_spend = top_customer['TotalSpent']

    # --- PLOTLY CHARTS & SLEEK STYLING ---
    plotly_template = "plotly_dark"
    text_color = "#E2E8F0"
    
    # 1. Geographic Revenue Chart (Horizontal Bar Chart)
    # Exclude United Kingdom for better visual distribution, since UK dominates (~88%)
    df_country_ex_uk = df_country[df_country['Country'] != 'United Kingdom'].head(10)
    fig_country = px.bar(
        df_country_ex_uk.sort_values(by='TotalSales', ascending=True),
        x='TotalSales',
        y='Country',
        orientation='h',
        title="Global Sales Revenue (Excluding United Kingdom)",
        color='TotalSales',
        color_continuous_scale=['#4158D0', '#C850C0', '#FFCC70']
    )
    fig_country.update_layout(
        template=plotly_template,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=text_color, family="Plus Jakarta Sans"),
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(title="Revenue (GBP)", gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(title="", gridcolor="rgba(255,255,255,0.05)")
    )

    # 2. Daily Sales Revenue Trend (Area Chart)
    fig_daily = go.Figure()
    fig_daily.add_trace(go.Scatter(
        x=df_daily['InvoiceDay'],
        y=df_daily['DailySales'],
        mode='lines',
        name='Daily Revenue',
        line=dict(color='#00F2FE', width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 242, 254, 0.1)'
    ))
    fig_daily.update_layout(
        title=dict(text="Daily Revenue Streams (2010 - 2011)", font=dict(size=16, color="#FFFFFF")),
        template=plotly_template,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=text_color, family="Plus Jakarta Sans"),
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(title="Date", showgrid=False),
        yaxis=dict(title="Sales Revenue (GBP)", gridcolor="rgba(255,255,255,0.05)")
    )

    # 3. Top Products by Revenue
    df_top_prod = df_products.head(8)
    fig_products = px.bar(
        df_top_prod,
        x='TotalRevenue',
        y='Description',
        orientation='h',
        title="Top 8 Products by Revenue Generation",
        color='TotalUnitsSold',
        color_continuous_scale=['#FF5E62', '#F3A152', '#2ECC71']
    )
    fig_products.update_layout(
        template=plotly_template,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=text_color, family="Plus Jakarta Sans"),
        coloraxis_showscale=True,
        coloraxis=dict(colorbar=dict(title="Units Sold")),
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(title="Revenue (GBP)", gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(title="")
    )

    # 4. Hourly Transaction Waves (Line chart)
    fig_hourly = go.Figure()
    fig_hourly.add_trace(go.Scatter(
        x=df_hourly['Hour'],
        y=df_hourly['TransactionLines'],
        mode='lines+markers',
        name='Activity Count',
        line=dict(color='#C850C0', width=3, shape='spline'),
        marker=dict(size=8, color='#FF5E62', line=dict(width=1, color='#FFFFFF')),
        fill='tozeroy',
        fillcolor='rgba(200, 80, 192, 0.08)'
    ))
    fig_hourly.update_layout(
        title=dict(text="Hourly Transaction Frequencies (Peak Hours)", font=dict(size=16, color="#FFFFFF")),
        template=plotly_template,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=text_color, family="Plus Jakarta Sans"),
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(title="Hour of Day (24h)", dtick=1, showgrid=False),
        yaxis=dict(title="Invoice Volume", gridcolor="rgba(255,255,255,0.05)")
    )

    # 5. Anomaly Rate by Country (Sleek Horizontal Bar of Suspicious Transaction Counts)
    df_susp_country_filtered = df_susp_country[df_susp_country['SuspiciousCount'] > 0].head(8)
    fig_anomalies = px.bar(
        df_susp_country_filtered,
        x='SuspiciousCount',
        y='Country',
        orientation='h',
        title="High-Risk Transactions Detected by Country",
        color='SuspiciousCount',
        color_continuous_scale=['#FFE000', '#799F0C']
    )
    fig_anomalies.update_layout(
        template=plotly_template,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=text_color, family="Plus Jakarta Sans"),
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(title="Flagged Anomalies Count", gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(title="")
    )

    # --- HTML GENERATION WITH PREMIUM GLASSMORPHISM ---
    output_html = os.path.join(script_dir, "retail_analytics_dashboard.html")
    print(f"[GENERATING] Creating premium glassmorphic HTML dashboard: {output_html}")
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🛍️ Premium Retail Transaction Analytics Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #080710;
            --card-bg: rgba(255, 255, 255, 0.03);
            --card-border: rgba(255, 255, 255, 0.07);
            --neon-blue: #00F2FE;
            --neon-pink: #FF5E62;
            --neon-purple: #C850C0;
            --neon-orange: #FFCC70;
            --text-primary: #FFFFFF;
            --text-secondary: #94A3B8;
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: var(--bg-color);
            background-image: 
                radial-gradient(at 0% 0%, rgba(65, 88, 208, 0.15) 0px, transparent 40%),
                radial-gradient(at 100% 100%, rgba(200, 80, 192, 0.12) 0px, transparent 40%);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 1500px;
            margin: 0 auto;
        }}
        
        header {{
            margin-bottom: 40px;
            text-align: left;
            border-left: 4px solid var(--neon-blue);
            padding-left: 20px;
        }}
        
        header h1 {{
            font-size: 2.5rem;
            font-weight: 800;
            letter-spacing: -0.05em;
            background: linear-gradient(135deg, var(--neon-blue), var(--neon-purple), var(--neon-orange));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }}
        
        header p {{
            color: var(--text-secondary);
            font-size: 1rem;
            font-weight: 400;
        }}
        
        /* Metric Grid */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 20px;
            margin-bottom: 35px;
        }}
        
        .metric-card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 24px;
            padding: 28px;
            backdrop-filter: blur(25px);
            -webkit-backdrop-filter: blur(25px);
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative;
            overflow: hidden;
            box-shadow: 0 10px 30px -15px rgba(0, 0, 0, 0.3);
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
            border-color: rgba(255, 255, 255, 0.15);
            box-shadow: 0 20px 40px -20px rgba(0, 242, 254, 0.2);
        }}
        
        .metric-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 3px;
        }}
        
        .card-revenue::before {{ background: linear-gradient(90deg, var(--neon-blue), var(--neon-purple)); }}
        .card-volume::before {{ background: linear-gradient(90deg, var(--neon-purple), var(--neon-pink)); }}
        .card-uk::before {{ background: linear-gradient(90deg, var(--neon-pink), var(--neon-orange)); }}
        .card-anomalies::before {{ background: linear-gradient(90deg, var(--neon-orange), var(--neon-blue)); }}
        
        .metric-title {{
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 12px;
        }}
        
        .metric-value {{
            font-size: 2.2rem;
            font-weight: 800;
            margin-bottom: 8px;
            letter-spacing: -0.02em;
        }}
        
        .metric-subtext {{
            font-size: 0.8rem;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            gap: 5px;
        }}

        .metric-subtext span.positive {{
            color: #2ECC71;
            font-weight: 600;
        }}
        .metric-subtext span.warning {{
            color: #F1C40F;
            font-weight: 600;
        }}
        
        /* Charts Grid Layout */
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(12, 1fr);
            gap: 25px;
            margin-bottom: 30px;
        }}
        
        .chart-card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 28px;
            padding: 24px;
            backdrop-filter: blur(25px);
            -webkit-backdrop-filter: blur(25px);
            box-shadow: 0 15px 35px -20px rgba(0, 0, 0, 0.4);
            transition: border-color 0.3s ease;
        }}
        
        .chart-card:hover {{
            border-color: rgba(255, 255, 255, 0.12);
        }}
        
        .col-12 {{ grid-column: span 12; }}
        .col-8 {{ grid-column: span 8; }}
        .col-6 {{ grid-column: span 6; }}
        .col-4 {{ grid-column: span 4; }}
        
        @media (max-width: 1024px) {{
            .col-8, .col-6, .col-4 {{
                grid-column: span 12;
            }}
        }}
        
        .chart-container {{
            width: 100%;
            height: 400px;
        }}
    </style>
    <!-- Plotly.js Core -->
    <script src="https://cdn.plot.ly/plotly-2.24.1.min.js"></script>
</head>
<body>
    <div class="container">
        <header>
            <h1>🛍️ Retail Transaction Insights</h1>
            <p>Enterprise Business Intelligence Pipeline powered by HDFS, PySpark, Apache Hive, and Plotly</p>
        </header>
        
        <!-- Metrics Panel -->
        <div class="metrics-grid">
            <div class="metric-card card-revenue">
                <div class="metric-title">Total Processed Revenue</div>
                <div class="metric-value">£{total_revenue:,.2f}</div>
                <div class="metric-subtext">
                    <span class="positive">✔ Cleaned Dataset</span> from HDFS Storage
                </div>
            </div>
            
            <div class="metric-card card-volume">
                <div class="metric-title">Cleaned Sales Transactions</div>
                <div class="metric-value">{total_transactions:,}</div>
                <div class="metric-subtext">
                    <span class="positive">{len(df_daily)} Active Days</span> of recorded sales
                </div>
            </div>
            
            <div class="metric-card card-uk">
                <div class="metric-title">UK Core Market Share</div>
                <div class="metric-value">{uk_percentage:.1f}%</div>
                <div class="metric-subtext">
                    Sales revenue: £{uk_sales:,.2f}
                </div>
            </div>
            
            <div class="metric-card card-anomalies">
                <div class="metric-title">Flagged Risk (Anomalies)</div>
                <div class="metric-value">{suspicious_count:,}</div>
                <div class="metric-subtext">
                    <span class="warning">{suspicious_pct:.2f}% Anomaly Rate</span> (Qty ≥ 500 or Amt ≥ £10k)
                </div>
            </div>
        </div>
        
        <!-- Charts Workspace -->
        <div class="charts-grid">
            <!-- Daily Sales Area Chart -->
            <div class="chart-card col-12">
                <div id="chartDaily" class="chart-container"></div>
            </div>
            
            <!-- Global Distribution (ex UK) -->
            <div class="chart-card col-6">
                <div id="chartCountry" class="chart-container"></div>
            </div>
            
            <!-- Peak Hours Activity -->
            <div class="chart-card col-6">
                <div id="chartHourly" class="chart-container"></div>
            </div>
            
            <!-- Top Product Revenue -->
            <div class="chart-card col-8">
                <div id="chartProducts" class="chart-container"></div>
            </div>
            
            <!-- Suspicious High Risk Distribution -->
            <div class="chart-card col-4">
                <div id="chartAnomalies" class="chart-container"></div>
            </div>
        </div>
    </div>
    
    <script>
        // Inject Plotly JSON graphs directly
        const graphDaily = {fig_daily.to_json()};
        const graphCountry = {fig_country.to_json()};
        const graphHourly = {fig_hourly.to_json()};
        const graphProducts = {fig_products.to_json()};
        const graphAnomalies = {fig_anomalies.to_json()};
        
        // Render plots
        Plotly.newPlot('chartDaily', graphDaily.data, graphDaily.layout, {{responsive: true}});
        Plotly.newPlot('chartCountry', graphCountry.data, graphCountry.layout, {{responsive: true}});
        Plotly.newPlot('chartHourly', graphHourly.data, graphHourly.layout, {{responsive: true}});
        Plotly.newPlot('chartProducts', graphProducts.data, graphProducts.layout, {{responsive: true}});
        Plotly.newPlot('chartAnomalies', graphAnomalies.data, graphAnomalies.layout, {{responsive: true}});
    </script>
</body>
</html>
"""
    
    # Save the file
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"[SUCCESS] Dashboard created successfully! Saved to: {output_html}")

if __name__ == "__main__":
    main()
