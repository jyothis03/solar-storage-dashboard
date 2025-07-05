import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Chainfly", layout="centered")

st.title("Welcome to Chainfly ⚡")
USE_LOCAL = True

if "page" not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "home":
    col1, col2 = st.columns(2)
    with col1:
        if st.button(" Simulate"):
            st.session_state.page = "simulate"
            st.rerun()
    with col2:
        if st.button(" View Trends"):
            st.session_state.page = "trends"
            st.rerun()

if st.session_state.page == "simulate":
    st.subheader(" Solar Simulation")

    st.write("### Configure Simulation Parameters")

    # Location as text input
    location = st.text_input("Location (e.g., Kerala, Delhi)", "Default")

    # Scenario select
    scenario = st.selectbox("Scenario", ["Clear", "Cloudy", "Monsoon"])

    # Noise toggle
    noise = st.checkbox("Add Random Noise")

    # Battery size
    battery_size = st.slider("Battery size (kWh)", min_value=1, max_value=20, value=5)

    efficiency = st.slider("Round-trip Efficiency (%)", min_value=70, max_value=100, value=90)
    dod = st.slider("Depth of Discharge (DoD) (%)", min_value=50, max_value=100, value=80)

    # System loss factor
    loss_factor = st.slider("System loss factor (%)", min_value=0, max_value=50, value=10)

    if st.button("Run Simulation"):
        params = {
            "location": location,
            "battery_size": battery_size,
            "loss_factor": loss_factor,
            "scenario": scenario,
            "noise": noise,
            "efficiency": efficiency,
             "dod": dod
        }
        try:
            if USE_LOCAL:
                url = "http://127.0.0.1:8000/simulate"
            else:
                url = "https://solar-storage-backend.onrender.com/simulate"

            response = requests.get(url, params=params)

            if response.ok:
                data = response.json()
                panel_output = data["panel_output_kw"]
                storage_kw = data["storage_kw"]
                charge_percent = data["charge_percent"]
                timestamp = data["timestamp"]

                st.metric("Panel Output (kW)", panel_output)
                st.metric("Storage (kW)", storage_kw)
                st.metric("Charge Level (%)", f"{charge_percent}%")

                if charge_percent < 20:
                    st.error(" Battery Low: Consider grid charge")
                if panel_output > 4:
                    st.success(" High Panel Output")

                # ✅ Save in session_state
                st.session_state.simulation_result = {
                    "Location": location,
                    "Scenario": scenario,
                    "Noise Enabled": noise,
                    "Battery Size (kWh)": battery_size,
                    "Loss Factor (%)": loss_factor,
                    "Panel Output (kW)": panel_output,
                    "Storage (kW)": storage_kw,
                    "Charge Percent (%)": charge_percent,
                    "Timestamp": timestamp,
                }

            else:
                st.error("Failed to fetch simulation data.")
        except Exception as e:
            st.error(f"Connection error: {e}")

    # ✅ Check if we have a saved result
    if "simulation_result" in st.session_state:
        export_data = st.session_state.simulation_result

        df_export = pd.DataFrame([export_data])

        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="simulation_results.csv",
            mime="text/csv",
        )

        json_str = df_export.to_json(orient="records", indent=2)
        st.download_button(
            label="Download JSON",
            data=json_str,
            file_name="simulation_results.json",
            mime="application/json",
        )

    if st.button(" Back"):
        st.session_state.page = "home"
        st.rerun()

if st.session_state.page == "trends":
    st.subheader(" Real-Time Trends")

    url = "http://127.0.0.1:8000/charts" if USE_LOCAL else "https://solar-storage-backend.onrender.com/charts"

    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            df = pd.DataFrame(data)

            df["timestamp"] = pd.to_datetime(df["timestamp"])

            # Panel Output Chart with units
            st.subheader("Panel Output Trends")
            fig1, ax1 = plt.subplots(figsize=(8, 4))
            ax1.plot(df["timestamp"], df["panel_output_kw"], marker='o', linestyle='-')
            ax1.set_xlabel("Timestamp")
            ax1.set_ylabel("Panel Output (kW)")
            ax1.set_title("Panel Output Over Time")
            ax1.grid(True)
            st.pyplot(fig1)

            # Charge Trends Chart with units
            st.subheader("Charge Trends")
            fig2, ax2 = plt.subplots(figsize=(8, 4))
            ax2.plot(df["timestamp"], df["charge_percent"], marker='o', color='orange', linestyle='-')
            ax2.set_xlabel("Timestamp")
            ax2.set_ylabel("Charge Level (%)")
            ax2.set_title("Charge Level Over Time")
            ax2.grid(True)
            st.pyplot(fig2)

            if st.button("Back"):
                st.session_state.page = "home"
                st.rerun()
        else:
            st.error("Could not fetch chart data.")
    except Exception as e:
        st.error(f"Error: {e}")
        if st.button("Back"):
            st.session_state.page = "home"
            st.rerun()
