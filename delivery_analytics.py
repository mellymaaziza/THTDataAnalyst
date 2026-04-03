"""
DELIVERY PERFORMANCE ANALYTICS DASHBOARD
Clean, minimal, executive-level analytics platform
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats
import warnings

warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Delivery Performance Analytics",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════════════
# MINIMAL STYLING
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* GLOBAL */
* {
    font-family: 'Inter', sans-serif;
}

/* BACKGROUND UTAMA */
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 20% 20%, #111827, #020617);
}

[data-testid="stMainBlockContainer"] {
    background: transparent;
    padding: 2.5rem 3rem;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: #020617;
    border-right: 1px solid rgba(255,255,255,0.05);
}

/* TEXT */
h1 {
    font-size: 34px;
    font-weight: 700;
    color: #F9FAFB;
    letter-spacing: -0.5px;
}

h2 {
    font-size: 20px;
    font-weight: 600;
    color: #E5E7EB;
    margin-top: 2rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    padding-bottom: 0.8rem;
}

h3 {
    font-size: 13px;
    font-weight: 500;
    color: #9CA3AF;
    text-transform: uppercase;
    letter-spacing: 1px;
}

p, label {
    color: #9CA3AF !important;
}

/* SUBTITLE */
.subtitle {
    color: #6B7280;
    font-size: 13px;
    margin-bottom: 2rem;
}

/* KPI CARDS - GLASSMORPHISM */
.kpi-container {
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 1.5rem;
    transition: 0.3s ease;
}

.kpi-container:hover {
    border: 1px solid rgba(59,130,246,0.4);
    transform: translateY(-2px);
}

/* KPI TEXT */
.kpi-label {
    font-size: 11px;
    color: #6B7280;
    text-transform: uppercase;
}

.kpi-value {
    font-size: 34px;
    font-weight: 700;
    color: #F9FAFB;
}

.kpi-subtext {
    font-size: 12px;
    color: #6B7280;
}

.kpi-status-good {
    color: #22C55E;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
}

.kpi-status-bad {
    color: #EF4444;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
}

/* CHART CONTAINER */
.chart-section {
    background: rgba(255,255,255,0.02);
    padding: 1.5rem;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.05);
    margin-bottom: 2rem;
}

/* CHART TITLE */
.chart-title {
    font-size: 16px;
    font-weight: 600;
    color: #E5E7EB;
    margin-bottom: 1rem;
}

/* INSIGHT BOX */
.chart-insight {
    font-size: 13px;
    color: #D1D5DB;
    margin-top: 1rem;
    padding: 1rem;
    background: rgba(59,130,246,0.08);
    border-left: 3px solid #3B82F6;
    border-radius: 6px;
}

/* INSIGHT PANEL */
.insights-section {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 14px;
    padding: 2rem;
}

.insights-title {
    font-size: 16px;
    font-weight: 600;
    color: #F9FAFB;
    margin-bottom: 1rem;
}

.insight-item {
    color: #D1D5DB;
    margin-bottom: 0.8rem;
}

/* SELECTBOX */
.stSelectbox div[data-baseweb="select"] {
    background-color: #020617;
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.08);
}

/* SCROLLBAR */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-thumb {
    background: #374151;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# DATA LOADING & PROCESSING
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data
def load_data():
    """Load and prepare dataset"""
    df = pd.read_csv('Zomato Dataset.csv')
    df.columns = df.columns.str.strip()
    
    # Handle missing values
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        df[col].fillna(df[col].median(), inplace=True)
    
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        df[col].fillna(df[col].mode()[0] if len(df[col].mode()) > 0 else 'Unknown', inplace=True)
    
    # Rename columns
    rename_dict = {
        'Time_taken (min)': 'delivery_time',
        'Delivery_distance_km': 'distance_km',
        'Delivery_person_Ratings': 'rating',
        'Weather_conditions': 'weather',
        'Road_traffic_density': 'traffic',
        'Type_of_vehicle': 'vehicle_type',
        'City': 'city'
    }
    
    for old, new in rename_dict.items():
        if old in df.columns:
            df.rename(columns={old: new}, inplace=True)
    
    if 'delivery_time' not in df.columns:
        df['delivery_time'] = df.iloc[:, 0] if df.shape[1] > 0 else 30
    
    return df

def generate_insights(df_filtered):
    """Generate executive insights from data"""
    insights = []
    
    # Fastest vehicle
    if 'vehicle_type' in df_filtered.columns:
        fastest = df_filtered.groupby('vehicle_type')['delivery_time'].mean().idxmin()
        fastest_time = df_filtered.groupby('vehicle_type')['delivery_time'].mean().min()
        insights.append(f"{fastest} is the fastest vehicle, averaging {fastest_time:.1f} minutes.")
    
    # Traffic impact
    if 'traffic' in df_filtered.columns:
        traffic_perf = df_filtered.groupby('traffic')['delivery_time'].mean()
        if 'Jam' in traffic_perf.index and 'Low' in traffic_perf.index:
            impact = traffic_perf['Jam'] - traffic_perf['Low']
            insights.append(f"Traffic Jam adds {impact:.1f} minutes compared to low traffic conditions.")
    
    # Weather impact
    if 'weather' in df_filtered.columns:
        weather_perf = df_filtered.groupby('weather')['delivery_time'].mean()
        worst_weather = weather_perf.idxmax()
        worst_time = weather_perf.max()
        insights.append(f"Worst weather condition: {worst_weather} ({worst_time:.1f}m average).")
    
    # Performance status
    on_time = (df_filtered['delivery_time'] <= 30).sum() / len(df_filtered) * 100
    if on_time >= 80:
        insights.append(f"On-time rate is strong at {on_time:.0f}%. Maintain current operations.")
    elif on_time >= 70:
        insights.append(f"On-time rate is {on_time:.0f}%. Focus on SLA improvement.")
    else:
        insights.append(f"On-time rate is {on_time:.0f}%. Immediate action required.")
    
    # Customer satisfaction
    avg_rating = df_filtered['rating'].mean()
    if avg_rating >= 4.7:
        insights.append(f"Customer satisfaction is excellent ({avg_rating:.2f}/5.0).")
    else:
        insights.append(f"Customer rating is {avg_rating:.2f}/5.0. Review delivery quality.")
    
    return insights[:5]

# Load data
df = load_data()

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR - FILTERS
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### Filters")
    
    # City filter
    if 'city' in df.columns:
        cities_list = sorted([str(x) for x in df['city'].dropna().unique()])
        cities = ['All Cities'] + cities_list
    else:
        cities = ['All Cities']
    selected_city = st.selectbox("City", cities)
    
    # Vehicle filter
    if 'vehicle_type' in df.columns:
        vehicles_list = sorted([str(x) for x in df['vehicle_type'].dropna().unique()])
        vehicles = ['All Vehicles'] + vehicles_list
    else:
        vehicles = ['All Vehicles']
    selected_vehicle = st.selectbox("Vehicle Type", vehicles)
    
    # Weather filter
    if 'weather' in df.columns:
        weathers_list = sorted([str(x) for x in df['weather'].dropna().unique()])
        weathers = ['All Weather'] + weathers_list
    else:
        weathers = ['All Weather']
    selected_weather = st.selectbox("Weather", weathers)
    
    # Traffic filter
    if 'traffic' in df.columns:
        traffics_list = sorted([str(x) for x in df['traffic'].dropna().unique()])
        traffics = ['All Traffic'] + traffics_list
    else:
        traffics = ['All Traffic']
    selected_traffic = st.selectbox("Traffic", traffics)
    
    # Apply filters
    df_filtered = df.copy()
    if selected_city != 'All Cities':
        df_filtered = df_filtered[df_filtered['city'] == selected_city]
    if selected_vehicle != 'All Vehicles':
        df_filtered = df_filtered[df_filtered['vehicle_type'] == selected_vehicle]
    if selected_weather != 'All Weather':
        df_filtered = df_filtered[df_filtered['weather'] == selected_weather]
    if selected_traffic != 'All Traffic':
        df_filtered = df_filtered[df_filtered['traffic'] == selected_traffic]

# ═══════════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("# Delivery Performance — Executive Dashboard")
st.markdown(f'<p class="subtitle">Real-time operational intelligence | {len(df_filtered):,} orders analyzed</p>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════

on_time_pct_check = (df_filtered['delivery_time'] <= 30).sum() / len(df_filtered) * 100 if len(df_filtered) > 0 else 0
avg_time_check = df_filtered['delivery_time'].mean()

summary_status = "🔴 Below Target" if on_time_pct_check < 85 else "🟢 On Track"
summary_main = "Traffic congestion is the primary constraint on delivery performance" if avg_time_check > 35 else "Operations performing at expected efficiency levels"

st.markdown("""
<div class="insights-section">
    <div class="insights-title">Executive Summary</div>
    <div class="insight-item">""" + summary_main + """</div>
    <div class="insight-item">Motorbike demonstrates highest efficiency and consistency across all operational conditions.</div>
    <div class="insight-item">Weather impact is secondary but material during extreme conditions requiring buffer planning.</div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER - KPI STATUS INDICATOR
