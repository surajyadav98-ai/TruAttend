# from src.Database.config import supabase
from src.Database.config import supabase
import bcrypt


def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode(),bcrypt.gensalt()).decode()

def check_pass(pwd,hashed_pwd):
    return bcrypt.checkpw(pwd.encode(),hashed_pwd.encode())

def check_teacher_exist(username):
    #check for unique user return false if user already exst 
    response = supabase.table("teachers").select("username").eq("username",username).execute()
    return len(response.data) > 0


def create_teacher(username,password,name):
   
    data = {"username":username,"password":hash_pass(password),"name":name}
    response = supabase.table("teachers").insert(data).execute()
    return response.data

def teacher_login(username,password):
    response = supabase.table("teachers").select("*").eq("username",username).execute()
    if response.data:
        teacher = response.data[0] #username mil gaya h array m aata jo pehla wo hi isle 0
        if check_pass(password,teacher["password"]):
            return teacher
    return None
def get_all_student():
    response = supabase.table("students").select("*").execute()
    return response.data

def create_students(new_name,face_embadding=None,voice_embedding=None):
    data = {"name":new_name,"face_embedding":face_embadding,'voice_embedding':voice_embedding}
    response = supabase.table("students").insert(data).execute()
    return response.data

def create_subjects(subject_code,name,section,teacher_id):
    data = {"subject_code":subject_code,"name":name,"section":section,"teacher_id":teacher_id}
    response = supabase.table("subjects").insert(data).execute()
    return response.data

def get_teacher_subject(teacher_id):
    response = supabase.table('subjects').select("*,subject_students(count),attendance_logs(timestamp)").eq("teacher_id",teacher_id).execute()
    subjects = response.data

    for sub in subjects:
        sub['total_students'] = sub.get("subject_students",[{}])[0].get('count',0) if sub.get('subject_students') else 0 #[{}] folback mtlb nhi mla empty array or count mtlb nhi mila to 0
        attendance = sub.get('attendance_logs',[])
        unique_session = len(set(log['timestamp'] for log in attendance))
        sub['total_classes'] = unique_session


        sub.pop('subject_students',None)
        sub.pop('attendance_logs',None)

    return subjects

def enroll_student_to_subject(student_id,subject_id):
    data = {"student_id":student_id,"subject_id":subject_id}
    response = supabase.table('subject_students').insert(data).execute()
    return response.data

def unenroll_student_to_subject(student_id,subject_id):
    response = supabase.table('subject_students').delete().eq('student_id',student_id).eq('subject_id',subject_id).execute()
    return response.data

def get_student_subject(student_id):
    response = supabase.table('subject_students').select('*,subjects(*)').eq('student_id',student_id).execute()
    return response.data

def get_student_attandance(student_id):
    response = supabase.table('attendance_logs').select('*,subjects(*)').eq('student_id',student_id).execute()
    return response.data

def create_attendence_logs(logs):
    response = supabase.table('attendance_logs').insert(logs).execute()
    return response.data

def get_attandence_for_teacher(teacher_id):
    response = supabase.table('attendance_logs').select('*,subjects!inner(*)').eq('subjects.teacher_id',teacher_id).execute()
    return response.data