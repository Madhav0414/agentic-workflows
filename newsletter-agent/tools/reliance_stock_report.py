#!/usr/bin/env python3
"""
Generate a PDF report on Reliance Industries Limited (RELIANCE.NS) stock performance
for the last 5 days.
"""

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import sys

def fetch_reliance_data():
    """Fetch last 5 days of Reliance stock data."""
    try:
        # Fetch last 10 days to ensure we get 5 trading days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=10)

        df = yf.download("RELIANCE.NS", start=start_date, end=end_date, progress=False)

        # Flatten MultiIndex columns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]

        # Get last 5 rows (5 trading days)
        df = df.tail(5)

        if len(df) == 0:
            print("Error: No data retrieved for RELIANCE.NS")
            sys.exit(1)

        return df, 'Reliance Industries Limited'
    except Exception as e:
        print(f"Error fetching data: {e}")
        sys.exit(1)

def create_price_chart(df):
    """Create a price chart and return as image bytes."""
    fig, ax = plt.subplots(figsize=(10, 5))

    x_range = list(range(len(df)))
    close_vals = [float(x) for x in df['Close'].values]
    open_vals = [float(x) for x in df['Open'].values]
    high_vals = [float(x) for x in df['High'].values]
    low_vals = [float(x) for x in df['Low'].values]

    ax.plot(x_range, close_vals, marker='o', linewidth=2.5, color='#1E1B4B', label='Close Price', markersize=8)
    ax.plot(x_range, high_vals, linestyle='--', linewidth=1, color='#818CF8', alpha=0.6, label='High')
    ax.plot(x_range, low_vals, linestyle='--', linewidth=1, color='#EF4444', alpha=0.6, label='Low')

    ax.set_title('Reliance Industries Limited - 5 Day Price Chart', fontsize=14, fontweight='bold')
    ax.set_xlabel('Date', fontsize=10)
    ax.set_ylabel('Price (INR)', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Format x-axis with dates
    date_labels = [d.strftime('%m-%d') for d in df.index]
    ax.set_xticks(x_range)
    ax.set_xticklabels(date_labels, rotation=45)

    plt.tight_layout()

    # Save to bytes
    img_bytes = BytesIO()
    fig.savefig(img_bytes, format='png', dpi=100)
    img_bytes.seek(0)
    plt.close()

    return img_bytes

def create_volume_chart(df):
    """Create a volume chart and return as image bytes."""
    fig, ax = plt.subplots(figsize=(10, 4))

    x_range = range(len(df))
    colors_list = ['#4F46E5' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#EF4444'
                   for i in range(len(df))]

    ax.bar(x_range, df['Volume'].values, color=colors_list, alpha=0.7)
    ax.set_title('Trading Volume - 5 Days', fontsize=12, fontweight='bold')
    ax.set_xlabel('Date', fontsize=10)
    ax.set_ylabel('Volume', fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')

    # Format x-axis with dates
    date_labels = [d.strftime('%m-%d') for d in df.index]
    plt.xticks(x_range, date_labels, rotation=45)

    plt.tight_layout()

    img_bytes = BytesIO()
    fig.savefig(img_bytes, format='png', dpi=100)
    img_bytes.seek(0)
    plt.close()

    return img_bytes

def calculate_metrics(df):
    """Calculate performance metrics."""
    start_price = df['Open'].iloc[0]
    end_price = df['Close'].iloc[-1]
    high_5d = df['High'].max()
    low_5d = df['Low'].min()
    avg_volume = df['Volume'].mean()

    change = end_price - start_price
    change_pct = (change / start_price) * 100

    return {
        'start_price': start_price,
        'end_price': end_price,
        'change': change,
        'change_pct': change_pct,
        'high_5d': high_5d,
        'low_5d': low_5d,
        'avg_volume': avg_volume,
    }

def create_pdf_report(output_path=".tmp/reliance_report.pdf"):
    """Generate the PDF report."""

    # Fetch data
    df, company_name = fetch_reliance_data()
    metrics = calculate_metrics(df)

    # Create charts
    price_chart = create_price_chart(df)
    volume_chart = create_volume_chart(df)

    # Create PDF
    pdf = SimpleDocTemplate(output_path, pagesize=letter,
                            rightMargin=0.75*inch, leftMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)

    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#0F0C29'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#1E1B4B'),
        spaceAfter=10,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )

    # Title
    story.append(Paragraph("Reliance Industries Limited", title_style))
    story.append(Paragraph(f"5-Day Stock Performance Report", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
                          styles['Normal']))
    story.append(Spacer(1, 0.3*inch))

    # Metrics summary
    story.append(Paragraph("Performance Summary", heading_style))

    metrics_data = [
        ['Metric', 'Value'],
        ['Opening Price (5d start)', f"₹{metrics['start_price']:.2f}"],
        ['Closing Price (5d end)', f"₹{metrics['end_price']:.2f}"],
        ['5-Day Change', f"₹{metrics['change']:.2f} ({metrics['change_pct']:+.2f}%)"],
        ['5-Day High', f"₹{metrics['high_5d']:.2f}"],
        ['5-Day Low', f"₹{metrics['low_5d']:.2f}"],
        ['Avg Daily Volume', f"{metrics['avg_volume']:,.0f}"],
    ]

    metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F0C29')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))

    story.append(metrics_table)
    story.append(Spacer(1, 0.3*inch))

    # Price chart
    story.append(Paragraph("Price Trend", heading_style))
    price_img = Image(price_chart, width=6*inch, height=3*inch)
    story.append(price_img)
    story.append(Spacer(1, 0.2*inch))

    # Volume chart
    story.append(Paragraph("Trading Volume", heading_style))
    volume_img = Image(volume_chart, width=6*inch, height=2.4*inch)
    story.append(volume_img)
    story.append(Spacer(1, 0.2*inch))

    # Daily breakdown
    story.append(Paragraph("Daily Breakdown", heading_style))

    daily_data = [['Date', 'Open', 'High', 'Low', 'Close', 'Change %']]
    for idx, row in df.iterrows():
        daily_data.append([
            idx.strftime('%m-%d-%Y'),
            f"₹{row['Open']:.2f}",
            f"₹{row['High']:.2f}",
            f"₹{row['Low']:.2f}",
            f"₹{row['Close']:.2f}",
            f"{((row['Close']-row['Open'])/row['Open']*100):+.2f}%"
        ])

    daily_table = Table(daily_data, colWidths=[1.2*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.8*inch])
    daily_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E1B4B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F3F4F6')),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))

    story.append(daily_table)

    # Build PDF
    pdf.build(story)

    print(f"[OK] Reliance stock report generated: {output_path}")
    print(f"     Report period: {df.index[0].strftime('%B %d, %Y')} to {df.index[-1].strftime('%B %d, %Y')}")
    print(f"     5-Day change: INR {metrics['change']:.2f} ({metrics['change_pct']:+.2f}%)")

if __name__ == "__main__":
    create_pdf_report()
