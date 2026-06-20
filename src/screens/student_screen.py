import streamlit as st
from PIL import Image
import numpy as np
from src.components.dilogue_enroll import enroll_dialog

from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.pipelines.face_pipeline import predict_attendance,get_face_embaddings,train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding
from src.Database.db import get_all_student,create_students,get_student_subject,get_student_attandance,unenroll_student_to_subject
from src.components.subject_card import subject_card
import time

def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data['student_id']
    c1,c2, = st.columns(2,vertical_alignment = 'center',gap = 'xlarge')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"""welcome,{student_data['name']}""",text_alignment='center')

        if st.button('logout',type = "secondary",key = 'loginbackbtn',shortcut='control+backspace'):
            st.session_state['is_logged_in'] = False
            del st.session_state.student_data
            st.rerun()

    st.space()
    c1,c2 = st.columns(2)
    with c1:
        st.header("your enrolled subjects")
    with c2:
        if st.button('Enroll in subject',type='primary',width='stretch',icon="📚"):
            enroll_dialog()

    st.divider()

    with st.spinner("Loading your enrolled subjects..."):
        subjects = get_student_subject(student_id)
        logs = get_student_attandance(student_id)

    stats_map = {}

    for log in logs:
        sid = log['subject_id']

        if sid not in stats_map:
            stats_map[sid] = {"total":0,"attended":0}

        stats_map[sid]['total'] +=1

        if log.get('is_present'):
            stats_map[sid]['attended'] +=1

    cols = st.columns(2)
    for i ,sub_node in enumerate(subjects):
        sub = sub_node['subjects']
        sid = sub['subject_id']

        stats = stats_map.get(sid,{"total":0,"attended":0})
        def unenroll_btn():
            if st.button("unenroll from the course",type='tertiary',width='stretch',icon='❌',key=f"unenroll_{sid}"):
                unenroll_student_to_subject(student_id,sid)
                st.toast(f"unenroll from {sub['name']}succesfully!")
                st.rerun()
            
        with cols[i%2]:
            subject_card(
                name = sub['name'],
                code = sub['subject_code'],
                section = sub['section'],
                stats= [
                    ('📅','Total',stats['total']),
                    ('✔️','Attended',stats['attended']),
                ],

                footer_callback=unenroll_btn
            )


   

    st.divider()

    footer_dashboard()
def student_screen():
    
    style_background_dashboard()
    style_base_layout()

    if "student_data" in st.session_state:
        student_dashboard()
        return

    c1,c2, = st.columns(2,vertical_alignment = 'center',gap = 'xlarge')
    with c1:
        header_dashboard()
    with c2:
       if st.button('Go back to Home',type = "secondary",key = 'loginbackbtn',shortcut='control+backspace'):
            st.session_state['login_type'] = None
            st.rerun()

    st.header("Login using Face_Id",text_alignment='center')
    st.space()
    st.space()

    show_registration = False
    photo_source = st.camera_input("position your face in the centre")
    if photo_source:
       img =  np.array(Image.open(photo_source))#ye line photo ko numpy array m convert kr rhi h taki uska use hum aage kr ske face recognition m

       with st.spinner('Ai is scanning..'): #spinner mtlb jabt tak saare fnctn chl nhi jaate y kuch return nh krte
           detected,all_ids,num_faces = predict_attendance(img)

           if num_faces == 0:
               st.warning('face not found!..')
           elif num_faces > 1:
               st.warning('multiple face found..')
           else:
               if detected:
                   student_id = list(detected.keys())[0]
                   all_student = get_all_student()
                   student = next((s for s in all_student if s['student_id']==student_id),None)

                   if student:
                    st.session_state['is_logged_in']= True
                    st.session_state['user_role'] = 'student'
                    st.session_state.student_data = student
                    st.toast(f"welcome back{student['name']}")
                    time.sleep(1)
                    st.rerun()
                    
               else:
                   st.info('Face not recognised! you might be a new student!')
                   show_registration = True

    if show_registration:
        with st.container(border = True):
            st.header('Register new profile')
            new_name = st.text_input("Enter your name",placeholder='E.g. suraj yadav')

            st.subheader('optional : voice Enrollment')
            st.info("Enroll your for voice only attendence")

            audio_data = None

            try:
                audio_data = st.audio_input("record a shot phrase like i am present,my name is suraj")
            except Exception:
                st.error('audio data failed')

            if st.button('Create account', type='primary'):
                if new_name:
                    with st.spinner('Creating Profile'):
                       img= np.array(Image.open(photo_source))
                       encoding = get_face_embaddings(img)

                       if encoding:
                           face_imb = encoding[0].tolist()

                           voice_emb = None
                           if audio_data:
                               voice_emb = get_voice_embedding(audio_data.read())

                           response_data = create_students(new_name,face_embadding=face_imb,voice_embedding=voice_emb)

                           if response_data:
                                train_classifier()
                                st.session_state.is_logged_in= True
                                st.session_state.user_log = 'student'
                                st.session_state.student_data = response_data[0]
                                st.toast(f"👋profile created! hey {new_name}")
                                time.sleep(1)
                                st.rerun()
                    st.error("couldnt capture your facial features for registration")

                else:
                    st.warning('please enter your name')
    
                   


    footer_dashboard()
    