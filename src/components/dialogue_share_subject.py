import streamlit  as st
import segno
import io
@st.dialog("Share class link")
def share_subject_dialog(subject_name,subject_code):
   app_domain = "snapclass.streamlit.app"
   join_url = f"{app_domain}/?join-code={subject_code}"
   st.header

   st.header("Scan to Join")
   qr = segno.make(join_url)
   out = io.BytesIO()
   qr.save(out,kind='png',scale=10,border=1)

   col1,col2 = st.columns(2)

   with col1:
      st.markdown('### copy link')
      st.code(join_url,language='text')
      st.code(subject_code,language= 'text')
      st.info('copy this link to share on Watshup or Email')

   with col2:
      st.markdown('### scan to join')
      st.image(out.getvalue())