from datetime import datetime
from turtle import pd

import streamlit as st
from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card
from src.Database.db import teacher_login,check_teacher_exist,get_teacher_subject,create_teacher,get_attandence_for_teacher
from src.components.diaogue_create_subject import create_subject_dialogue
from src.components.dialogue_share_subject import share_subject_dialog
from src.pipelines.face_pipeline import predict_attendance
from src.components.dialog_add_photos import add_photos_dialog
from src.Database.config import supabase
from src.pipelines.face_pipeline import predict_attendance
from src.components.dialoge_attandence_result import attandence_result_dialog
import numpy as np
import pandas as pd
from src.components.dialoge_voice_attandence import dialog_voice_attandence

def teacher_screen():

    style_background_dashboard()
    style_base_layout()
    
    if "teacher_data" in st.session_state:
        teacher_dashboard()#mtl teacher login ho chuka h to dashboard dikhao
    elif 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type=="login":
         teacher_screen_login()

    elif st.session_state.teacher_login_type == "register":
         teacher_screen_register()
    

def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    c1,c2, = st.columns(2,vertical_alignment = 'center',gap = 'xlarge')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"""welcome,{teacher_data['name']}""",text_alignment='center')

        if st.button('logout',type = "secondary",key = 'loginbackbtn',shortcut='control+backspace'):
            st.session_state['is_logged_in'] = False
            del st.session_state.teacher_data
            st.rerun()

    st.space()
    if "current_teacher_tab" not in st.session_state:
     st.session_state.current_teacher_tab = 'Take Attandence'
    tab1,tab2,tab3 = st.columns(3)
    
    with tab1:
       type1 = "primary" if st.session_state.current_teacher_tab == 'Take Attandence' else "tertiary"
       if  st.button("Take Attandence",type=type1,width = "stretch",icon = ':material/ar_on_you:'):
          st.session_state.current_teacher_tab = 'Take Attandence'
          st.rerun()

    with tab2:
       type2 =  "primary" if st.session_state.current_teacher_tab == 'Manage_subject' else "tertiary"
       if  st.button("Manage_subject",type = type2,width = "stretch",icon = ':material/book_ribbon:'):
          st.session_state.current_teacher_tab = 'Manage_subject'
          st.rerun()

    with tab3:
       type3 = "primary" if st.session_state.current_teacher_tab == 'Attandence_records' else "tertiary"
       if  st.button("Attandence Records",type = type3,width = "stretch",icon = ':material/cards_stack:'):
          st.session_state.current_teacher_tab = 'Attandence_records'
          st.rerun()

    st.divider()

    if st.session_state.current_teacher_tab == "Take Attandence":
        teacher_tab_take_attandence()
    
    if st.session_state.current_teacher_tab == "Manage_subject":
        teacher_tab_manage_subject()
    
    if st.session_state.current_teacher_tab == "Attandence_records":
        teacher_tab_Attandence_records()

    

    
    footer_dashboard()

