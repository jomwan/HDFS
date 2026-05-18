import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

def main():
    print("Loading fraud statistics...")
    script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else '/home/jovyan/work/fraud_detection/notebooks'
    summary_file = os.path.join(script_dir, "fraud_summary.csv")
    alerts_file = os.path.join(script_dir, "fraud_alerts.csv")
    
    try:
        df_summary = pd.read_csv(summary_file)
        df_alerts = pd.read_csv(alerts_file)
    except:
        print("Error: Summary files not found. Run the Spark job first.")
        return

    # 1. Bar Chart: Total Transactions vs Fraudulent ones
    fig1 = go.Figure(data=[
        go.Bar(name='Total Transactions', x=df_summary['type'], y=df_summary['total_trans'], marker_color='#3498db'),
        go.Bar(name='Fraudulent', x=df_summary['type'], y=df_summary['fraud_count'], marker_color='#e74c3c')
    ])
    fig1.update_layout(title="Transaction Volume vs Fraud Incidents", barmode='group', yaxis_type="log")

    # 2. Pie Chart: Fraud Share by Type
    fig2 = px.pie(df_summary, values='fraud_count', names='type', 
                  title="Fraud Distribution by Transaction Type",
                  color_discrete_sequence=px.colors.sequential.Reds_r)

    # 3. Scatter Plot: Fraud Amount vs Step (Time)
    fig3 = px.scatter(df_alerts, x="step", y="amount", size="amount", color="is_suspicious",
                     title="Confirmed Fraudulent Transactions over Time",
                     labels={"step": "Time Unit (Hour)", "amount": "Transaction Amount"},
                     hover_data=["nameOrig", "nameDest"])

    # Save Dashboard
    output_html = os.path.join(script_dir, "fraud_dashboard.html")
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write("<html><head><title>Fraud Detection Dashboard</title>")
        f.write("<style>body { font-family: 'Segoe UI', sans-serif; background: #1a1a1a; color: white; margin: 30px; }")
        f.write(".chart { background: #2d2d2d; padding: 20px; border-radius: 15px; margin-bottom: 25px; border: 1px solid #444; }</style>")
        f.write("</head><body>")
        f.write("<h1>🛡️ PaySim Fraud Detection Dashboard</h1>")
        f.write("<p>Analyzing synthetic financial transactions for anomalous patterns.</p>")
        f.write("<div class='chart'>" + fig1.to_html(full_html=False, include_plotlyjs='cdn') + "</div>")
        f.write("<div class='chart'>" + fig2.to_html(full_html=False, include_plotlyjs=False) + "</div>")
        f.write("<div class='chart'>" + fig3.to_html(full_html=False, include_plotlyjs=False) + "</div>")
        f.write("</body></html>")

    print(f"Dashboard successfully generated at {output_html}")

if __name__ == "__main__":
    main()
