import streamlit as st

def header_home():
   logo_url = "https://i.ibb.co/8L10ShpV/Whats-App-Image-2026-06-20-at-6-31-17-PM.jpg"
   st.markdown(f"""
    <div style = "display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 30px; margin-top: 10px">   
      <img src = '{logo_url}' style="height:180px;border-radius: 50px;" />
      <h1 style = 'text-align: center; color:#E0E3FF'>Tru<br/> Attend</h1>
</div>
               """,unsafe_allow_html=True)
   

def header_dashboard():
   logo_url = "https://i.ibb.co/8L10ShpV/Whats-App-Image-2026-06-20-at-6-31-17-PM.jpg" 

   st.markdown(f"""
    <div style = "display: flex;  align-items: center; justify-content: center; gap:0px;">   
      <img src = '{logo_url}' style="height:80px;border-radius: 50px;" />
      <h2 style = 'text-align: left; color:#5865F2;line-height: 1.1;font-size: 1rem !important;'>Tru <br/>Attend</h2>
      
</div>
               """,unsafe_allow_html=True)
