import streamlit  as st
from src.Database.db import create_subjects

@st.dialog("Create New Subject")
def create_subject_dialogue(teacher_id):
    st.write("enter thre detail of new subbject")
    sub_id = st.text_input("subject_code",placeholder="CS101")
    sub_name = st.text_input("subject_name",placeholder="Introduction Machine Learning")
    sub_section = st.text_input("Section",placeholder="A")

    if st.button("Create Subject Now",type= "primary",width="stretch",):
        if sub_id and sub_name and sub_section:
            try:
                create_subjects(sub_id,sub_name,sub_section,teacher_id)
                st.toast("create subject succesfuully!")
                st.rerun()
            except Exception as e:
                st.error(f"ERROR:{str(e)}")

        else:
            st.warning("please fill all required field")