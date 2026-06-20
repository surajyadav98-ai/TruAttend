import dlib #dlib k ans=der bhot model hote h 
import numpy as np
import face_recognition_models
import streamlit as st
from sklearn.svm import SVC
from src.Database.db import get_all_student# sabhi student k data se classify image classify mtlb

@st.cache_resource #ek baar hi install ho baarbaar nahi
def load_dlib_models():
    detector = dlib.get_frontal_face_detector()#upper upper face detect like boundary

    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()#face per jo point hote hai
    )

    facerec = dlib.face_recognition_model_v1( #iske bina kaam ho skta h dlib pr basic hota h y advance hota to efficent work karta h
         face_recognition_models.face_recognition_model_location()

    )

    return detector , sp , facerec

def get_face_embaddings(image_np):
    detector,sp,facerec = load_dlib_models()
    faces = detector(image_np,1) #1 isle ki ek baar hi process kre image wrn jada cpu lega

    encodings =[] #fir isme add hoga number

    for face in faces:
        shape = sp(image_np,face)#landmark nikaal lie face k
        face_descriptor = facerec.compute_face_descriptor(image_np,shape,1)#embading 128 mtlb dimension

        encodings.append(np.array(face_descriptor))

    return encodings

@st.cache_resource# heavy fnc to baar baar rerun na ho isle use mtlb baar baar data se connect n ho jab tak koi change n ho pehle wala hi purana data dete raho
def get_trained_model(): #embedding aur student id k base pr
    x = []
    y = []

    student_db = get_all_student()

    if not student_db:
        return None
    for student in student_db:
        embedding = student.get("face_embedding")
        if embedding:
            x.append(np.array(embedding))
            y.append(student.get("student_id"))

    if len(x) ==0:
        return 0
    
    clf = SVC(kernel = 'linear',probability=True,class_weight='balanced') #balance scale hi isle 
    try:
        clf.fit(x,y)
    except ValueError:
        pass
    return {'clf':clf,'x':x,'y':y}

def train_classifier(): #jab naya student add ho usse phle poorana data hi dete rhe isle cashe k use kiya
    st.cache_resource.clear()
    model_data = get_trained_model() #jab koi naya add kre to poorana wala casce clear hoke nya bne fir wahi deta ho jab tab koi dura kuch naya n ho
    return bool(model_data)

def predict_attendance(class_image_np):
    encodings = get_face_embaddings(class_image_np)

    detected_student = {}

    model_data = get_trained_model()

    if not model_data:
        return detected_student,[],len(encodings) #embedding ,student ki list , length
    
    clf = model_data['clf']
    x_train = model_data['x']
    y_train = model_data['y']

    all_student = sorted(list(set(y_train)))

    for encoding in encodings:
        if len(all_student)>=2:
            predicted_id = int(clf.predict([encoding])[0])

        else:
            predicted_id = int(all_student[0])

        student_embedding = x_train[y_train.index(predicted_id)]# ytrain k jis index pr jo studentid hogi usi pr embedding isle index se nikali embedding

        best_match_score = np.linalg.norm(student_embedding - encoding)#mera chra aur jo grp photo m chera mila h wo minus

        resemblance_threshold = 0.6# mtlb ager isse upper gya koi bhi vector to poora alag face different face h

        if best_match_score <= resemblance_threshold: #mtlb distance bhot kam h 
            detected_student[predicted_id] = True

    return detected_student,all_student,len(encodings)





      




