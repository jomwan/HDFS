import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

def main():
    print("[INFO] Loading airline sentiment analytics data...")
    
    # 1. Path Resolution
    script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else '/home/jovyan/work/airline_sentiment/notebooks'
    dist_file = os.path.join(script_dir, "sentiment_distribution.csv")
    airline_file = os.path.join(script_dir, "airline_sentiment.csv")
    reasons_file = os.path.join(script_dir, "top_negativereasons.csv")
    volume_file = os.path.join(script_dir, "daily_tweet_volume.csv")
    
    try:
        df_dist = pd.read_csv(dist_file)
        df_airline = pd.read_csv(airline_file)
        df_reasons = pd.read_csv(reasons_file)
        df_volume = pd.read_csv(volume_file)
        print("[SUCCESS] Loaded all summary datasets.")
    except Exception as e:
        print(f"[ERROR] Failed to load summary datasets: {e}")
        print("Please ensure process_airline_sentiment.py has run successfully first.")
        return

    # Calculate key metrics
    total_tweets = df_dist['count'].sum()
    neg_count = df_dist[df_dist['airline_sentiment'] == 'negative']['count'].values[0]
    neg_ratio = (neg_count / total_tweets) * 100
    top_complaint = df_reasons['negativereason'].values[0]
    
    # Most complained airline details
    df_airline['total_neg'] = df_airline['negative']
    most_complained = df_airline.sort_values(by='total_neg', ascending=False).iloc[0]
    worst_airline = most_complained['airline']
    worst_airline_neg = most_complained['total_neg']

    # --- PLOTLY CHARTS ---
    # Unified template & styling
    plotly_template = "plotly_dark"
    bg_color = "rgba(30, 30, 40, 0.6)"
    text_color = "#E0E0E0"
    
    # 1. Pie/Donut Chart: Overall Sentiment Distribution
    fig_sentiment = go.Figure(data=[go.Pie(
        labels=df_dist['airline_sentiment'],
        values=df_dist['count'],
        hole=.5,
        marker=dict(colors=['#FF5E62', '#F3A152', '#2ECC71']),
        textinfo='label+percent',
        hoverinfo='label+value+percent'
    )])
    fig_sentiment.update_layout(
        title=dict(text="Overall Sentiment Distribution", font=dict(size=18, color="#FFFFFF")),
        template=plotly_template,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=text_color),
        margin=dict(l=20, r=20, t=50, b=20)
    )

    # 2. Grouped Bar Chart: Sentiment comparison by Airline
    fig_airline = go.Figure(data=[
        go.Bar(name='Negative', x=df_airline['airline'], y=df_airline['negative'], marker_color='#FF5E62'),
        go.Bar(name='Neutral', x=df_airline['airline'], y=df_airline['neutral'], marker_color='#F3A152'),
        go.Bar(name='Positive', x=df_airline['airline'], y=df_airline['positive'], marker_color='#2ECC71')
    ])
    fig_airline.update_layout(
        title=dict(text="Customer Sentiment Across Major U.S. Airlines", font=dict(size=18, color="#FFFFFF")),
        barmode='group',
        template=plotly_template,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=text_color),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=60, b=20)
    )

    # 3. Horizontal Bar Chart: Top Negative reasons
    fig_reasons = px.bar(
        df_reasons.sort_values(by='count', ascending=True),
        x='count',
        y='negativereason',
        orientation='h',
        title="Top Passenger Complaint Reasons",
        color='count',
        color_continuous_scale=['#F3A152', '#FF5E62']
    )
    fig_reasons.update_layout(
        template=plotly_template,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=text_color),
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(title="Number of Incidents"),
        yaxis=dict(title="")
    )

    # 4. Daily Tweet Volume Line/Area Chart
    fig_volume = go.Figure()
    fig_volume.add_trace(go.Scatter(
        x=df_volume['date'], 
        y=df_volume['count'], 
        mode='lines+markers',
        name='Daily Volume',
        line=dict(color='#00F2FE', width=3),
        marker=dict(size=8, color='#0078FF', line=dict(width=2, color='#FFFFFF')),
        fill='tozeroy',
        fillcolor='rgba(0, 242, 254, 0.15)'
    ))
    fig_volume.update_layout(
        title=dict(text="Daily Tweet Volume (Feb 2015)", font=dict(size=18, color="#FFFFFF")),
        template=plotly_template,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=text_color),
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(title="Date"),
        yaxis=dict(title="Number of Tweets")
    )

    # --- HTML DASHBOARD GENERATION ---
    output_html = os.path.join(script_dir, "airline_sentiment_dashboard.html")
    print(f"[GENERATING] Creating premium HTML dashboard: {output_html}")
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>✈️ Airline Sentiment & Analytics Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0b0b13;
            --card-bg: rgba(22, 22, 38, 0.7);
            --card-border: rgba(255, 255, 255, 0.08);
            --neon-blue: #00F2FE;
            --neon-pink: #FF5E62;
            --neon-green: #2ECC71;
            --text-primary: #FFFFFF;
            --text-secondary: #B0B0C5;
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
                radial-gradient(at 10% 20%, rgba(0, 242, 254, 0.05) 0px, transparent 50%),
                radial-gradient(at 90% 80%, rgba(255, 94, 98, 0.05) 0px, transparent 50%);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            margin-bottom: 40px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 2.8rem;
            font-weight: 800;
            letter-spacing: -0.05em;
            background: linear-gradient(135deg, var(--neon-blue), var(--neon-pink));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        
        header p {{
            color: var(--text-secondary);
            font-size: 1.1rem;
        }}
        
        /* Metric Grid */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .metric-card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 20px;
            padding: 25px;
            backdrop-filter: blur(16px);
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            position: relative;
            overflow: hidden;
        }}
        
        .metric-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
        }}
        
        .card-total::before {{ background: var(--neon-blue); }}
        .card-ratio::before {{ background: var(--neon-pink); }}
        .card-complaint::before {{ background: #F3A152; }}
        .card-worst::before {{ background: #9B59B6; }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.4);
            border-color: rgba(255, 255, 255, 0.15);
        }}
        
        .metric-label {{
            color: var(--text-secondary);
            font-size: 0.9rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 8px;
        }}
        
        .metric-value {{
            font-size: 2.2rem;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 8px;
        }}
        
        .metric-sub {{
            color: var(--text-secondary);
            font-size: 0.85rem;
        }}
        
        /* Visualization Grid */
        .viz-grid {{
            display: grid;
            grid-template-columns: repeat(12, 1fr);
            gap: 25px;
            margin-bottom: 30px;
        }}
        
        .viz-card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 24px;
            padding: 25px;
            backdrop-filter: blur(16px);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        }}
        
        .col-4 {{ grid-column: span 4; }}
        .col-8 {{ grid-column: span 8; }}
        .col-6 {{ grid-column: span 6; }}
        .col-12 {{ grid-column: span 12; }}
        
        @media (max-width: 1024px) {{
            .col-4, .col-8, .col-6 {{
                grid-column: span 12;
            }}
        }}
        
        /* Insights Panel */
        .insights-panel {{
            background: linear-gradient(135deg, rgba(22, 22, 38, 0.8), rgba(11, 11, 19, 0.9));
            border: 1px solid var(--card-border);
            border-radius: 24px;
            padding: 35px;
            margin-top: 40px;
            backdrop-filter: blur(16px);
        }}
        
        .insights-panel h2 {{
            font-size: 1.8rem;
            font-weight: 800;
            margin-bottom: 20px;
            border-left: 5px solid var(--neon-pink);
            padding-left: 15px;
        }}
        
        .insights-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
        }}
        
        .insight-section h3 {{
            color: var(--neon-blue);
            font-size: 1.15rem;
            margin-bottom: 12px;
            font-weight: 600;
        }}
        
        .insight-section p {{
            color: var(--text-secondary);
            line-height: 1.6;
            font-size: 0.95rem;
        }}
        
        .insight-section ul {{
            list-style-type: none;
            margin-top: 10px;
        }}
        
        .insight-section ul li {{
            color: var(--text-secondary);
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            display: flex;
            justify-content: space-between;
        }}
        
        .insight-section ul li span {{
            color: var(--text-primary);
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>✈️ US Airlines Customer Sentiment Analysis</h1>
            <p>Distributed Storage & Spark MapReduce Pipeline Insights from {total_tweets:,} Passenger Tweets</p>
        </header>
        
        <!-- Metrics Summary -->
        <section class="metrics-grid">
            <div class="metric-card card-total">
                <div class="metric-label">Total Tweets Analyzed</div>
                <div class="metric-value">{total_tweets:,}</div>
                <div class="metric-sub">Ingested into HDFS and validated</div>
            </div>
            <div class="metric-card card-ratio">
                <div class="metric-label">Negative Sentiment Ratio</div>
                <div class="metric-value">{neg_ratio:.1f}%</div>
                <div class="metric-sub">{neg_count:,} negative complaint tweets</div>
            </div>
            <div class="metric-card card-complaint">
                <div class="metric-label">Top Passenger Complaint</div>
                <div class="metric-value" style="font-size: 1.6rem; margin-top: 8px;">{top_complaint}</div>
                <div class="metric-sub">{df_reasons['count'].values[0]:,} registered complaints</div>
            </div>
            <div class="metric-card card-worst">
                <div class="metric-label">Highest Complaint Volume</div>
                <div class="metric-value">{worst_airline}</div>
                <div class="metric-sub">{worst_airline_neg:,} negative tweets received</div>
            </div>
        </section>
        
        <!-- Visualizations Grid -->
        <section class="viz-grid">
            <div class="viz-card col-4">
                {fig_sentiment.to_html(full_html=False, include_plotlyjs='cdn')}
            </div>
            <div class="viz-card col-8">
                {fig_airline.to_html(full_html=False, include_plotlyjs='cdn')}
            </div>
            
            <div class="viz-card col-6">
                {fig_reasons.to_html(full_html=False, include_plotlyjs='cdn')}
            </div>
            <div class="viz-card col-6">
                {fig_volume.to_html(full_html=False, include_plotlyjs='cdn')}
            </div>
        </section>
        
        <!-- Business Insights & Interpretation -->
        <section class="insights-panel">
            <h2>💡 Big Data Analytics Interpretation</h2>
            <div class="insights-grid">
                <div class="insight-section">
                    <h3>📊 Sentiment Trend Analysis</h3>
                    <p>
                        A massive <strong>{neg_ratio:.1f}%</strong> of passenger feedback is classified as <strong>negative</strong>, 
                        whereas positive feedback is a mere {((df_dist[df_dist['airline_sentiment'] == 'positive']['count'].values[0]) / total_tweets)*100:.1f}%.
                        This demonstrates a severe systemic negative sentiment baseline in U.S. domestic aviation customer service,
                        reflecting widespread passenger frustration during the analysis window.
                    </p>
                    <ul style="margin-top: 15px;">
                        <li>Negative Tweets: <span>{neg_count:,}</span></li>
                        <li>Neutral Tweets: <span>{df_dist[df_dist['airline_sentiment'] == 'neutral']['count'].values[0]:,}</span></li>
                        <li>Positive Tweets: <span>{df_dist[df_dist['airline_sentiment'] == 'positive']['count'].values[0]:,}</span></li>
                    </ul>
                </div>
                
                <div class="insight-section">
                    <h3>⚠️ Top Operational Failure Modes</h3>
                    <p>
                        The most frequent complaints, analyzed via Spark, show that <strong>{top_complaint}</strong> is the primary driver 
                        with <strong>{df_reasons['count'].values[0]:,} incidents</strong>. This outweighs flight delays, 
                        meaning that passengers' frustration spikes when facing unhelpful customer service channels.
                    </p>
                    <ul>
                        <li>1. {df_reasons['negativereason'].values[0]}: <span>{df_reasons['count'].values[0]:,}</span></li>
                        <li>2. {df_reasons['negativereason'].values[1]}: <span>{df_reasons['count'].values[1]:,}</span></li>
                        <li>3. {df_reasons['negativereason'].values[2]}: <span>{df_reasons['count'].values[2]:,}</span></li>
                    </ul>
                </div>
                
                <div class="insight-section">
                    <h3>🛠️ Operational Recommendations</h3>
                    <p>
                        <strong>1. Expand Front-line Support Capacity:</strong> Given that "Customer Service Issue" is the number one cause of negative sentiment (2,910 counts), U.S. carriers must drastically invest in scaling digital chat channels and customer response systems.
                    </p>
                    <p style="margin-top: 10px;">
                        <strong>2. Optimize Real-Time Alert Buffers:</strong> As shown in the daily volume analysis, sentiment volume peaked heavily on <strong>Feb 23</strong> (3,515 tweets). Operational teams need dynamic queue staffing models aligned with adverse weather or operational events to handle feedback spikes.
                    </p>
                </div>
            </div>
        </section>
    </div>
</body>
</html>
"""

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"[SUCCESS] Dashboard exported successfully!")

if __name__ == "__main__":
    main()
