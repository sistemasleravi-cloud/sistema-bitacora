import streamlit as st

R   = "#C8102E"
RDK = "#A50D26"
NEG = "#0A0A0A"
INK = "#0F0F0F"
GRI = "#8A8A8A"
GRL = "#E2E2E5"
FON = "#F4F4F6"
BLA = "#FFFFFF"
VER = "#16A34A"
AMA = "#D97706"
PEL = "#DC2626"
FH  = "'Bebas Neue', sans-serif"
FB  = "'Inter', sans-serif"
TASK_COLORS = [R, "#B00E27", "#980C21", "#800A1C", "#680817"]

def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Bebas+Neue&display=swap');

    :root {
        --rojo:     #C8102E;
        --rojo-dk:  #A50D26;
        --negro:    #0A0A0A;
        --ink:      #0F0F0F;
        --surface:  #161616;
        --mid:      #1E1E1E;
        --borde:    #2A2A2A;
        --gris-d:   #5A5A5A;
        --gris:     #8A8A8A;
        --gris-l:   #C8C8C8;
        --fondo:    #F4F4F6;
        --blanco:   #FFFFFF;
        --card:     #FFFFFF;
        --verde:    #16A34A;
        --amarillo: #D97706;
        --danger:   #DC2626;
        --r:        8px;
        --t:        all 0.15s ease;
        --sh:       0 1px 2px rgba(0,0,0,0.06), 0 2px 8px rgba(0,0,0,0.05);
        --sh-md:    0 4px 20px rgba(0,0,0,0.08);
        --font:     'Inter', sans-serif;
        --font-d:   'Bebas Neue', sans-serif;
    }

    *, *::before, *::after { box-sizing: border-box; }
    html, body, [class*="css"] { font-family: var(--font) !important; }

    #MainMenu, footer { visibility: hidden; }

    .stApp { background: var(--fondo) !important; }
    .block-container {
        padding: 2.5rem 3rem 4rem 3rem !important;
        max-width: 1320px !important;
        margin: 0 auto !important;
    }

    [data-testid="stSidebar"] {
        background: var(--negro) !important;
        border-right: 1px solid var(--borde) !important;
        width: 240px !important;
        min-width: 240px !important;
    }
    [data-testid="stSidebar"] > div:first-child { padding: 0 !important; }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: var(--gris) !important;
    }

    [data-testid="stSidebar"] .stRadio > div {
        flex-direction: column !important;
        gap: 0 !important;
    }

    [data-testid="stSidebar"] .stRadio > div > label {
        display: flex !important;
        align-items: center !important;
        padding: 0.72rem 1.4rem !important;
        margin: 0 !important;
        border-radius: 0 !important;
        background: transparent !important;
        border-left: 2px solid transparent !important;
        cursor: pointer !important;
        transition: var(--t) !important;
    }
    [data-testid="stSidebar"] .stRadio > div > label:hover {
        background: rgba(255,255,255,0.04) !important;
        border-left-color: var(--gris-d) !important;
    }
    [data-testid="stSidebar"] .stRadio p {
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        color: #AAAAAA !important;
        letter-spacing: 0 !important;
        text-transform: none !important;
        margin: 0 !important;
        opacity: 1 !important;
    }

    [data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        border: 1px solid var(--borde) !important;
        color: var(--gris-d) !important;
        font-family: var(--font) !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
        padding: 0.5rem 1rem !important;
        border-radius: 4px !important;
        box-shadow: none !important;
        width: 100% !important;
        transition: var(--t) !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        border-color: var(--rojo) !important;
        color: var(--rojo) !important;
        background: rgba(200,16,46,0.05) !important;
        transform: none !important;
        box-shadow: none !important;
    }

    .stButton > button {
        background: var(--rojo) !important;
        color: var(--blanco) !important;
        border: none !important;
        border-radius: 6px !important;
        font-family: var(--font) !important;
        font-size: 0.76rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        padding: 0.62rem 1.5rem !important;
        height: auto !important;
        min-height: 2.5rem !important;
        white-space: normal !important;
        line-height: 1.35 !important;
        box-shadow: 0 1px 3px rgba(200,16,46,0.30) !important;
        transition: var(--t) !important;
    }
    .stButton > button:hover {
        background: var(--rojo-dk) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(200,16,46,0.36) !important;
    }
    .stButton > button:active { transform: translateY(0) !important; }

    [data-testid="stForm"] {
        background: var(--card) !important;
        border: 1px solid #E8E8EA !important;
        border-radius: var(--r) !important;
        padding: 2rem !important;
        box-shadow: var(--sh) !important;
    }

    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        border: 1.5px solid #E2E2E5 !important;
        border-radius: 6px !important;
        background: var(--fondo) !important;
        color: var(--ink) !important;
        font-family: var(--font) !important;
        font-size: 0.88rem !important;
        padding: 0.58rem 0.9rem !important;
        transition: var(--t) !important;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--rojo) !important;
        background: var(--blanco) !important;
        box-shadow: 0 0 0 3px rgba(200,16,46,0.10) !important;
        outline: none !important;
    }
    .stTextInput > div > div > input::placeholder { color: #B0B0B8 !important; }

    .stTextInput label,
    .stNumberInput label,
    .stSelectbox label {
        font-family: var(--font) !important;
        font-size: 0.7rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        color: var(--gris) !important;
    }

    .stSelectbox > div > div {
        border: 1.5px solid #E2E2E5 !important;
        border-radius: 6px !important;
        background: var(--fondo) !important;
        font-family: var(--font) !important;
        font-size: 0.88rem !important;
        transition: var(--t) !important;
    }
    .stSelectbox > div > div:focus-within {
        border-color: var(--rojo) !important;
        box-shadow: 0 0 0 3px rgba(200,16,46,0.10) !important;
    }

    .stNumberInput button {
        background: var(--fondo) !important;
        border: 1.5px solid #E2E2E5 !important;
        color: var(--ink) !important;
        min-height: unset !important;
        box-shadow: none !important;
        transition: var(--t) !important;
    }
    .stNumberInput button:hover {
        background: var(--rojo) !important;
        color: var(--blanco) !important;
        border-color: var(--rojo) !important;
        transform: none !important;
    }

    .stRadio > div { gap: 0.4rem !important; flex-wrap: wrap !important; }
    .stRadio label {
        background: var(--blanco) !important;
        border: 1.5px solid #E2E2E5 !important;
        border-radius: 6px !important;
        padding: 0.42rem 1.1rem !important;
        cursor: pointer !important;
        transition: var(--t) !important;
        box-shadow: var(--sh) !important;
    }
    .stRadio label:hover { border-color: var(--rojo) !important; }
    .stRadio p {
        font-family: var(--font) !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        color: var(--ink) !important;
        margin: 0 !important;
    }

    [data-testid="stSidebar"] .stRadio label {
        border-radius: 0 !important;
        border: none !important;
        border-left: 2px solid transparent !important;
        background: transparent !important;
        padding: 0.72rem 1.4rem !important;
        box-shadow: none !important;
    }

    h1 {
        font-family: var(--font) !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
        color: var(--ink) !important;
        margin: 0 !important;
        line-height: 1.2 !important;
    }
    h2 {
        font-family: var(--font) !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em !important;
        color: var(--ink) !important;
        margin: 0 !important;
    }
    h3 {
        font-family: var(--font) !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        color: var(--gris) !important;
        margin: 0 !important;
    }

    [data-testid="stDataFrame"] {
        border-radius: var(--r) !important;
        overflow: hidden !important;
        box-shadow: var(--sh) !important;
        border: 1px solid #E8E8EA !important;
    }

    [data-testid="stAlert"] {
        border-radius: 6px !important;
        font-family: var(--font) !important;
        font-size: 0.84rem !important;
    }

    [data-testid="stPlotlyChart"] {
        background: var(--blanco) !important;
        border: 1px solid #E8E8EA !important;
        border-radius: var(--r) !important;
        overflow: hidden !important;
        box-shadow: var(--sh) !important;
    }

    [data-testid="column"] { padding: 0 0.4rem !important; }

    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #D0D0D5; border-radius: 2px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--rojo); }
    </style>
    """, unsafe_allow_html=True)