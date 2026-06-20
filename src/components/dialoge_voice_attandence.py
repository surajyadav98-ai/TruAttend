from datetime import datetime
from src.components.dialoge_attandence_result import show_attendence_results
from src.pipelines.voice_pipeline import process_bulk_audio
import pandas as pd
import streamlit as st
from  src.Database.config import supabase


@st.dialog("voice attandence")
def dialog_voice_attandence(selected_subject_id):
    st.write("record audio of student for attandece")

    audio_data = None
    audio_data = st.audio_input("record classroom audio")

    if st.button("Analyze_audio",type="primary",width="stretch"):
        with st.spinner("Analyzing data..."):
            enrolled_res = supabase.table('subject_students').select("*,students(*)").eq('subject_id',selected_subject_id).execute()
            enrolled_students = enrolled_res.data

            if not enrolled_students:
                st.warning('No student enrolled in this course')
                return
            candidate_dict = {
                 s['students']['student_id']: s['students']['voice_embedding'] #map student IDs to their voice embeddings
                 for s in enrolled_students if s['students'].get("voice_embedding")
            }
            if not candidate_dict:
                st.error('No students registered with voice profiles')
                return
            audio_bytes = audio_data.read()
            detected_score = process_bulk_audio(audio_bytes,candidate_dict)

            results,attandance_to_log = [],[]

            curent_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for node in enrolled_students:
                student = node['students']
                score = detected_score.get(student['student_id'],0.0)#ager ek bnda multiple photo m  mila to uske sare source milega
                is_present = bool(score)>0

                results.append({
                                "Name":student['name'],
                                "ID":student['student_id'],
                                "Sources":score if is_present else "-", #ager prsnt h tabhi dikhyenge comma seprate m
                                "status":"Present✅" if is_present else "Absent❌"
                            })
                attandance_to_log.append({
                                "student_id":student['student_id'],
                                "subject_id":selected_subject_id,
                                "timestamp":curent_timestamp,
                                "is_present":bool(is_present)
                            })
            st.session_state.voice_attandence_results = (pd.DataFrame(results),attandance_to_log)

    if st.session_state.get("voice_attandence_results"):
        st.divider()
        df_results,logs = st.session_state.voice_attandence_results
        show_attendence_results(df_results,logs)