def teacher_tab_take_attandence():
    teacher_id = st.session_state.teacher_data['teacher_id'] #teacher k data le liea
    st.header("Take Ai Attandence")

    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images=[]

    subjects = get_teacher_subject(teacher_id)
    if not subjects:
        st.warning("you havent create any subject yest! please create one to login!")
        return
    subject_options = {f"{s['name']}-{s['subject_code']}":s['subject_id'] for s in subjects}

    col1,col2 = st.columns([3,1],vertical_alignment='bottom')# mtlb box size to first k 3 aur 1 

    with col1:
        selected_subjects_label = st.selectbox('Select Subject',options=list(subject_options.keys()))#dict ko key m dlm k lie
    with col2:
        if st.button('Add photos',type = 'primary',icon='📷',width='stretch'):
            add_photos_dialog()

    selected_subject_id = subject_options[selected_subjects_label] 
    st.divider()

    if st.session_state.attendance_images:
        st.header('Added photos')
        gallery_cols = st.columns(4)

        for idx, img in enumerate(st.session_state.attendance_images): #idx isle kuki unke id ke base pr respected column m phli photo col1 m dusi col2 m ese
            with gallery_cols[idx % 4]:
                st.image(img, width='stretch',caption=f"photo {idx+1}")
                has_photos = bool(st.session_state.attendance_images)


    c1,c2,c3 = st.columns(3)
    has_photos = bool(st.session_state.attendance_images)

    with c1:
        if st.button('clear photos',width='stretch',type='tertiary',icon=':material/delete:',disabled = not has_photos):
            st.session_state.attendance_images=[]
            st.rerun()

    with c2:
        has_photos = bool(st.session_state.attendance_images)#ager ek bhi photo h to true wrna false
        if st.button('Run Face Analysis',width='stretch',type='secondary',icon=':material/analytics:',disabled= not has_photos):
            with st.spinner("Deep Scanning Classroom photos...."):
                all_detected_id = {}

                for idx,img in enumerate(st.session_state.attendance_images):

                    img_np = np.array(img.convert('RGB')) #rgv m convert krne se mofdel k lie procesing krn easy hota hai
                    detected,_,_ = predict_attendance(img_np)


                    if detected:
                        for sid in detected.keys():
                            student_id = int(sid)

                            all_detected_id.setdefault(student_id,[]).append(f"photo{idx+1}")
                
                enrolled_res = supabase.table('subject_students').select("*,students(*)").eq('subject_id',selected_subject_id).execute()

                enrolled_students = enrolled_res.data

                if not enrolled_students:
                    st.warning('No student enrolled in this course')
                else:
                    results,attandance_to_log = [],[]

                    curent_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    for node in enrolled_students:
                        student = node['students']
                        sources = all_detected_id.get(int(student['student_id']),[])#ager ek bnda multiple photo m  mila to uske sare source milega
                        is_present = len(sources)>0

                        results.append({
                            "Name":student['name'],
                            "ID":student['student_id'],
                            "Sources":",".join(sources) if is_present else "-", #ager prsnt h tabhi dikhyenge comma seprate m
                            "status":"Present✅" if is_present else "Absent❌"
                        })
                        attandance_to_log.append({
                            "student_id":student['student_id'],
                            "subject_id":selected_subject_id,
                            "timestamp":curent_timestamp,
                            "is_present":bool(is_present)
                        })
                
                    attandence_result_dialog(pd.DataFrame(results),attandance_to_log)
    with c3:
        if st.button("voice_input",width = 'stretch',type='primary',icon='🎤'):
            dialog_voice_attandence(selected_subject_id)



                        
                      
                    
                      

                

                    
                

        
        




def teacher_tab_manage_subject():
    teacher_id  = st.session_state.teacher_data["teacher_id"]
    col1,col2 = st.columns(2)
    with col1:
        st.header("Manage Subjects")
    with col2:
       if st.button("ceate a new subject",width= "stretch"):
           create_subject_dialogue(teacher_id)
    #List of all subject
    subjects = get_teacher_subject(teacher_id)
    if subjects:
      for sub in subjects:

        stats = [
            ("👥", "Students", sub['total_students']),
            ("🎯", "Classes", sub['total_classes'])
        ]
        def share_btn():
            if st.button(f"Share_code:{sub['name']}",key=f"share_{sub['subject_code']}",icon="📤"):
             share_subject_dialog(sub['name'],sub['subject_code'])
        st.space()
        subject_card(
            name=sub['name'],
            code=sub['subject_code'],
            section=sub['section'],
            stats=stats,
            footer_callback= share_btn
            
        )

        st.divider()

    else:
      st.info("NO SUBJECT FOUND CREATE ONE ABOVE")




    
