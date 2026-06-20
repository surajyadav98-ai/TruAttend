import streamlit  as st
from src.Database.db import enroll_student_to_subject
from src.Database.config import supabase
from src.Database.db import create_attendence_logs
import time
def show_attendence_results(df,logs):
            st.write("please review attandance before confirming")
            st.dataframe(df,hide_index=True,width='stretch')

            col1,col2 = st.columns(2)

            with col1:
                if st.button('descard',width='stretch'):
                    st.session_state.voice_attendance_results = None
                    st.session_state.attendance_images = []
                    st.rerun()

            with col2:
                if st.button('confirm & save',width='stretch',type='primary'):
                    try:
                       create_attendence_logs(logs)
                       st.toast('attandence taken')
                       st.session_state.attendance_images = []
                       st.session_state.voice_attendance_results = None
                       st.rerun()
                    except Exception as e:
                     st.error('sync failed')
        
@st.dialog("Attandance results")
def attandence_result_dialog(df,logs):
    show_attendence_results(df,logs)

        