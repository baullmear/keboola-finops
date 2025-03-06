import streamlit as st
import pandas as pd
from pathlib import Path

# Sample data - replace with your actual data source
data = {
    "Metric": [
        "Počet projektů",
        "PPU",
        "Premimum SLA",
        "CS Mds",
        "Snowflake credits",
        "Snowflake storage"
    ],
    "Current Spend": [150, 20000, 13043, 5, 3500, 70],  # Example values
    "Limit": [130, 28000, 13043, 15, 4167, 100]  # Example limits
}

# Convert to DataFrame
df = pd.DataFrame(data)

# Set page config for a cleaner look
st.set_page_config(
    page_title="Keboola FinOps",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
        background-color: #f0f2f6;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4 !important;
        color: white !important;
    }
    .card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 15px;
        border-left: 4px solid #1f77b4;
    }
    .header-card {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    .total-box {
        background-color: #1f77b4;
        color: white;
        padding: 15px;
        border-radius: 5px;
        text-align: center;
        margin-top: 20px;
    }
    .warning {
        color: #ff6b6b;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Remove logo-related code and just keep the title
st.markdown("# Keboola FinOps")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Aktuální spotřeba", "Cena za jednotku", "Celkové náklady", "Plánování"])

# Tab 1: Display the data with a nicer table
with tab1:
    st.write("### Aktuální spotřeba")
    
    # Add explanation in a styled container
    st.markdown("""
    <div class="header-card">
    <p>Přehled aktuální spotřeby jednotlivých metrik ve srovnání s jejich limity.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add option to switch between monthly and yearly view
    time_period = st.radio("Zobrazit:", ["Měsíční", "Roční"], horizontal=True)
    
    # Create a copy of the dataframe to modify based on selection
    display_df = df.copy()
    
    # If yearly view is selected, adjust values appropriately
    if time_period == "Roční":
        for i, metric in enumerate(display_df["Metric"]):
            # Don't multiply number of projects or Premium SLA
            if metric not in ["Počet projektů", "Premimum SLA", "Snowflake storage"]:
                # Multiply current spend by 12 for all metrics
                display_df.at[i, "Current Spend"] = display_df.at[i, "Current Spend"] * 12
                
                # Set specific yearly limits for certain metrics
                if metric == "PPU":
                    display_df.at[i, "Limit"] = 336000
                elif metric == "Snowflake credits":
                    display_df.at[i, "Limit"] = 50004
                elif metric == "CS Mds":
                    display_df.at[i, "Limit"] = 180
                else:
                    # For other metrics, multiply limit by 12
                    display_df.at[i, "Limit"] = display_df.at[i, "Limit"] * 12
    
    # Format the dataframe for display
    display_df_formatted = display_df.copy()
    display_df_formatted["Current Spend"] = display_df_formatted["Current Spend"].apply(lambda x: f"{x:,}")
    display_df_formatted["Limit"] = display_df_formatted["Limit"].apply(lambda x: f"{x:,}")
    
    # Display the table with better styling
    st.table(display_df_formatted)

    # Plotting with better visuals
    st.write(f"### {time_period} spotřeba vs Limit")
    
    # Create two columns for the progress bars
    col1, col2 = st.columns(2)
    
    # Display progress bars in columns
    for i, (index, row) in enumerate(display_df.iterrows()):
        with col1 if i % 2 == 0 else col2:
            progress_value = int((row['Current Spend'] / row['Limit']) * 100)
            
            # Create a card for each metric
            st.markdown(f"""
            <div class="card">
                <h4 style="color:#1f77b4;margin-bottom:10px;">{row['Metric']}</h4>
                <p><b>Spotřeba:</b> {row['Current Spend']:,} / {row['Limit']:,} ({progress_value}%)</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Add progress bar
            st.progress(100 if progress_value > 100 else progress_value)
            
            # Add warning if limit exceeded
        

# Tab 2: Adjust Price Per Unit
unit_costs = {}
overconsumption_costs = {}  # New dictionary to store overconsumption prices
with tab2:
    st.write("### Cena za jednotku")
    
    # Add explanation in a styled container
    st.markdown("""
    <div class="header-card">
    <p>Nastavení cen za jednotku pro jednotlivé metriky, včetně základních cen, cen se slevou a cen za nadspotřebu.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for side-by-side price tables
    col1, col2 = st.columns(2)
    
    # Basic price column
    with col1:
        st.markdown("""
        <div style="background-color:#1f77b4;color:white;padding:10px;border-radius:5px;margin-bottom:10px;text-align:center;">
            <h4 style="margin:0;">Základní cena (bez slevy)</h4>
        </div>
        """, unsafe_allow_html=True)
        
        basic_costs = {}
        for metric in data["Metric"]:
            # Set default values for basic price (without sales discount)
            if metric == "Počet projektů":
                default_value = 468.0  # Example: higher basic price before discount
            elif metric == "PPU":
                default_value = 0.94    # Example: higher basic price before discount
            elif metric == "CS Mds":
                default_value = 650.0  # Example: higher basic price before discount
            elif metric == "Snowflake credits":
                default_value = 5.0    # Example: higher basic price before discount
            elif metric == "Snowflake storage":
                default_value = 30.0   # Example: higher basic price before discount
            else:
                default_value = 0.0
            
            # Add a number input for basic price in a card
            st.markdown(f"""
            <div class="card" style="border-left-color:#4e79a7;">
                <h5>{metric}</h5>
            </div>
            """, unsafe_allow_html=True)
            basic_price = st.number_input(f"Základní cena - {metric}", min_value=0.0, value=default_value, step=0.1, key=f"basic_{metric}")
            basic_costs[metric] = basic_price
    
    # Discounted price column
    with col2:
        st.markdown("""
        <div style="background-color:#1f77b4;color:white;padding:10px;border-radius:5px;margin-bottom:10px;text-align:center;">
            <h4 style="margin:0;">Cena se slevou</h4>
        </div>
        """, unsafe_allow_html=True)
        
        for metric in data["Metric"]:
            # Set default values for price with sales discount (current prices)
            if metric == "Počet projektů":
                default_value = 377.0
            elif metric == "PPU":
                default_value = 0.75
            elif metric == "CS Mds":
                default_value = 500.0
            elif metric == "Snowflake credits":
                default_value = 4.0
            elif metric == "Snowflake storage":
                default_value = 23.0
            else:
                default_value = 0.0
            
            # Add a number input for price with sales in a card
            st.markdown(f"""
            <div class="card" style="border-left-color:#59a14f;">
                <h5>{metric}</h5>
            </div>
            """, unsafe_allow_html=True)
            new_price = st.number_input(f"{metric}", min_value=0.0, value=default_value, step=0.1)
            unit_costs[metric] = new_price
    
    # Add a divider
    st.markdown("---")
    
    # Overconsumption pricing table (separate section)
    st.markdown("""
    <div style="background-color:#1f77b4;color:white;padding:10px;border-radius:5px;margin-bottom:10px;text-align:center;">
        <h3 style="margin:0;">Cena za nadspotřebu</h3>
    </div>
    <p>Speciální ceny pro nadlimitní spotřebu vybraných metrik:</p>
    """, unsafe_allow_html=True)
    
    # Create a dataframe for the overconsumption pricing table
    overconsumption_data = {
        "Metrika": ["Počet projektů", "PPU"],
        "Cena za nadspotřebu": [650.0, 1.3]
    }
    
    # Convert to DataFrame
    overconsumption_df = pd.DataFrame(overconsumption_data)
    
    # Display the table with better styling
    st.table(overconsumption_df)
    
    # Store the overconsumption prices in the dictionary
    overconsumption_costs["Počet projektů"] = 650.0
    overconsumption_costs["PPU"] = 1.3
    
    # Add another divider
    st.markdown("---")
    
    # Display pricing tables with better formatting (moved from tab4)
    st.markdown("""
    <div style="background-color:#1f77b4;color:white;padding:10px;border-radius:5px;margin-bottom:10px;text-align:center;">
        <h3 style="margin:0;">Cenová pásma</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background-color:#4e79a7;color:white;padding:10px;border-radius:5px;margin-bottom:10px;text-align:center;">
            <h4 style="margin:0;">KEBOOLA PROJECT</h4>
        </div>
        """, unsafe_allow_html=True)
        
        df_project = pd.DataFrame([
            {"Pásmo": "0-5", "Sleva": "0%", "Cena za jednotku": "$500"},
            {"Pásmo": "6-10", "Sleva": "5%", "Cena za jednotku": "$475"},
            {"Pásmo": "11-25", "Sleva": "10%", "Cena za jednotku": "$450"},
            {"Pásmo": "26 a více", "Sleva": "15%", "Cena za jednotku": "$425"}
        ])
        st.table(df_project)

    with col2:
        st.markdown("""
        <div style="background-color:#4e79a7;color:white;padding:10px;border-radius:5px;margin-bottom:10px;text-align:center;">
            <h4 style="margin:0;">KEBOOLA PPU</h4>
        </div>
        """, unsafe_allow_html=True)
        
        df_ppu = pd.DataFrame([
            {"Pásmo": "až 2 000", "Sleva": "0%", "Cena za jednotku": "$1.00"},
            {"Pásmo": "2 001 - 5 000", "Sleva": "5%", "Cena za jednotku": "$0.95"},
            {"Pásmo": "5 001 - 10 000", "Sleva": "10%", "Cena za jednotku": "$0.90"},
            {"Pásmo": "10 001 - 20 000", "Sleva": "15%", "Cena za jednotku": "$0.85"},
            {"Pásmo": "20 001 a více", "Sleva": "20%", "Cena za jednotku": "$0.80"}
        ])
        st.table(df_ppu)

# Function to calculate price based on volume (moved to global scope)
def get_price(volume, pricing_table):
    for (min_vol, max_vol), rates in pricing_table.items():
        if min_vol <= volume <= max_vol:
            return rates['price']
    return pricing_table[max(pricing_table.keys())]['price']

# Define pricing tables (moved to global scope)
project_pricing = {
    (0, 5): {'discount': 0.00, 'price': 500},
    (6, 10): {'discount': 0.05, 'price': 475},
    (11, 25): {'discount': 0.10, 'price': 450},
    (26, float('inf')): {'discount': 0.15, 'price': 425}
}

ppu_pricing = {
    (0, 2000): {'discount': 0.00, 'price': 1.00},
    (2001, 5000): {'discount': 0.05, 'price': 0.95},
    (5001, 10000): {'discount': 0.10, 'price': 0.90},
    (10001, 20000): {'discount': 0.15, 'price': 0.85},
    (20001, float('inf')): {'discount': 0.20, 'price': 0.80}
}

# Tab 3: Calculated Costs
with tab3:
    st.write("### Celkové náklady")
    
    # Create a container with a light background for the explanation
    st.markdown("""
    <div class="header-card">
    <p>Tato sekce zobrazuje vypočítané náklady na základě aktuální spotřeby a jednotkových cen. 
    Pro metriky překračující limit se používá speciální cenová politika.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Function to calculate costs with appropriate pricing
    def calculate_cost(metric, spend, limit, unit_cost):
        if spend <= limit:
            # Under limit - use regular pricing
            cost = spend * unit_cost
            details = f"{spend} × ${unit_cost:.2f} = ${cost:.2f}"
            return cost, details
        
        # Over limit - handle differently based on metric
        if metric == "Počet projektů":
            # Use project pricing tiers
            cost = calculate_cost_with_tiers(spend, limit, project_pricing)
            in_limit = min(spend, limit)
            over_limit = max(0, spend - limit)
            in_limit_price = get_price(limit, project_pricing)
            over_limit_price = get_price(over_limit, project_pricing)
            
            details = f"""
            <span style="color:#0066cc">V limitu:</span> {in_limit} × ${in_limit_price:.2f} = ${in_limit * in_limit_price:.2f}<br>
            <span style="color:#ff6b6b">Nad limit:</span> {over_limit} × ${over_limit_price:.2f} = ${over_limit * over_limit_price:.2f}<br>
            <span style="font-weight:bold">Celkem: ${cost:.2f}</span>
            """
            return cost, details
            
        elif metric == "PPU":
            # Use PPU pricing tiers
            cost = calculate_cost_with_tiers(spend, limit, ppu_pricing)
            in_limit = min(spend, limit)
            over_limit = max(0, spend - limit)
            in_limit_price = get_price(limit, ppu_pricing)
            over_limit_price = get_price(over_limit, ppu_pricing)
            
            details = f"""
            <span style="color:#0066cc">V limitu:</span> {in_limit} × ${in_limit_price:.2f} = ${in_limit * in_limit_price:.2f}<br>
            <span style="color:#ff6b6b">Nad limit:</span> {over_limit} × ${over_limit_price:.2f} = ${over_limit * over_limit_price:.2f}<br>
            <span style="font-weight:bold">Celkem: ${cost:.2f}</span>
            """
            return cost, details
            
        elif metric == "Premimum SLA":
            # Premium SLA is a fixed price
            cost = spend * unit_cost
            details = f"Fixní cena: ${cost:.2f}"
            return cost, details
            
        else:
            # For other metrics, apply 30% premium on over-limit portion
            in_limit = min(spend, limit)
            over_limit = max(0, spend - limit)
            in_limit_cost = in_limit * unit_cost
            over_limit_cost = over_limit * (unit_cost * 1.3)
            cost = in_limit_cost + over_limit_cost
            
            details = f"""
            <span style="color:#0066cc">V limitu:</span> {in_limit} × ${unit_cost:.2f} = ${in_limit_cost:.2f}<br>
            <span style="color:#ff6b6b">Nad limit:</span> {over_limit} × ${unit_cost * 1.3:.2f} (30% navýšení) = ${over_limit_cost:.2f}<br>
            <span style="font-weight:bold">Celkem: ${cost:.2f}</span>
            """
            return cost, details
    
    # Helper function for tiered pricing calculation
    def calculate_cost_with_tiers(spend, limit, pricing_table):
        in_limit_cost = min(spend, limit) * get_price(limit, pricing_table)
        if spend > limit:
            over_limit = spend - limit
            over_limit_cost = over_limit * get_price(over_limit, pricing_table)
            return in_limit_cost + over_limit_cost
        return in_limit_cost
    
    # Calculate costs for all metrics
    calculated_costs = []
    cost_details = []
    
    # Create columns for the metrics display
    col1, col2 = st.columns(2)
    
    # Process each metric
    for i, (index, row) in enumerate(df.iterrows()):
        metric = row['Metric']
        current_spend = row['Current Spend']
        limit = row['Limit']
        unit_cost = unit_costs.get(metric, 0)
        
        # Calculate cost and get details
        cost, details = calculate_cost(metric, current_spend, limit, unit_cost)
        calculated_costs.append(cost)
        
        # Display in alternating columns
        with col1 if i % 2 == 0 else col2:
            # Create a card-like container for each metric
            st.markdown(f"""
            <div class="card">
                <h4 style="color:#1f77b4;margin-bottom:5px;">{metric}</h4>
                <p><b>Aktuální spotřeba:</b> {current_spend:,}</p>
                <p><b>Limit:</b> {limit:,}</p>
                <p><b>Výpočet:</b><br>{details}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Add a divider
    st.markdown("---")
    
    # Display the calculated costs in a table
    st.subheader("Souhrn nákladů")
    
    # Create a DataFrame with all the cost information
    calculated_df = pd.DataFrame({
        "Metrika": data["Metric"],
        "Aktuální spotřeba": [row['Current Spend'] for _, row in df.iterrows()],
        "Limit": [row['Limit'] for _, row in df.iterrows()],
        "Vypočítaná cena ($)": [f"{cost:,.2f}" for cost in calculated_costs]
    })
    
    # Display the table
    st.table(calculated_df)

    # Calculate and display the total cost
    total_cost = sum(calculated_costs)
    
    # Create a visually appealing total cost display
    st.markdown(f"""
    <div class="total-box">
        <h2 style="margin:0;">Celkové náklady: ${total_cost:,.2f}</h2>
    </div>
    """, unsafe_allow_html=True)

# Tab 4: Forecasting Overusage
with tab4:
    st.write("### Plánované náklady při dokupu")
    
    # Add explanation in a styled container
    st.markdown("""
    <div class="header-card">
    <p>Plánování budoucích nákladů na základě předpokládané spotřeby. Zadejte očekávanou spotřebu pro jednotlivé metriky.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Forecasted usage input section
    st.markdown("""
    <div style="background-color:#1f77b4;color:white;padding:10px;border-radius:5px;margin-bottom:10px;text-align:center;">
        <h4 style="margin:0;">Zadejte plánovanou spotřebu</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Organize inputs in columns
    col1, col2 = st.columns(2)
    
    forecasted_costs = []
    forecasted_usage_values = {}
    forecasted_price_values = {}
    
    # First collect all inputs
    for i, metric in enumerate(data["Metric"]):
        # Skip Premium SLA as it's a fixed price
        if metric == "Premimum SLA":
            fixed_price = unit_costs.get(metric, 0) * data["Current Spend"][data["Metric"].index(metric)]
            forecasted_costs.append(fixed_price)
            forecasted_usage_values[metric] = data["Current Spend"][data["Metric"].index(metric)]
            forecasted_price_values[metric] = unit_costs.get(metric, 0)
            continue
            
        # Place input fields in alternating columns with card styling
        with col1 if i % 2 == 0 else col2:
            st.markdown(f"""
            <div class="card">
                <h4 style="color:#1f77b4;margin-bottom:5px;">{metric}</h4>
                <p>Zadejte plánovanou spotřebu:</p>
            </div>
            """, unsafe_allow_html=True)
            
            forecasted_usage = st.number_input(f"{metric}", min_value=0, step=1, format="%d")
            forecasted_usage_values[metric] = forecasted_usage
            
            # Calculate price based on the metric
            if metric == "Počet projektů":
                unit_price = get_price(forecasted_usage, project_pricing)
            elif metric == "PPU":
                unit_price = get_price(forecasted_usage, ppu_pricing)
            else:
                unit_price = unit_costs.get(metric, 0)
                
            forecasted_price_values[metric] = unit_price
            forecasted_cost = forecasted_usage * unit_price
            forecasted_costs.append(forecasted_cost)
    
    # Add divider
    st.markdown("---")
    
    # Display calculated costs section
    st.markdown("""
    <div style="background-color:#1f77b4;color:white;padding:10px;border-radius:5px;margin-bottom:10px;text-align:center;">
        <h4 style="margin:0;">Výsledek kalkulace</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Create a DataFrame with all the forecast information
    forecast_data = {
        "Metrika": list(data["Metric"]),
        "Plánovaná spotřeba": [forecasted_usage_values.get(m, 0) for m in data["Metric"]],
        "Cena za jednotku ($)": [forecasted_price_values.get(m, 0) for m in data["Metric"]],
        "Celková cena ($)": forecasted_costs
    }
    
    forecast_df = pd.DataFrame(forecast_data)
    
    # Format the numbers with commas and 2 decimal places
    for col in ["Cena za jednotku ($)", "Celková cena ($)"]:
        forecast_df[col] = forecast_df[col].apply(lambda x: f"{x:,.2f}")
    
    # Display the table
    st.table(forecast_df)

    # Calculate and display the total forecasted cost
    total_forecasted_cost = sum(forecasted_costs)
    
    # Create a visually appealing total cost display
    st.markdown(f"""
    <div class="total-box">
        <h2 style="margin:0;">Celkové plánované náklady: ${total_forecasted_cost:,.2f}</h2>
    </div>
    """, unsafe_allow_html=True) 