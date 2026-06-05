import streamlit as st
from config import FB, FH, R, GRI, GRL, NEG, BLA

def page_header(titulo, subtitulo=""):
    sub = f'<p style="font-family:{FB};font-size:0.84rem;color:{GRI};margin:0.35rem 0 0 0;font-weight:400;">{subtitulo}</p>' if subtitulo else ""
    st.markdown(f"""
        <div style="margin-bottom:2rem;padding-bottom:1.5rem;border-bottom:1px solid {GRL};">
            <div style="display:flex;align-items:center;gap:0.8rem;">
                <div style="width:3px;height:1.8rem;background:{R};border-radius:2px;flex-shrink:0;"></div>
                <div>
                    <h1>{titulo}</h1>
                    {sub}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def metric_card(col, label, valor):
    col.markdown(f"""
        <div style="background:{NEG};border-radius:8px;padding:1.5rem 1.8rem;
                    box-shadow:0 4px 24px rgba(0,0,0,0.22);position:relative;overflow:hidden;">
            <div style="position:absolute;inset:0 0 auto 0;height:2px;background:{R};"></div>
            <p style="font-family:{FB};font-size:0.65rem;font-weight:600;letter-spacing:0.14em;
                      text-transform:uppercase;color:#555;margin:0 0 0.6rem 0;">{label}</p>
            <p style="font-family:{FH};font-size:2.8rem;color:{BLA};margin:0;line-height:1;
                      letter-spacing:0.03em;">{valor}</p>
        </div>
    """, unsafe_allow_html=True)

def section_title(titulo, subtitulo=""):
    sub = f'<p style="font-family:{FB};font-size:0.8rem;color:{GRI};margin:0.2rem 0 0 0;">{subtitulo}</p>' if subtitulo else ""
    st.markdown(f"""
        <div style="margin:2.5rem 0 1.2rem 0;">
            <h2>{titulo}</h2>
            {sub}
        </div>
    """, unsafe_allow_html=True)

def row_card(col, contenido_html, borde_color=R):
    col.markdown(f"""
        <div style="background:{BLA};border:1px solid {GRL};border-left:3px solid {borde_color};
                    border-radius:8px;padding:0.9rem 1.2rem;margin-bottom:0.5rem;
                    box-shadow:0 1px 4px rgba(0,0,0,0.05);">
            {contenido_html}
        </div>
    """, unsafe_allow_html=True)