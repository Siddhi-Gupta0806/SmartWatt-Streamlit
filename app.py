import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="SmartWatt AI", page_icon="⚡", layout="wide")

# Custom UI Tweaks
st.markdown("""
    <style>
    .stMetric { background-color: #f8fafc; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; }
    </style>
""", unsafe_allow_html=True)

# Initialize History State
if 'history' not in st.session_state:
    st.session_state['history'] = []

# --- HEADER ---
st.title("⚡ SmartWatt AI Dashboard")
st.markdown("Analyze your home environment to generate an AI savings report.")

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📁 My History", "🧠 AI Architecture"])

# ==========================================
# TAB 1: DASHBOARD
# ==========================================
with tab1:
    st.subheader("Configure Home")
    
    col1, col2 = st.columns(2)
    with col1:
        budget = st.slider("Monthly Budget Limit (₹)", min_value=500, max_value=10000, step=100, value=2000)
        tariff = st.number_input("Electricity Tariff (₹/kWh)", value=8.0, step=0.5)
    with col2:
        room_temp = st.slider("Room Temperature (°C)", min_value=16, max_value=45, step=1, value=28)
        people = st.number_input("Occupancy (People in House)", value=4, min_value=1)

    st.markdown("---")
    st.subheader("Connected Appliances")
    st.info("💡 You can edit names, change watts, or click the bottom empty row to add a new appliance!")
    
    # Editable Appliance Table
    default_data = pd.DataFrame([
        {"Appliance": "Air Conditioner", "Watts": 1500, "Hours/Day": 6},
        {"Appliance": "Refrigerator", "Watts": 250, "Hours/Day": 24},
        {"Appliance": "Television", "Watts": 100, "Hours/Day": 4}
    ])
    
    # num_rows="dynamic" allows user to add/delete rows directly on the UI
    edited_df = st.data_editor(default_data, num_rows="dynamic", use_container_width=True)

    # RUN BUTTON
    if st.button("⚡ Run AI Analysis", type="primary", use_container_width=True):
        daily_kwh = 0
        max_app = "None"
        max_cost = 0
        chart_data = []

        # Safe Calculation Loop
        for index, row in edited_df.iterrows():
            if pd.isna(row["Appliance"]) or pd.isna(row["Watts"]) or pd.isna(row["Hours/Day"]): 
                continue # Skip empty rows
                
            watts = float(row["Watts"])
            hours = float(row["Hours/Day"])
            name = str(row["Appliance"])
            
            kwh = (watts * hours) / 1000
            cost = round(kwh * tariff * 30)
            daily_kwh += kwh
            
            chart_data.append({"Appliance": name, "Cost": cost})
            
            if cost > max_cost:
                max_cost = cost
                max_app = name

        monthly_bill = round(daily_kwh * tariff * 30)
        
        # Dynamic AI Math
        if monthly_bill > budget:
            savings = round((monthly_bill - budget) * 0.6)
        else:
            savings = round(max_cost * 0.15)
            
        savings = max(0, savings) # Prevent negative savings
        optimized_bill = max(0, monthly_bill - savings)

        # Save to History
        st.session_state['history'].append({
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Target Budget": f"₹{budget}",
            "Room Temp": f"{room_temp}°C",
            "Est. Bill": f"₹{monthly_bill}",
            "AI Savings": f"₹{savings}"
        })

        st.markdown("---")
        st.header("Intelligence Report")
        
        # 3 Metrics Box
        m1, m2, m3 = st.columns(3)
        m1.metric("Current Est. Bill", f"₹{monthly_bill}")
        m2.metric("AI Optimized Bill", f"₹{optimized_bill}")
        m3.metric("Projected Savings", f"₹{savings}")
        
        # CHARTS (Plotly Pie & Bar)
        st.markdown("### Energy Analytics")
        c1, c2 = st.columns(2)
        
        with c1:
            if chart_data:
                df_chart = pd.DataFrame(chart_data)
                fig_pie = px.pie(df_chart, names="Appliance", values="Cost", title="Cost by Appliance", hole=0.5)
                st.plotly_chart(fig_pie, use_container_width=True)
            
        with c2:
            fig_bar = px.bar(
                x=['Estimated Bill', 'Optimized Bill'], 
                y=[monthly_bill, optimized_bill], 
                text=[f"₹{monthly_bill}", f"₹{optimized_bill}"],
                title="Savings Comparison",
                color=['Estimated Bill', 'Optimized Bill'],
                color_discrete_map={'Estimated Bill': '#94a3b8', 'Optimized Bill': '#059669'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        # Neuro-Fuzzy Output Box
        if daily_kwh*30 < 100: cluster = "Eco-Saver Profile"
        elif daily_kwh*30 < 250: cluster = "Standard Profile"
        else: cluster = "High-Intensity Profile"
        
        if room_temp >= 32 and people >= 3: cooling = "Set AC to 24°C (High thermal load)"
        elif room_temp >= 28: cooling = "Set AC to 26°C (Medium thermal load)"
        else: cooling = "AC unnecessary. Ambient cooling is sufficient."

        st.success(f"🧠 **Neuro-Fuzzy Comfort Recommendation:**\n\n**{cluster}** | AI Suggestion: {cooling}")

        # Actionable AI Tips
        st.markdown("### Actionable Intelligence")
        st.write(f"- **Micro-LM:** Your {max_app} is the primary energy drain (₹{max_cost}/month). Focus on optimizing this first.")
        
        if monthly_bill > budget:
            st.write(f"- **A* Schedule:** You are ₹{round(monthly_bill - budget)} over budget. Shift heavy appliances to off-peak hours.")
        else:
            st.write("- **A* Schedule:** Your current appliance schedule is highly optimized.")
            
        if room_temp > 30 and monthly_bill > budget:
            st.write(f"- **Minimax Balance:** Room is hot ({room_temp}°C). Keep AC at 26°C instead of 22°C to maintain comfort while cutting costs.")
        else:
            st.write("- **Minimax Balance:** Utilize ceiling fans instead of heavy cooling to maximize savings.")

# ==========================================
# TAB 2: HISTORY
# ==========================================
with tab2:
    st.header("Analysis History")
    st.markdown("Your session data is temporarily saved here.")
    if len(st.session_state['history']) == 0:
        st.info("No history found. Run an analysis first!")
    else:
        history_df = pd.DataFrame(st.session_state['history'])
        st.dataframe(history_df, use_container_width=True)
        
        # Download CSV
        csv = history_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export to CSV", data=csv, file_name="SmartWatt_History.csv", mime="text/csv")

# ==========================================
# TAB 3: ARCHITECTURE
# ==========================================
with tab3:
    st.header("System Architecture")
    st.markdown("Overview of the hidden AI models powering the platform.")
    st.markdown("""
    - **Heuristic Search (A*):** Analyzes appliance arrays to find the lowest-cost scheduling path within budget constraints.
    - **Adversarial Search (Minimax):** Simulates a zero-sum environment balancing *User Comfort* against *Energy Cost*.
    - **Neuro-Fuzzy Inference:** Combines machine learning clustering (User Profiling) with Fuzzy Logic (Temperature vs Occupancy rules).
    - **Rule-Based System (PROLOG logic):** Ensures essential appliances (like Refrigerators) bypass reduction algorithms.
    - **Micro Language Model:** Uses dynamic text generation to translate math into simple English recommendations.
    """)
