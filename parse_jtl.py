import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import sys
import os

jtl_file = sys.argv[1]
base_name = os.path.splitext(jtl_file)[0]
output_csv = f"{base_name}_aggregate.csv"
output_html = f"{base_name}_aggregate.html"

if not os.path.exists(jtl_file) or os.path.getsize(jtl_file) == 0:
    print(f"❌ Error: '{jtl_file}' is missing or empty.")
    sys.exit(1)

try:
    df = pd.read_csv(jtl_file)

    if 'label' not in df.columns or 'elapsed' not in df.columns:
        print("❌ Error: Required columns not found in JTL CSV.")
        sys.exit(1)

    df['timeStamp'] = pd.to_datetime(df['timeStamp'], unit='ms')
    df['success'] = df['success'].astype(str)

    agg = df.groupby('label').agg(
        samples=('timeStamp', 'count'),
        avg_resp_time=('elapsed', 'mean'),
        min_resp_time=('elapsed', 'min'),
        max_resp_time=('elapsed', 'max'),
        error_pct=('success', lambda x: 100 * (x != 'true').sum() / len(x)),
        start_time=('timeStamp', 'min'),
        end_time=('timeStamp', 'max')
    ).reset_index()

    agg['duration_sec'] = (agg['end_time'] - agg['start_time']).dt.total_seconds().clip(lower=1)
    agg['throughput'] = agg['samples'] / agg['duration_sec']

    agg = agg.drop(columns=['start_time', 'end_time', 'duration_sec'])
    agg = agg.round(2)

    agg.to_csv(output_csv, index=False)
    print(f"✅ Aggregate CSV report saved to: {output_csv}")

    print("\n🐢 Top 3 Slowest Transactions (by avg response time):")
    print(agg.sort_values(by="avg_resp_time", ascending=False).head(3).to_string(index=False))

    # Create bar chart: Avg Response Time
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=agg['label'],
        y=agg['avg_resp_time'],
        marker_color='indianred'
    ))
    fig1.update_layout(
        title="Average Response Time by Transaction",
        xaxis_title="Transaction Label",
        yaxis_title="Avg Response Time (ms)"
    )
    chart1_html = pio.to_html(fig1, full_html=False, include_plotlyjs='cdn')

    # Create bar chart: Error Percentage
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=agg['label'],
        y=agg['error_pct'],
        marker_color='crimson'
    ))
    fig2.update_layout(
        title="Error Percentage by Transaction",
        xaxis_title="Transaction Label",
        yaxis_title="Error %"
    )
    chart2_html = pio.to_html(fig2, full_html=False, include_plotlyjs=False)

    # Aggregate table HTML
    agg_table = agg.sort_values(by="avg_resp_time", ascending=False).to_html(index=False, classes='report', border=0)

    # Final HTML with embedded charts
    html_template = f"""
    <html>
    <head>
        <title>JMeter Aggregate Report</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            h2 {{ color: #333; }}
            table.report {{
                border-collapse: collapse;
                width: 100%;
            }}
            table.report th, table.report td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
            }}
            table.report th {{
                background-color: #f2f2f2;
                color: #333;
            }}
        </style>
    </head>
    <body>
        <h2>📊 JMeter Aggregate Report</h2>
        {agg_table}
        <h2>🚀 Charts</h2>
        {chart1_html}
        <br><br>
        {chart2_html}
    </body>
    </html>
    """

    with open(output_html, 'w') as f:
        f.write(html_template)

    print(f"✅ HTML report with charts saved to: {output_html}")

except Exception as e:
    print(f"❌ Failed to parse and generate report: {e}")
    sys.exit(1)