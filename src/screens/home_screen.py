import streamlit as st
from src.components.header import header_home
from src.ui.base_layout import style_base_layout,style_background_home
from src.components.footer import footer_home

def home_screen():
    # st.header('Welcome to the home Screen')

    header_home()
    style_base_layout()
    style_background_home()

    col1 , col2 = st.columns(2,gap = "large")
    with col1:
       st.header("I'm Student",width=310)
       st.image("https://i.ibb.co/3y0qM47J/Chat-GPT-Image-Apr-23-2026-02-52-13-PM.png",width=240)
       if st.button('student poertal',type = 'primary',icon =':material/arrow_outward:',icon_position='right'):
            st.session_state['login_type'] = 'student'
            st.rerun()


    with col2:
       st.header("I'm Teacher",width = 310)
       st.image("https://i.ibb.co/PsV0Z45G/Chat-GPT-Image-Apr-23-2026-03-01-22-PM.png",width=240)
       if st.button('teacher poertal',type = 'primary',icon =':material/arrow_outward:',icon_position='right'):
           st.session_state['login_type'] = 'teacher'
           st.rerun()

    footer_home()