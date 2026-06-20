import streamlit  as st
from src.Database.db import enroll_student_to_subject
from src.Database.config import supabase
import time

@st.dialog("Quick enrollment")
def auto_enroll_dilogue(subject_code):
    student_id = st.session_state.student_data['student_id']

    res = supabase.table('subjects').select('subject_id,name').eq('subject_code',subject_code).execute()
    if not res.data:
        st.error('subject code not found!')
        if st.button('close'):
            st.query_params.clear()
            st.rerun()
        return 
    subject = res.data[0]#mtlb ager mil jata h code tab

    check = supabase.table('subject_students').select('*').eq('subject_id',subject['subject_id']).eq('student_id',student_id).execute()
    if check.data:
       st.info("you are already enrolled")
       if st.button('Got It!'):
            st.query_params.clear()
            st.rerun()
       return
    st.markdown(f"would you like to enroll in **{subject['name']}**?")

    col1,col2 = st.columns(2)
    with col1:
        if st.button('NO Thanks'):
            st.query_params.clear()
            st.rerun()
    with col2:
        if st.button('yes enroll now',type='primary',width='stretch'):
            enroll_student_to_subject(student_id,subject['subject_id'])
            st.success("joined succesfully!")
            st.query_params.clear()
            time.sleep(2)
            st.rerun()
       




  
      
          
    