def teacher_tab_Attandence_records():

    st.header("Attandence Records")
    
    teacher_id = st.session_state.teacher_data['teacher_id']
    records = get_attandence_for_teacher(teacher_id)

    if not records:
        return
    
    data = []

    for r in records:
        ts = r.get('timestamp')

        data.append({ #timestamp ko readable format m convert krne k lie
            "its_group":ts.split(".")[0] if ts else None, #miliscnd ko nikaldia uusse digerence aaskta ek hi time pr n hone se bhi
            "Time":datetime.fromisoformat(ts).strftime("%y-%m-%d %I:%M %p") if ts else "N'A",
            "Subject":r['subject']['name'],
            "Subject_Code":r['subjects']['subject_code'],
            "is_present":bool(r.get('is_present',False))

        })
    df = pd.DataFrame(data)

    summary = (
        df.groupby(["its_group","Time","Subject","Subject_Code"])
        .agg(
            Present_Count = {"is_present","sum"},
            Total_Count = ("is_present","count")
        ).reset_index()

    )
    summary["Attandence Stats"] = (
        "✅"+ summary["Present_Count"].astype(str) + "/" + summary["Total_Count"].astype(str)+'Students'
    )
    display_df = (summary.sort_values(by="its_group",ascending=False)
                  [['Time','Subject','Subject_Code','Attandence Stats']]
    )
    st.dataframe(display_df,width='stretch',hide_index=True)
 


def login_teacher(username,password):
    if not username or not password:
        return False
    teacher = teacher_login(username,password)
    if teacher:
        teacher = teacher_login(username,password)
        st.session_state.user_role = "teacher"
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True

    return False

def teacher_screen_login():
    c1,c2, = st.columns(2,vertical_alignment = 'center',gap = 'xlarge')
    with c1:
        header_dashboard()
    with c2:
       if st.button('Go back to Home',type = "secondary",key = 'loginbackbtn',shortcut='control+backspace'):
            st.session_state['login_type'] = None
            st.rerun()

    st.header("Login using password",text_alignment='center')
    st.space()
    st.space()
    teacher_username = st.text_input("Enter Username",placeholder="shweta malik")
    teacher_password = st.text_input("Enter Password",placeholder="password",type = 'password')

    st.divider()

    bt1,bt2 = st.columns(2)
    with bt1:
        if st.button('Login',icon =':material/passkey:',shortcut= 'control+enter',width = 'stretch'):
            if login_teacher(teacher_username,teacher_password):
                st.toast("Welcome back "+teacher_username,icon="👋")
                import time
                time.sleep(2)
                st.rerun()

            else:
                st.error("Invalid username or password")

    with bt2:
        if st.button('Registered instead',type = 'primary',icon =':material/passkey:',width = 'stretch'):
            st.session_state.teacher_login_type = "register"
        

    footer_dashboard()


from src.Database.db import check_teacher_exist, teacher_login
from src.Database.db import create_teacher
def register_teacher(teacher_username,teacher_password,teacher_name,teacher_pass_confirm):
    if not teacher_username or not teacher_name or not teacher_password or not teacher_pass_confirm:
        return False, "ALL fields are required"
    if check_teacher_exist(teacher_username):
        return False, "Teacher with this username already exists"
    if teacher_password != teacher_pass_confirm:
        return False, "Sorry password did not match"
    try:
      create_teacher(teacher_username,teacher_password,teacher_name)
      return True,"Successfully created login now!"
    except Exception as e:
        return False, "Unexpected error"
    
   
 
def teacher_screen_register():
    c1,c2, = st.columns(2,vertical_alignment = 'center',gap = 'xlarge')
    with c1:
        header_dashboard()
    with c2:
      st.button('Go back to Home',type = "secondary",key = 'loginbackbtn',shortcut='control+backspace')
        

    st.header("Register your teacher profile",text_alignment='center')

    st.space()
    st.space()
    teacher_username = st.text_input("Enter Username",placeholder="shweta malik")
    teacher_name = st.text_input("Enter your Name",placeholder="shweta malik")
    teacher_password = st.text_input("Enter Password",placeholder="password",type = 'password')
    teacher_pass_confirm = st.text_input("Confirm your Password",placeholder="confirm password",type = 'password')

    st.divider()

    bt1,bt2 = st.columns(2)
    with bt1:
        if st.button('Register now',icon =':material/passkey:',shortcut= 'control+enter',width = 'stretch'):
            success ,message = register_teacher(teacher_username,teacher_password,teacher_name,teacher_pass_confirm)
            if success:
                st.success(message)
                import time
                time.sleep(2)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else:
                st.error(message)
    with bt2:
       if st.button('Login instead',type = 'primary',icon =':material/passkey:',width = 'stretch'):
            st.session_state.teacher_login_type = "login"

    footer_dashboard()
            
    
    