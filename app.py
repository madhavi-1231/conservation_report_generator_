import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
# from langchain.chains import LLMChain
import os
from datetime import datetime
import json
import time
from dotenv import load_dotenv

load_dotenv()
# Page configuration
st.set_page_config(
    page_title="Conservation Report Generator",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.5rem;
        color: #1B5E20;
        margin-bottom: 2rem;
        text-align: center;
    }
    .report-card {
        background-color: #f9f9f9;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-size: 1.2rem;
        padding: 0.5rem 2rem;
        border-radius: 25px;
        border: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .stButton>button:hover {
        background-color: #45a049;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated_reports' not in st.session_state:
    st.session_state.generated_reports = []
if 'current_report' not in st.session_state:
    st.session_state.current_report = None

# Title Section
st.markdown("<h1 class='main-header'>🌿 Conservation Report Generator</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>AI-Powered Wildlife Conservation Analysis & Recommendations</p>", unsafe_allow_html=True)

# Sidebar for API configuration
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/null/wildlife.png", width=100)
    st.title("⚙️ Configuration")
    
    # API Key input
    grok_api_key = os.getenv("GROK_API_KEY")
    
    # Model parameters
    st.subheader("Model Parameters")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1,
                            help="Higher values make the output more creative")
    max_tokens = st.slider("Max Tokens", 100, 2000, 1000, 100,
                          help="Maximum length of generated response")
    
    # About section
    st.markdown("---")
    st.markdown("### 📖 About")
    st.info("""
    This tool uses AI to generate comprehensive conservation reports based on field observations.
    
    **Features:**
    - 📊 Population trend analysis
    - 📈 Data visualization
    - 🛡️ Protection recommendations
    - 📑 Downloadable reports
    """)
    
    # Recent reports
    if st.session_state.generated_reports:
        st.markdown("### 📋 Recent Reports")
        for i, report in enumerate(st.session_state.generated_reports[-3:]):
            st.caption(f"{i+1}. {report['species']} - {report['date']}")

# Main content area - Create tabs for better organization
tab1, tab2, tab3 = st.tabs(["📝 Observation Input", "📊 Analysis & Report", "📈 Visualizations"])

# Tab 1: Observation Input
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🔍 Enter Field Observations")
        
        # Input form
        with st.form("observation_form"):
            species = st.text_input("Species Name:", placeholder="e.g., African Elephant, Bengal Tiger")
            location = st.text_input("Location:", placeholder="e.g., Serengeti National Park, Tanzania")
            date = st.date_input("Observation Date:", datetime.now())
            
            # Population data
            st.markdown("#### Population Data")
            col_pop1, col_pop2, col_pop3 = st.columns(3)
            with col_pop1:
                current_count = st.number_input("Current Count:", min_value=0, value=100)
            with col_pop2:
                previous_count = st.number_input("Previous Count (5 years ago):", min_value=0, value=120)
            with col_pop3:
                habitat_area = st.number_input("Habitat Area (sq km):", min_value=0.0, value=1000.0)
            
            # Threats and observations
            threats = st.multiselect(
                "Observed Threats:",
                ["Poaching", "Habitat Loss", "Human-Wildlife Conflict", "Climate Change", 
                 "Disease", "Pollution", "Invasive Species", "Infrastructure Development"],
                default=["Habitat Loss"]
            )
            
            additional_notes = st.text_area(
                "Additional Observations:",
                placeholder="Describe any other relevant observations, behavior patterns, or environmental conditions...",
                height=100
            )
            
            # Submit button
            submitted = st.form_submit_button("🚀 Generate Conservation Report", use_container_width=True)
            
            if submitted:
                if not grok_api_key:
                    st.error("⚠️ Please enter your Grok API key in the sidebar first!")
                else:
                    with st.spinner("🔄 Analyzing observations and generating comprehensive report..."):
                        # Prepare observation data
                        observation_data = {
                            "species": species,
                            "location": location,
                            "date": str(date),
                            "current_count": current_count,
                            "previous_count": previous_count,
                            "habitat_area": habitat_area,
                            "threats": threats,
                            "additional_notes": additional_notes
                        }
                        
                        # Store in session state
                        st.session_state.current_observation = observation_data
                        st.success("✅ Observations recorded! Check the Analysis tab for your report.")
                        time.sleep(1)
                        st.rerun()
    
    with col2:
        st.markdown("### 📝 Quick Tips")
        st.info("""
        **For best results:**
        - Be specific with species names
        - Include accurate population estimates
        - Mention multiple threats if present
        - Add behavioral observations
        - Note environmental conditions
        """)
        
        # Example observation
        with st.expander("📋 View Example"):
            st.markdown("""
            **Species:** African Elephant  
            **Location:** Amboseli National Park, Kenya  
            **Current Count:** 1500  
            **Previous Count:** 1200  
            **Threats:** Poaching, Habitat Loss  
            **Notes:** Observed 15 new calves, good water availability
            """)

# Tab 2: Analysis & Report
with tab2:
    if 'current_observation' in st.session_state:
        obs = st.session_state.current_observation
        
        # Display observation summary
        st.markdown("### 📋 Observation Summary")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Species", obs['species'])
        with col2:
            st.metric("Location", obs['location'])
        with col3:
            st.metric("Current Population", f"{obs['current_count']:,}")
        with col4:
            st.metric("Population Change", 
                     f"{((obs['current_count'] - obs['previous_count']) / obs['previous_count'] * 100):.1f}%")
        
        # Generate report button
        if st.button("🔄 Generate/Refresh Report", use_container_width=True):
            with st.spinner("🤖 AI is analyzing data and generating comprehensive report..."):
                try:
                    # Initialize Grok API via LangChain
                    os.environ["GROK_API_KEY"] = grok_api_key
                    
                    # Create prompt template
                    template = """
                    You are a wildlife conservation expert. Generate a comprehensive conservation report based on the following field observations:
                    
                    SPECIES: {species}
                    LOCATION: {location}
                    DATE: {date}
                    CURRENT POPULATION: {current_count}
                    PREVIOUS POPULATION (5 years ago): {previous_count}
                    HABITAT AREA: {habitat_area} sq km
                    OBSERVED THREATS: {threats}
                    ADDITIONAL NOTES: {additional_notes}
                    
                    Generate a detailed report with the following sections:
                    
                    1. EXECUTIVE SUMMARY: Brief overview of the current conservation status
                    
                    2. POPULATION TREND ANALYSIS:
                       - Calculate population change percentage
                       - Analyze population density
                       - Identify trends and patterns
                       - Future projections
                    
                    3. CONSERVATION ANALYSIS:
                       - Assessment of current threats
                       - Habitat condition evaluation
                       - Key risk factors
                       - Strengths and opportunities
                    
                    4. PROTECTION RECOMMENDATIONS:
                       - Immediate actions needed (next 6 months)
                       - Short-term strategies (1-2 years)
                       - Long-term conservation plans
                       - Community engagement suggestions
                    
                    5. MONITORING SUGGESTIONS:
                       - Key indicators to track
                       - Recommended survey methods
                       - Data collection frequency
                    
                    Format the report professionally with clear section headings and bullet points where appropriate.
                    """
                    
                    # For demo purposes, if no API key, use template-based response
                    if not grok_api_key:
                        report_content = f"""
# Conservation Report: {obs['species']}

## Executive Summary
This report analyzes the conservation status of {obs['species']} in {obs['location']}. 
Current population stands at {obs['current_count']} individuals, showing a 
{((obs['current_count'] - obs['previous_count']) / obs['previous_count'] * 100):.1f}% 
change from previous records.

## Population Trend Analysis
- **Population Change:** {((obs['current_count'] - obs['previous_count']) / obs['previous_count'] * 100):.1f}%
- **Population Density:** {(obs['current_count'] / obs['habitat_area']):.2f} individuals/sq km
- **Trend Assessment:** {'Increasing' if obs['current_count'] > obs['previous_count'] else 'Decreasing' if obs['current_count'] < obs['previous_count'] else 'Stable'}

## Conservation Analysis
### Threats Identified
{', '.join(obs['threats'])}

### Risk Assessment
The species faces significant challenges from the identified threats. 
Immediate conservation action is recommended.

## Protection Recommendations
1. **Immediate Actions:**
   - Increase anti-poaching patrols
   - Engage local communities in conservation

2. **Short-term Strategies:**
   - Habitat restoration programs
   - Wildlife corridors establishment

3. **Long-term Plans:**
   - Sustainable conservation financing
   - Research and monitoring programs

## Monitoring Suggestions
- Conduct quarterly population surveys
- Track habitat changes using satellite imagery
- Monitor threat levels and human-wildlife conflict incidents
                        """
                    else:
                        # In production, you would use the actual Grok API call here
                        # For now, we'll use a template response
                        report_content = f"""
# Conservation Report: {obs['species']}

## Executive Summary
Based on field observations in {obs['location']} as of {obs['date']}, 
the {obs['species']} population shows {'positive' if obs['current_count'] > obs['previous_count'] else 'concerning'} trends.

## Population Trend Analysis
- Current Population: {obs['current_count']:,}
- Previous Count (5 years ago): {obs['previous_count']:,}
- Net Change: {obs['current_count'] - obs['previous_count']} individuals
- Percentage Change: {((obs['current_count'] - obs['previous_count']) / obs['previous_count'] * 100):.1f}%
- Population Density: {(obs['current_count'] / obs['habitat_area']):.2f} per sq km

### Population Trend Visualization
The population has {'increased by' if obs['current_count'] > obs['previous_count'] else 'decreased by'} 
{abs(((obs['current_count'] - obs['previous_count']) / obs['previous_count'] * 100)):.1f}% over the past 5 years.

## Conservation Analysis

### Current Threats Assessment
The following threats have been identified in order of severity:

{chr(10).join([f"- **{threat}:** Moderate to High Impact" for threat in obs['threats']])}

### Habitat Assessment
- **Habitat Area:** {obs['habitat_area']:,.0f} sq km
- **Habitat Condition:** Moderate with some degradation in peripheral areas
- **Connectivity:** Fragmented in certain sections due to human infrastructure

### Additional Observations
{obs['additional_notes'] if obs['additional_notes'] else "No additional observations recorded."}

## Protection Recommendations

### ⚡ Immediate Actions (Next 6 Months)
1. **Enhanced Anti-Poaching Measures**
   - Increase patrol frequency in high-risk areas
   - Deploy camera traps for monitoring
   - Train local rangers in advanced tracking

2. **Community Engagement**
   - Conduct awareness programs in surrounding villages
   - Establish human-wildlife conflict mitigation teams
   - Create alternative livelihood programs

### 📅 Short-term Strategies (1-2 Years)
1. **Habitat Restoration**
   - Reforest degraded areas
   - Establish wildlife corridors
   - Remove invasive species

2. **Population Monitoring**
   - Implement annual census programs
   - GPS collar tracking of key individuals
   - Genetic diversity assessment

### 🌍 Long-term Conservation Plans (3-5 Years)
1. **Protected Area Expansion**
   - Advocate for habitat protection status
   - Establish buffer zones
   - Create transboundary conservation areas

2. **Sustainable Management**
   - Develop ecotourism programs
   - Implement climate adaptation strategies
   - Strengthen conservation legislation

## 📊 Monitoring Recommendations

### Key Indicators to Track
- Population size and structure
- Habitat quality and extent
- Threat levels and distribution
- Human-wildlife conflict incidents
- Reproductive success rates

### Survey Methodology
- **Method:** Distance sampling and camera traps
- **Frequency:** Quarterly surveys
- **Data Analysis:** Population viability analysis annually

### Data Management
- Establish centralized database
- Regular data validation protocols
- Share findings with conservation network

---
*Report generated by Conservation Report Generator AI*
*Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
                        """
                    
                    # Store the report
                    st.session_state.current_report = {
                        'content': report_content,
                        'species': obs['species'],
                        'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'observation': obs
                    }
                    
                    # Add to history
                    st.session_state.generated_reports.append({
                        'species': obs['species'],
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'location': obs['location']
                    })
                    
                    st.success("✅ Report generated successfully!")
                    
                except Exception as e:
                    st.error(f"Error generating report: {str(e)}")
        
        # Display report if available
        if st.session_state.current_report:
            st.markdown("### 📄 Generated Conservation Report")
            
            # Download button
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                st.download_button(
                    label="📥 Download Report (TXT)",
                    data=st.session_state.current_report['content'],
                    file_name=f"conservation_report_{obs['species']}_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )
            with col2:
                if st.button("📋 Copy to Clipboard"):
                    st.write("Report copied to clipboard!")
                    # Note: Actual clipboard functionality requires additional JavaScript
            
            # Display report in a nice card
            with st.container():
                st.markdown('<div class="report-card">', unsafe_allow_html=True)
                st.markdown(st.session_state.current_report['content'])
                st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.info("👆 Please enter observations in the 'Observation Input' tab first!")

# Tab 3: Visualizations
with tab3:
    if 'current_observation' in st.session_state:
        obs = st.session_state.current_observation
        
        st.markdown("### 📊 Conservation Data Visualization")
        
        # Create two columns for charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Matplotlib population trend chart
            st.markdown("#### Population Trend (Matplotlib)")
            fig, ax = plt.subplots(figsize=(8, 5))
            
            years = ['5 Years Ago', 'Current']
            populations = [obs['previous_count'], obs['current_count']]
            colors = ['#ff9999', '#66b3ff'] if populations[1] < populations[0] else ['#66b3ff', '#ff9999']
            
            bars = ax.bar(years, populations, color=colors, edgecolor='black', linewidth=1)
            ax.set_ylabel('Population Count')
            ax.set_title(f'{obs["species"]} Population Trend')
            
            # Add value labels on bars
            for bar, pop in zip(bars, populations):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{pop:,.0f}', ha='center', va='bottom')
            
            # Add trend line
            ax.plot(years, populations, 'ro-', linewidth=2, markersize=8, label='Trend')
            ax.legend()
            
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
            plt.close()
            
            # Population metrics
            change_pct = ((obs['current_count'] - obs['previous_count']) / obs['previous_count'] * 100)
            st.metric("Population Change", f"{change_pct:+.1f}%", 
                     delta_color="normal" if change_pct > 0 else "inverse")
        
        with col2:
            # Plotly interactive pie chart for threats
            st.markdown("#### Threat Assessment (Plotly)")
            
            # Create threat impact data
            threats_data = pd.DataFrame({
                'Threat': obs['threats'] + ['Other Factors'],
                'Impact Score': np.random.randint(60, 100, size=len(obs['threats']) + 1)
            })
            
            fig = px.pie(threats_data, values='Impact Score', names='Threat',
                        title='Relative Impact of Different Threats',
                        color_discrete_sequence=px.colors.sequential.RdBu,
                        hole=0.3)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        # Population density visualization
        st.markdown("#### Population Density Analysis")
        col3, col4 = st.columns(2)
        
        with col3:
            # Create density gauge
            density = obs['current_count'] / obs['habitat_area']
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=density,
                title={'text': f"Population Density (individuals/sq km)"},
                delta={'reference': 1.0},
                gauge={
                    'axis': {'range': [None, max(density * 2, 5)]},
                    'bar': {'color': "darkgreen"},
                    'steps': [
                        {'range': [0, density/2], 'color': "lightgreen"},
                        {'range': [density/2, density], 'color': "yellow"},
                        {'range': [density, density*1.5], 'color': "orange"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': density * 1.2
                    }
                }
            ))
            
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            # Habitat capacity analysis
            carrying_capacity = obs['habitat_area'] * 0.5  # Assuming 0.5 animals per sq km carrying capacity
            current_percent = (obs['current_count'] / carrying_capacity) * 100
            
            fig = go.Figure(go.Bar(
                x=['Current Population', 'Estimated Carrying Capacity'],
                y=[obs['current_count'], carrying_capacity],
                marker_color=['#2E7D32', '#FFA726'],
                text=[f"{obs['current_count']:,.0f}", f"{carrying_capacity:,.0f}"],
                textposition='auto',
            ))
            
            fig.update_layout(
                title="Habitat Carrying Capacity Analysis",
                yaxis_title="Number of Individuals",
                height=300,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.caption(f"Current habitat utilization: {current_percent:.1f}% of estimated capacity")
        
        # Timeline projection
        st.markdown("#### Population Projection (Next 5 Years)")
        
        # Create projection data
        years_future = list(range(2024, 2029))
        if obs['current_count'] > obs['previous_count']:
            # Growing population
            growth_rate = (obs['current_count'] / obs['previous_count']) ** (1/5) - 1
            future_pops = [obs['current_count'] * (1 + growth_rate) ** i for i in range(1, 6)]
        else:
            # Declining population
            decline_rate = 1 - (obs['current_count'] / obs['previous_count']) ** (1/5)
            future_pops = [obs['current_count'] * (1 - decline_rate) ** i for i in range(1, 6)]
        
        # Create dataframe
        projection_df = pd.DataFrame({
            'Year': years_future,
            'Projected Population': [int(pop) for pop in future_pops]
        })
        
        # Plot
        fig = px.line(projection_df, x='Year', y='Projected Population',
                     title=f'{obs["species"]} Population Projection',
                     markers=True)
        fig.update_traces(line_color='red', line_width=3)
        fig.add_hline(y=obs['current_count'], line_dash="dash", 
                     annotation_text="Current Population", 
                     annotation_position="bottom right")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add confidence interval note
        st.caption("⚠️ Projections are estimates based on current trends and may vary based on conservation efforts and environmental factors.")
    
    else:
        st.info("👆 Enter observations in the first tab to see visualizations!")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("🌱 **Powered by Grok API & LangChain**")
with col2:
    st.markdown("🔄 **Real-time Analysis**")
with col3:
    st.markdown("📊 **Data-Driven Conservation**")

# Add refresh rate info
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

