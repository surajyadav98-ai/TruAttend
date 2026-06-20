import streamlit  as st
from src.Database.db import enroll_student_to_subject
from src.Database.config import supabase
import time

@st.dialog("enroll in subject")
def enroll_dialog():
   st.write('Enter the subject code provided by your teacher to enroll')
   join_code = st.text_input('subject_code',placeholder='Eg CS101')

   if st.button("Enroll Now",type='primary',width='stretch'):
      if join_code: #check kre ki kya wo subject exist bhi krta h tabhi to enroll krenge
         res = supabase.table('subjects').select('subject_id','name','subject_code').eq('subject_code',join_code).execute()
         if res.data:
            subject = res.data[0]
            student_id = st.session_state.student_data['student_id'] #stuent id phe to exist nhi krti to session state se stid nikalete h check krne k lie
            check = supabase.table('subject_students').select('*').eq('subject_id',subject['subject_id']).eq('student_id',student_id).execute()
            if check.data:
               st.warning('you are already enrolled in this program')
            else:
               enroll_student_to_subject(student_id,subject['subject_id'])
               st.success("succesfully enolled!")
               time.sleep(1)
               st.rerun()
      else:
         st.warning('please enter a subject code')
      
          
    