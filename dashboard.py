import streamlit as st
import requests

st.set_page_config(page_title="Chainfly")
st.title("Dashboard")

USE_LOCAL = True

if st.button("Get data"):

    if USE_LOCAL:
        response= requests.get(" http://127.0.0.1:8000/simulate")
    else:
        response = requests.get("https://solar-storage-backend.onrender.com/simulate")
    st.write("Status code:", response.status_code)  # Show status code in Streamlit
    st.write("Raw response:", response.text)        # Show raw response in Streamlit

    # Only try to parse JSON if the response is OK
    if response.headers.get("content-type", "").startswith("application/json"):
        data = response.json()
        st.metric("Panel Output(kW)", data["panel_output_kw"])
        st.metric("Storage (kW)", data["storage_kw"])
        st.metric("Charge Level (%)", f'{data["charge_percent"]}%')
    else:
        st.error("Response is not valid JSON. See raw response above.")
