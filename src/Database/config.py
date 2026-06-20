import streamlit as st

from supabase import create_client, Client

supabase: Client = create_client(
    st.secrets["SUPABASE_URL"], 
    st.secrets["SUPABASE_KEY"]
) #create client leta h url or key jo secrete.toml m h  ##database instance bngaya

 