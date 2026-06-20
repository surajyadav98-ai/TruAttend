import streamlit as st

def subject_card(name, code, section, stats=None, footer_callback=None):
    html = f"""
    <div style="background:white; border:1.5px solid black #cbd5e1; border-radius:10px; padding:20px 24px; margin-bottom:8px;">
        <h4 style="margin:0 0 8px 0; color:#1e293b; font-size:1.1rem; font-weight:600;">{name}</h4>
        <p style="margin:0 0 10px 0; color:#475569; font-size:0.9rem;">
            Code : <span style="background:#E0E3FF; color:#5865F2; padding:2px 8px; border-radius:6px; font-weight:600;">{code}</span>
            &nbsp;| Section : {section}
        </p>
    """
    
    if stats:
        html += '<div style="display:flex; gap:16px; flex-wrap:wrap; margin-bottom:4px;">'
        for icon, label, value in stats:
            html += f'<span style="color:#64748b; font-size:0.85rem;">{icon} <b>{value}</b> {label}</span>'
        html += '</div>'
    
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)
    
    if footer_callback:
        footer_callback()