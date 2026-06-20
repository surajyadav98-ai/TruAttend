from resemblyzer import VoiceEncoder,preprocess_wav
import numpy as np
import io
import librosa
import streamlit as st

def load_voice_encoder():
    return VoiceEncoder()

def get_voice_embedding(audio_bytes):#hne embedding nikaldia mtlb number m krdi voice conv
    try:
        encoder = load_voice_encoder()

        audio,sr = librosa.load(io.BytesIO(audio_bytes),sr=16000)      #audio or sample-rate
        wav = preprocess_wav(audio)
        embedding = encoder.embed_utterance(wav)
        return embedding.tolist()
    except Exception as e:
        st.error('voice recorg error')
        return None
    
def identify_speaker(new_embedding,candidate_dict,threshold=0.40):#thrushold me dot prodoct nikale aur match krte h isse kam hue to sahi h
    if new_embedding is None or not candidate_dict:
        return None ,0.0
    best_stid = None
    best_score = -1

    for sid,store_embadding in candidate_dict.items():
        if store_embadding:
            similarity = np.dot(new_embedding,store_embadding)
            if similarity>best_score:
                best_score=similarity
                best_stid = sid

    

    if best_score >= threshold:
        return best_score,best_stid
    
    return None,best_score

def process_bulk_audio(audio_bytes,candidate_dict,thrushold=0.40):
     
    try:
       encoder = load_voice_encoder()

       audio,sr = librosa.load(io.BytesIO(audio_bytes),sr = 16000)
       segments = librosa.effects.split(audio,top_db= 30)#topdb mtlb sensitivity dekhta like  jo slow bolo usk bhi ager ise bada denge to chillakr bolega usi ko rekhega captur krega

       identified_result = {}

       for start ,end in segments:
           
            if(end-start) < sr*0.5: # mtlb wo noise h faltu awaz h slow si koi mtlb nhi h
               continue 
           
            segment_audio = audio[start:end]
            wav = preprocess_wav(segment_audio)
            embedding = encoder.embed_utterance(wav)

            sid,score = identify_speaker(embedding,candidate_dict,thrushold)

            if sid:
                if sid not in identified_result or score > identified_result[sid]:
                    identified_result[sid] = score

       return identified_result
    except Exception as e:
        st.error("bulk process error:{e}")
        print(f"ERROR:{e}")
        return {}
        
               




            
