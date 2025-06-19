import streamlit as st
import requests

st.set_page_config(page_title="Chainfly")
st.title("Dashboard")

if st.button("Get data"):
    response=requests.get("https://solar-storage-backend.onrender.com/simulate")
    data=response.json()

    st.metric("Panel Output(kW)",data["panel_output_kw"])
    st.metric("Storage (kW)", data["storage_kw"])
    st.metric("Charge Level (%)", f'{data["charge_percent"]}%')