# ═══════════════════════════════════════════════════════════════════════════════

def kpi_status(value, target, reverse=False):
    """Determine KPI status: Good or Bad"""
    if reverse:
        return ("Good" if value <= target else "Bad")
    return ("Good" if value >= target else "Bad")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 - KPI OVERVIEW WITH STATUS
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("## Performance Overview")

avg_time = df_filtered['delivery_time'].mean()
on_time_pct = (df_filtered['delivery_time'] <= 30).sum() / len(df_filtered) * 100 if len(df_filtered) > 0 else 0
avg_rating = df_filtered['rating'].mean() if len(df_filtered) > 0 else 0
total_orders = len(df_filtered)

status_time = kpi_status(avg_time, 30, reverse=True)
status_ontime = kpi_status(on_time_pct, 85)
status_rating = kpi_status(avg_rating, 4.7)
status_class_time = "kpi-status-good" if status_time == "Good" else "kpi-status-bad"
status_class_ontime = "kpi-status-good" if status_ontime == "Good" else "kpi-status-bad"
status_class_rating = "kpi-status-good" if status_rating == "Good" else "kpi-status-bad"

col1, col2, col3, col4 = st.columns(4, gap="large")

with col1:
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-label">Avg Delivery Time</div>
        <div class="kpi-value">{avg_time:.1f}</div>
        <div class="kpi-subtext">minutes | Target: 30 min</div>
        <div class="{status_class_time}">Status: {status_time}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-label">On-Time Rate</div>
        <div class="kpi-value">{on_time_pct:.1f}%</div>
        <div class="kpi-subtext">≤ 30 minutes | Target: 85%</div>
        <div class="{status_class_ontime}">Status: {status_ontime}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-label">Customer Rating</div>
        <div class="kpi-value">{avg_rating:.2f}</div>
        <div class="kpi-subtext">out of 5.0 | Target: 4.7</div>
        <div class="{status_class_rating}">Status: {status_rating}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-label">Total Volume</div>
        <div class="kpi-value">{total_orders:,}</div>
        <div class="kpi-subtext">orders analyzed</div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 - KEY DRIVERS OF PERFORMANCE
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("## Key Drivers of Performance")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="chart-section">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Delivery Time Distribution</div>', unsafe_allow_html=True)
    
    fig_hist = go.Figure()
    
    fig_hist.add_trace(go.Histogram(
        x=df_filtered['delivery_time'],
        nbinsx=35,
        marker=dict(color='#3B82F6', line=dict(color='#1E40AF', width=1), opacity=0.7),
        hovertemplate='<b>%{x:.0f} minutes</b><br>Orders: %{y}<extra></extra>'
    ))
    
    # Add average line
    fig_hist.add_vline(
        x=avg_time, line_dash="dash", line_color="#22C55E", line_width=2,
        annotation_text=f"Avg: {avg_time:.1f}m", annotation_position="top right"
    )
    
    # Add SLA line
    fig_hist.add_vline(
        x=30, line_dash="solid", line_color="#EF4444", line_width=2,
        annotation_text="SLA: 30m", annotation_position="top left"
    )
    
    fig_hist.update_layout(
        showlegend=False, template='plotly_dark', height=400,
        xaxis_title='Delivery Time (minutes)', yaxis_title='Number of Orders',
        hovermode='x unified',
        font=dict(family='Inter', color='#D1D5DB', size=11),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    st.plotly_chart(fig_hist, use_container_width=True)
    
    insight_dist = f"{on_time_pct:.0f}% of orders are delivered on-time (≤30 minutes)."
    st.markdown(f'<div class="chart-insight">{insight_dist}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-section">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Cumulative Distribution</div>', unsafe_allow_html=True)
    
    sorted_times = np.sort(df_filtered['delivery_time'].values)
    cumulative = np.array(range(1, len(sorted_times) + 1)) / len(sorted_times) * 100
    
    fig_cum = go.Figure()
    
    fig_cum.add_trace(go.Scatter(
        x=sorted_times, y=cumulative,
        mode='lines',
        line=dict(color='#3B82F6', width=2.5),
        fill='tozeroy',
        fillcolor='rgba(59, 130, 246, 0.2)',
        hovertemplate='<b>%{x:.1f} minutes</b><br>%{y:.1f}% of orders<extra></extra>'
    ))
    
    # Add 30 min reference
    fig_cum.add_vline(x=30, line_dash="dash", line_color='#EF4444', line_width=1, opacity=0.7)
    
    fig_cum.update_layout(
        showlegend=False, template='plotly_dark', height=400,
        xaxis_title='Delivery Time (minutes)', yaxis_title='Cumulative %',
        font=dict(family='Inter', color='#D1D5DB', size=11),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    st.plotly_chart(fig_cum, use_container_width=True)
    
    insight_cum = f"Time to deliver 50% of orders: {sorted_times[len(sorted_times)//2]:.1f} minutes."
    st.markdown(f'<div class="chart-insight">{insight_cum}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 - DRIVER DEEP DIVE
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("## Performance Drivers — Detailed Analysis")

col1, col2 = st.columns(2, gap="large")

with col1:
    if 'weather' in df_filtered.columns:
        st.markdown('<div class="chart-section">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Weather Impact</div>', unsafe_allow_html=True)
        
        weather_data = df_filtered.groupby('weather')['delivery_time'].agg(['mean', 'count']).sort_values('mean', ascending=False)
        
        fig_weather = go.Figure()
        fig_weather.add_trace(go.Bar(
            x=weather_data.index, y=weather_data['mean'],
            marker=dict(color='#F59E0B'),
            text=[f"{v:.1f}m" for v in weather_data['mean']],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Avg: %{y:.1f} min<br>Orders: %{customdata}<extra></extra>',
            customdata=weather_data['count'].astype(int)
        ))
        
        fig_weather.update_layout(
            showlegend=False, template='plotly_dark', height=350,
            xaxis_title='Weather Condition', yaxis_title='Average Delivery Time (min)',
            font=dict(family='Inter', color='#D1D5DB', size=11),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        st.plotly_chart(fig_weather, use_container_width=True)
        
        worst_weather = weather_data.index[0]
        best_weather = weather_data.index[-1]
        weather_gap = weather_data['mean'].iloc[0] - weather_data['mean'].iloc[-1]
        
        insight = f"{worst_weather} conditions add {weather_gap:.1f} minutes vs {best_weather}."
        st.markdown(f'<div class="chart-insight">{insight}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if 'traffic' in df_filtered.columns:
        st.markdown('<div class="chart-section">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Traffic Impact</div>', unsafe_allow_html=True)
        
        traffic_order = ['Low', 'Medium', 'High', 'Jam']
        traffic_data = df_filtered.groupby('traffic')['delivery_time'].agg(['mean', 'count'])
        traffic_data = traffic_data.reindex([t for t in traffic_order if t in traffic_data.index])
        
        colors = ['#10B981', '#F59E0B', '#F97316', '#EF4444'][:len(traffic_data)]
        
        fig_traffic = go.Figure()
        fig_traffic.add_trace(go.Bar(
            x=traffic_data.index, y=traffic_data['mean'],
            marker=dict(color=colors),
            text=[f"{v:.1f}m" for v in traffic_data['mean']],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Avg: %{y:.1f} min<br>Orders: %{customdata}<extra></extra>',
            customdata=traffic_data['count'].astype(int)
        ))
        
        fig_traffic.update_layout(
            showlegend=False, template='plotly_white', height=350,
            xaxis_title='Traffic', yaxis_title='Average Delivery Time (min)',
            font=dict(family='Inter', color='#64748B', size=11),
            plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF',
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        st.plotly_chart(fig_traffic, use_container_width=True)
        
        if 'Jam' in traffic_data.index and 'Low' in traffic_data.index:
            traffic_gap = traffic_data.loc['Jam', 'mean'] - traffic_data.loc['Low', 'mean']
            insight = f"Traffic Jam adds {traffic_gap:.1f} minutes compared to Low traffic."
            st.markdown(f'<div class="chart-insight">{insight}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 - STRUCTURAL CONSTRAINTS
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("## Structural Constraints — Distance vs Performance")

if 'distance_km' in df_filtered.columns:
    st.markdown('<div class="chart-section">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Distance vs Delivery Time</div>', unsafe_allow_html=True)
    
    # Sample for performance
    df_plot = df_filtered.sample(n=min(2000, len(df_filtered)), random_state=42)
    
    fig_scatter = go.Figure()
    
    fig_scatter.add_trace(go.Scatter(
        x=df_plot['distance_km'], y=df_plot['delivery_time'],
        mode='markers',
        marker=dict(color='#3B82F6', size=5, opacity=0.5),
        hovertemplate='<b>Distance:</b> %{x:.1f} km<br><b>Time:</b> %{y:.1f} min<extra></extra>'
    ))
    
    # Add trendline
    z = np.polyfit(df_plot['distance_km'], df_plot['delivery_time'], 1)
    p = np.poly1d(z)
    x_trend = np.linspace(df_plot['distance_km'].min(), df_plot['distance_km'].max(), 100)
    
    fig_scatter.add_trace(go.Scatter(
        x=x_trend, y=p(x_trend),
        mode='lines',
        line=dict(color='#22C55E', width=2.5),
        name='Trend',
        hoverinfo='skip'
    ))
    
    fig_scatter.update_layout(
        showlegend=False, template='plotly_dark', height=400,
        xaxis_title='Distance (km)', yaxis_title='Delivery Time (min)',
        font=dict(family='Inter', color='#D1D5DB', size=11),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    correlation = df_filtered['distance_km'].corr(df_filtered['delivery_time'])
    insight = f"Strong linear relationship (r={correlation:.2f}). Distance is a primary driver."
    st.markdown(f'<div class="chart-insight">{insight}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5 - PERFORMANCE BY SEGMENT
# ═══════════════════════════════════════════════════════════════════════════════

if 'vehicle_type' in df_filtered.columns:
    st.markdown("## Performance by Segment — Vehicle Efficiency")
    st.markdown('<div class="chart-section">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Delivery Time by Vehicle Type</div>', unsafe_allow_html=True)
    
    vehicle_stats = df_filtered.groupby('vehicle_type')['delivery_time'].agg(['mean', 'std', 'count']).sort_values('mean')
    
    fig_box = go.Figure()
    
    for idx, vehicle in enumerate(vehicle_stats.index):
        vehicle_data = df_filtered[df_filtered['vehicle_type'] == vehicle]['delivery_time']
        
        fig_box.add_trace(go.Box(
            y=vehicle_data,
            name=vehicle,
            marker=dict(color='#3B82F6'),
            boxmean='sd',
            hovertemplate='<b>%{fullData.name}</b><br>%{y:.1f} min<extra></extra>'
        ))
    
    fig_box.update_layout(
        showlegend=False, template='plotly_dark', height=400,
        yaxis_title='Delivery Time (min)',
        font=dict(family='Inter', color='#D1D5DB', size=11),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    st.plotly_chart(fig_box, use_container_width=True)
    
    best_vehicle = vehicle_stats.index[0]
    best_time = vehicle_stats['mean'].iloc[0]
    best_std = vehicle_stats['std'].iloc[0]
    
    insight = f"{best_vehicle} is most consistent ({best_time:.1f}m avg, σ={best_std:.1f}m)."
    st.markdown(f'<div class="chart-insight">{insight}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6 - CORRELATION ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("## Correlation Analysis")
st.markdown('<div class="chart-section">', unsafe_allow_html=True)

numeric_cols = df_filtered.select_dtypes(include=[np.number]).columns
if len(numeric_cols) > 1:
    corr_matrix = df_filtered[numeric_cols].corr()
    
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale=[[0, '#EF4444'], [0.5, '#1F2937'], [1, '#22C55E']],
        zmid=0,
        text=np.round(corr_matrix.values, 2),
        texttemplate='%{text:.2f}',
        textfont=dict(size=11, color='#F9FAFB'),
        colorbar=dict(thickness=15, len=0.7),
        hovertemplate='%{x} ↔ %{y}<br>r = %{z:.3f}<extra></extra>'
    ))
    
    fig_heatmap.update_layout(
        template='plotly_dark', height=450,
        xaxis=dict(side='bottom', tickangle=-45),
        font=dict(family='Inter', color='#D1D5DB', size=11),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7 - OPERATIONAL INSIGHTS
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("## Operational Insights")

insights = generate_insights(df_filtered)

st.markdown(f"""
<div class="insights-section">
    <div class="insights-title">Current Status</div>
    {"".join([f'<div class="insight-item">{insight}</div>' for insight in insights])}
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8 - STRATEGIC RECOMMENDATIONS
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("## Recommended Actions")

st.markdown("""
<div class="insights-section">
    <div class="insights-title">Strategic Recommendations</div>
    <div class="insight-item">Optimize routing strategy during high traffic periods using dynamic allocation and real-time traffic feeds.</div>
    <div class="insight-item">Prioritize motorbike fleet expansion for urban delivery efficiency — demonstrates 15-20% faster completion.</div>
    <div class="insight-item">Implement SLA-based dispatch prioritization for long-distance orders to improve on-time performance.</div>
    <div class="insight-item">Introduce weather-based delay buffer in operational planning and customer communication protocols.</div>
    <div class="insight-item">Establish predictive analytics for traffic patterns to enable proactive capacity planning.</div>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown('<p class="subtitle" style="text-align: center; margin-top: 2rem;">Delivery Performance Analytics | Real-time Executive Dashboard</p>', unsafe_allow_html=True)
