import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Chainfly", layout="centered")

st.title("Welcome to Chainfly ⚡")
USE_LOCAL = False

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

    try:
        if USE_LOCAL:
            response = requests.get("http://127.0.0.1:8000/simulate")
        else:
            response = requests.get("https://solar-storage-backend.onrender.com/simulate")

        if response.ok:
            data = response.json()
            panel_output = data["panel_output_kw"]
            storage_kw = data["storage_kw"]
            charge_percent = data["charge_percent"]

            st.metric("Panel Output (kW)", panel_output)
            st.metric("Storage (kW)", storage_kw)
            st.metric("Charge Level (%)", f"{charge_percent}%")

            if charge_percent < 20:
                st.error(" Battery Low: Consider grid charge")
            if panel_output > 4:
                st.success(" High Panel Output")

        else:
            st.error("Failed to fetch simulation data.")
    except Exception as e:
        st.error(f"Connection error: {e}")

    if st.button(" Back"):
        st.session_state.page = "home"
        st.rerun()
    elif st.button("Simulate again"):
        st.session_state.page = "simulate"
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

            st.subheader("Panel Output Trends")
            st.line_chart(df.set_index("timestamp")[["panel_output_kw"]], use_container_width=True)
            st.subheader("Charge Trends")
            st.line_chart(df.set_index("timestamp")[["charge_percent"]], use_container_width=True)
        
            if st.button("Back"):
                st.session_state.page = "home"
                st.rerun()
        else:
            st.error("Could not fetch chart data.")
    except Exception as e:
        st.error(f"Error: {e}")
        if st.button("⬅ Back"):
            st.session_state.page = "home"
            st.rerun()

