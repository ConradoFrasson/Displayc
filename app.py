import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import time
from telemetry_generator import TelemetryGenerator

# Configure page
st.set_page_config(
    page_title="Racing Telemetry Dashboard",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for racing HUD styling
st.markdown("""
<style>
    .main > div {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }
    
    .stMetric {
        background-color: rgba(40, 40, 40, 0.8);
        border: 1px solid #ff4444;
        border-radius: 5px;
        padding: 10px;
        text-align: center;
    }
    
    .stMetric > div > div > div > div {
        font-size: 2rem !important;
        font-weight: bold;
        color: #ffffff;
        text-shadow: 0 0 10px #ff4444;
    }
    
    .tire-indicator {
        background-color: rgba(40, 40, 40, 0.9);
        border: 2px solid #333;
        border-radius: 8px;
        padding: 15px;
        margin: 5px;
        text-align: center;
        min-height: 120px;
    }
    
    .status-led {
        display: inline-block;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        margin: 2px;
        border: 1px solid #333;
    }
    
    .rpm-display {
        font-size: 4rem;
        font-weight: bold;
        color: #ffffff;
        text-align: center;
        text-shadow: 0 0 20px #ff4444;
        background-color: rgba(0, 0, 0, 0.8);
        border: 3px solid #ff4444;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    
    .speed-display {
        font-size: 3rem;
        font-weight: bold;
        color: #ffffff;
        text-align: center;
        text-shadow: 0 0 15px #44ff44;
        background-color: rgba(0, 0, 0, 0.8);
        border: 3px solid #44ff44;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .lap-time-panel {
        background-color: rgba(40, 40, 40, 0.9);
        border: 2px solid #ffaa00;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .warning-indicator {
        background-color: #ff4444;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        margin: 2px;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize telemetry generator
@st.cache_resource
def get_telemetry_generator():
    return TelemetryGenerator()

def format_time(seconds):
    """Format seconds into MM:SS.mmm format"""
    if seconds is None:
        return "--:--.---"
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return f"{minutes}:{remaining_seconds:06.3f}"

def create_tire_status_display(tire_data):
    """Create tire status display with temperature and pressure"""
    tire_html = ""
    
    for position in ['FL', 'FR', 'RL', 'RR']:
        data = tire_data[position]
        temp = data['temperature']
        pressure = data['pressure']
        
        # Color coding based on temperature
        if temp > 100:
            temp_color = "#ff4444"  # Red
        elif temp > 85:
            temp_color = "#ffaa00"  # Yellow
        else:
            temp_color = "#44ff44"  # Green
            
        # Color coding based on pressure
        if pressure < 2.0:
            pressure_color = "#ff4444"  # Red
        elif pressure < 2.1:
            pressure_color = "#ffaa00"  # Yellow
        else:
            pressure_color = "#44ff44"  # Green
        
        tire_html += f"""
        <div class="tire-indicator">
            <h4 style="color: #ffffff; margin-bottom: 10px;">{position}</h4>
            <div style="color: {temp_color}; font-size: 1.2rem; font-weight: bold;">
                {temp:.0f}°C
            </div>
            <div style="color: {pressure_color}; font-size: 1rem; margin-top: 5px;">
                {pressure:.1f} PSI
            </div>
        </div>
        """
    
    return tire_html

def create_status_led_bar(indicators):
    """Create status LED indicator bar"""
    led_html = "<div style='text-align: center; margin: 10px 0;'>"
    
    for indicator in indicators:
        color = indicator['color']
        if color == 'red':
            bg_color = '#ff4444'
        elif color == 'yellow':
            bg_color = '#ffaa00'
        elif color == 'green':
            bg_color = '#44ff44'
        elif color == 'blue':
            bg_color = '#4444ff'
        else:
            bg_color = '#888888'
            
        led_html += f'<span class="status-led" style="background-color: {bg_color};" title="{indicator["status"]}"></span>'
    
    led_html += "</div>"
    return led_html

def create_vertical_gauge(value, min_val, max_val, title, unit, warning_threshold=None, critical_threshold=None):
    """Create a vertical gauge for temperature displays"""
    # Determine color based on thresholds
    if critical_threshold and value >= critical_threshold:
        color = '#ff4444'
    elif warning_threshold and value >= warning_threshold:
        color = '#ffaa00'
    else:
        color = '#44ff44'
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"{title}<br><span style='font-size:0.8em'>{unit}</span>"},
        gauge = {
            'axis': {'range': [None, max_val]},
            'bar': {'color': color, 'thickness': 0.3},
            'bgcolor': "rgba(40,40,40,0.8)",
            'borderwidth': 2,
            'bordercolor': "#333333",
            'steps': [
                {'range': [0, warning_threshold or max_val*0.7], 'color': 'rgba(68, 255, 68, 0.3)'},
                {'range': [warning_threshold or max_val*0.7, critical_threshold or max_val*0.9], 'color': 'rgba(255, 170, 0, 0.3)'},
                {'range': [critical_threshold or max_val*0.9, max_val], 'color': 'rgba(255, 68, 68, 0.3)'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': critical_threshold or max_val
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "white", 'family': "Arial"},
        height=300
    )
    
    return fig

def create_horizontal_soc_gauge(soc_value, power_kw):
    """Create horizontal SOC gauge with power indicator"""
    fig = go.Figure()
    
    # SOC bar
    fig.add_trace(go.Bar(
        x=[soc_value],
        y=['SOC'],
        orientation='h',
        marker=dict(
            color='#44ff44' if soc_value > 30 else '#ffaa00' if soc_value > 15 else '#ff4444',
            line=dict(color='#ffffff', width=2)
        ),
        text=f'{soc_value:.1f}%',
        textposition='inside',
        textfont=dict(color='white', size=16, family='Arial Black'),
        showlegend=False
    ))
    
    fig.update_layout(
        xaxis=dict(
            range=[0, 100],
            showgrid=False,
            showticklabels=True,
            title="State of Charge (%)",
            titlefont=dict(color='white'),
            tickfont=dict(color='white')
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=False
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(40,40,40,0.8)',
        font=dict(color='white'),
        height=150,
        title=dict(
            text=f"SOC: {soc_value:.1f}% | Power: {power_kw:.1f}kW",
            font=dict(color='white', size=14),
            x=0.5
        )
    )
    
    return fig

def main():
    """Main dashboard application"""
    # Initialize session state
    if 'telemetry_gen' not in st.session_state:
        st.session_state.telemetry_gen = get_telemetry_generator()
    
    # Auto-refresh setup
    placeholder = st.empty()
    
    # Main dashboard loop
    with placeholder.container():
        # Get current telemetry data
        telemetry = st.session_state.telemetry_gen.get_all_telemetry()
        
        # Title and status LED bar
        st.markdown("# 🏎️ Racing Telemetry Dashboard")
        st.markdown("### Status Indicators")
        st.markdown(create_status_led_bar(telemetry['status_indicators']), unsafe_allow_html=True)
        
        # Main telemetry display
        col1, col2, col3 = st.columns([2, 2, 2])
        
        with col1:
            # Tire Status Display
            st.markdown("### 🛞 Tire Status")
            tire_display_html = f"""
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                {create_tire_status_display(telemetry['tires'])}
            </div>
            """
            st.markdown(tire_display_html, unsafe_allow_html=True)
            
            # Warning indicators
            st.markdown("### ⚠️ System Warnings")
            warnings = [ind for ind in telemetry['status_indicators'] if ind['color'] in ['red', 'yellow']]
            if warnings:
                warning_html = ""
                for warning in warnings[:5]:  # Show top 5 warnings
                    warning_html += f'<span class="warning-indicator">{warning["status"]}</span>'
                st.markdown(warning_html, unsafe_allow_html=True)
            else:
                st.success("All systems normal")
        
        with col2:
            # RPM and Speed Display
            st.markdown("### 🚗 Engine Data")
            
            # RPM Display
            rpm_html = f"""
            <div class="rpm-display">
                {telemetry['engine']['rpm']:,}
                <div style="font-size: 1rem; color: #cccccc;">RPM</div>
            </div>
            """
            st.markdown(rpm_html, unsafe_allow_html=True)
            
            # Speed Display
            speed_html = f"""
            <div class="speed-display">
                {telemetry['engine']['speed']}
                <div style="font-size: 1rem; color: #cccccc;">Km/h</div>
                <div style="font-size: 0.8rem; color: #ffaa00;">Endurance Mode</div>
            </div>
            """
            st.markdown(speed_html, unsafe_allow_html=True)
            
            # Lap Times Panel
            lap_times = telemetry['lap_times']
            lap_time_html = f"""
            <div class="lap-time-panel">
                <h4 style="color: #ffaa00; margin-bottom: 15px;">⏱️ Lap Times</h4>
                <div style="color: #44ff44;">
                    <strong>Best:</strong> {format_time(lap_times['best_lap_time'])}
                </div>
                <div style="color: #ffffff; margin-top: 8px;">
                    <strong>Previous:</strong> {format_time(lap_times['previous_lap_time'])}
                </div>
                <div style="color: #ffaa00; margin-top: 8px;">
                    <strong>Current:</strong> {format_time(lap_times['current_lap_time'])}
                </div>
                <div style="color: #cccccc; margin-top: 8px; font-size: 0.9rem;">
                    Lap #{lap_times['current_lap']}
                </div>
            </div>
            """
            st.markdown(lap_time_html, unsafe_allow_html=True)
        
        with col3:
            # Temperature Gauges
            st.markdown("### 🌡️ Temperature Monitor")
            
            temp_col1, temp_col2 = st.columns(2)
            with temp_col1:
                battery_gauge = create_vertical_gauge(
                    telemetry['thermal']['battery_temp'], 
                    0, 80, 
                    "BAT", "°C", 
                    warning_threshold=60, 
                    critical_threshold=70
                )
                st.plotly_chart(battery_gauge, use_container_width=True)
            
            with temp_col2:
                motor_gauge = create_vertical_gauge(
                    telemetry['thermal']['motor_temp'], 
                    0, 110, 
                    "MOT", "°C",
                    warning_threshold=90,
                    critical_threshold=100
                )
                st.plotly_chart(motor_gauge, use_container_width=True)
            
            # SOC Gauge
            st.markdown("### 🔋 Power System")
            soc_gauge = create_horizontal_soc_gauge(
                telemetry['power']['soc'], 
                telemetry['power']['power_kw']
            )
            st.plotly_chart(soc_gauge, use_container_width=True)
            
            # Additional system info
            st.markdown(f"""
            <div style="background-color: rgba(40,40,40,0.8); padding: 15px; border-radius: 8px; border: 1px solid #333;">
                <div style="color: #ffffff; font-size: 0.9rem;">
                    <strong>Throttle Position:</strong> {telemetry['engine']['throttle_position']*100:.1f}%<br>
                    <strong>System Time:</strong> {telemetry['timestamp'].strftime('%H:%M:%S')}<br>
                    <strong>Session Status:</strong> <span style="color: #44ff44;">Active</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Auto-refresh every 500ms for real-time feel
    time.sleep(0.5)
    st.rerun()

if __name__ == "__main__":
    main()
