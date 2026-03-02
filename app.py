import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from scipy import stats
from sklearn.preprocessing import StandardScaler, LabelEncoder
import io
import statsmodels.api as sm
import streamlit.components.v1 as components
import base64
import os

def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

# Pre-load backgrounds
sidebar_img_base64 = get_base64_of_bin_file("sidebar_bg.png")
upload_bg_base64 = get_base64_of_bin_file("backgound1.png")

# ==========================================
# 1. Config & State Management
# ==========================================
st.set_page_config(page_title="Advanced Analytics Engine", page_icon="🧬", layout="wide")

# ==========================================
# 2. Styling & Layout (Absolute Top to Prevent Flickering)
# ==========================================
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
<style>
    /* 1. HIDE DEFAULT STATUS INDICATOR */
    [data-testid="stStatusWidget"], 
    .stStatusWidget {
        display: none !important;
        visibility: hidden !important;
    }

    .main { background-color: #f4f6f9; }
    
    /* ==========================================
       FIX: REDUCE TOP PADDING FOR MAIN CONTENT
       ========================================== */
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* ==========================================
       FIX: HEADER POSITION IN MAIN CONTENT
       ========================================== */
    section[data-testid="stMain"] > div > div > div > div:first-child {
        margin-top: 0 !important;
    }
    
    /* Enhanced Metric Cards */
    .stMetric { 
        background: white !important; 
        padding: 20px !important; 
        border-radius: 12px !important; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important; 
        border-top: 4px solid #3b82f6 !important;
    }
    .stMetric [data-testid="stMetricValue"] { font-size: 1.8rem !important; font-weight: 800 !important; color: #1e3a8a !important; }
    .stMetric [data-testid="stMetricLabel"] { font-size: 0.9rem !important; font-weight: 600 !important; color: #475569 !important; }
    
    /* ==========================================
       SIDEBAR STYLING - WHITE TEXT FOR ALL
       ========================================== */
    [data-testid="stSidebar"] {
        background-image: linear-gradient(rgba(15, 23, 42, 0.90), rgba(15, 23, 42, 0.95)), url("data:image/png;base64,%s");
        background-size: cover;
        background-position: center;
    }
    [data-testid="stSidebarContent"] { 
        padding-top: 0rem !important;
        color: #ffffff !important;
    }
    
    /* ALL TEXT IN SIDEBAR = WHITE */
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* ==========================================
       FIX: RED COLOR FOR PRO IN SIDEBAR
       ========================================== */
    [data-testid="stSidebar"] span[data-testid="stMarkdownContainer"] span {
        color: #ff4b4b !important;
    }
    
    /* Target specific red elements */
    [data-testid="stSidebar"] [style*="color: rgb(255, 75, 75)"],
    [data-testid="stSidebar"] [style*="color: #ff4b4b"],
    [data-testid="stSidebar"] [style*="color: #ef4444"] {
        color: #ff4b4b !important;
    }
    
    /* ==========================================
       FIX: WHITE TEXT FOR DATA UPLOAD HEADER
       ========================================== */
    .upload-header-white {
        color: #ffffff !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .upload-subheader-white {
        color: #e2e8f0 !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    
    /* SIDEBAR TITLE STYLING */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown {
        color: #ffffff !important;
    }
    
    /* RADIO BUTTON LABELS = WHITE */
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        padding: 8px 12px !important;
        border-radius: 8px !important;
        transition: all 0.2s !important;
        color: #ffffff !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background-color: rgba(255,255,255,0.15) !important;
        color: #ffffff !important;
    }
    
    /* ACTIVE/CHECKED STATE */
    [data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.3), rgba(37, 99, 235, 0.4)) !important;
        border-left: 3px solid #3b82f6 !important;
        color: #ffffff !important;
    }
    
    /* HIDE RADIO CIRCLE */
    [data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
        display: none !important;
    }
    
    /* GLOABL CARD HOVER EFFECTS */
    [data-testid="stMetric"], .custom-card {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: 1px solid transparent !important;
    }
    [data-testid="stMetric"]:hover, .custom-card:hover {
        transform: translateY(-5px) scale(1.01) !important;
        box-shadow: 0 12px 24px rgba(0,0,0,0.1) !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
    }
    
    .stButton>button { border-radius: 8px !important; font-weight: bold !important; }
    .log-container { background-color: #1e1e2e !important; color: #a6adc8 !important; padding: 12px !important; border-radius: 8px !important; font-family: monospace !important; border-left: 4px solid #94e2d5 !important; }
    
    /* Ensure the sidebar toggle specifically is visible */
    [data-testid="stSidebarCollapsedControl"] {
        visibility: visible !important;
        z-index: 999999 !important;
    }

    .stAppDeployButton { display:none !important; }
    [data-testid="stAppDeployButton"] { display: none !important; }
    
    /* Advanced EDA Radio Button Navigation Styling (Scoped to Main Body) */
    section[data-testid="stMain"] div[data-testid="stRadio"] div[role="radiogroup"] {
        display: flex;
        flex-direction: row;
        gap: 10px;
        background: transparent;
    }
    section[data-testid="stMain"] div[data-testid="stRadio"] div[role="radiogroup"] label {
        padding: 4px 10px !important;
        border-radius: 6px !important;
        font-size: 11px !important;
        cursor: pointer;
        transition: all 0.2s ease !important;
    }
    section[data-testid="stMain"] div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
        opacity: 0.9;
    }
    
    /* Hide the actual radio circle in main */
    section[data-testid="stMain"] div[data-testid="stRadio"] div[role="radiogroup"] label span[data-baseweb="radio"],
    section[data-testid="stMain"] div[data-testid="stRadio"] div[role="radiogroup"] label div[data-baseweb="radio"],
    section[data-testid="stMain"] div[data-testid="stRadio"] div[role="radiogroup"] label input[type="radio"],
    section[data-testid="stMain"] div[data-testid="stRadio"] div[role="radiogroup"] label > div:first-child:not(:has([data-testid="stMarkdownContainer"])) {
        display: none !important;
    }

    /* ACTIVE RED STATE IN MAIN */
    section[data-testid="stMain"] div[data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"],
    section[data-testid="stMain"] div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
        background: #ff4b4b !important;
        background-image: linear-gradient(to right, #ff4b4b, #ce1212) !important;
        border: 2px solid white !important;
        box-shadow: 0 0 15px rgba(255, 75, 75, 0.6) !important;
        color: white !important;
        font-weight: 900 !important;
        transform: scale(1.05) !important;
        filter: invert(1) hue-rotate(180deg) !important;
    }
    
    section[data-testid="stMain"] div[data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"] *,
    section[data-testid="stMain"] div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) * {
        color: white !important;
    }
    
    /* ==========================================
       FIX: PAGE HEADERS POSITION - ADD TOP MARGIN
       ========================================== */
    .page-header-container {
        margin-top: 2rem !important;
        margin-bottom: 1.5rem !important;
        padding-top: 1rem !important;
    }
    
    /* ==========================================
       DARK MODE TOGGLE BUTTON STYLING
       ========================================== */
    .dark-mode-toggle-container {
        position: fixed;
        bottom: 20px;
        left: 20px;
        z-index: 999999 !important;
    }
    
    /* Style for the toggle in sidebar */
    [data-testid="stSidebar"] [data-testid="stToggle"] {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
    [data-testid="stSidebar"] [data-testid="stToggle"] > div {
        background-color: #3b82f6 !important;
    }
</style>
""" % sidebar_img_base64, unsafe_allow_html=True)

# Initialize Session State
if 'df' not in st.session_state:
    st.session_state.df = None
if 'original_df' not in st.session_state:
    st.session_state.original_df = None
if 'log' not in st.session_state:
    st.session_state.log = ["Platform Initialized."]
if 'dx_selected_view' not in st.session_state:
    st.session_state.dx_selected_view = 0

def add_to_log(message):
    st.session_state.log.append(message)

def create_color_card(title, value, grad_from, grad_to, border_color, text_color="#111827", value_color="#111827", val_font_size="1.8rem"):
    return f"""
    <div class="custom-card" style='background: linear-gradient(135deg, {grad_from} 0%, {grad_to} 100%); padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border-top: 4px solid {border_color}; height: 115px; display: flex; flex-direction: column; justify-content: center;'>
        <div style='font-size: 14px; font-weight: 600; color: {text_color}; margin-bottom: 5px; opacity: 0.9;'>{title}</div>
        <div style='font-size: {val_font_size}; font-weight: 800; color: {value_color};'>{value}</div>
    </div>
    """

def styled_table(df, height=420, full_width=True):
    if hasattr(df, 'to_html'):
        html_table = df.to_html(index=False, border=0)
    else:
        html_table = df.to_html(index=False, border=0)
    
    width_val = "100%" if full_width else "fit-content"
    
    components.html(f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
      * {{ box-sizing: border-box; margin: 0; padding: 0; }}
      body {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background: #ffffff;
        font-size: 0.85rem;
      }}
      #top-scroll {{
        overflow-x: scroll;
        overflow-y: hidden;
        height: 12px;
        margin-bottom: 2px;
      }}
      #top-scroll-inner {{ height: 1px; }}
      #table-wrap {{
        overflow-x: scroll;
        overflow-y: auto;
        max-height: {height - 60}px;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        width: {width_val};
        max-width: 100%;
        min-width: 300px;
      }}
      table {{
        border-collapse: collapse;
        width: auto;
        min-width: 100%;
      }}
      thead th {{
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
        color: #ffffff;
        padding: 10px 18px;
        text-align: left;
        font-weight: 600;
        white-space: nowrap;
        position: sticky;
        top: 0;
        z-index: 2;
        border-right: 1px solid rgba(255,255,255,0.15);
      }}
      tbody td {{
        padding: 8px 18px;
        border-bottom: 1px solid #e5e7eb;
        white-space: nowrap;
        color: #111827;
        background-color: #ffffff;
      }}
      tbody tr:nth-child(even) td {{ background-color: #eff6ff; }}
      tbody tr:hover td {{ background-color: #dbeafe !important; }}
    </style>
    </head>
    <body>
      <div id="top-scroll"><div id="top-scroll-inner"></div></div>
      <div id="table-wrap">
        {html_table}
      </div>
      <script>
        const wrap = document.getElementById('table-wrap');
        const topScroll = document.getElementById('top-scroll');
        const topInner = document.getElementById('top-scroll-inner');
        function syncWidth() {{
          topInner.style.width = wrap.scrollWidth + 'px';
        }}
        syncWidth();
        new ResizeObserver(syncWidth).observe(wrap);
        wrap.onscroll = () => topScroll.scrollLeft = wrap.scrollLeft;
        topScroll.onscroll = () => wrap.scrollLeft = topScroll.scrollLeft;
      </script>
    </body>
    </html>
    """, height=height)

def to_excel(df):
    """تصدير DataFrame إلى Excel مع معالجة الأخطاء"""
    try:
        output = io.BytesIO()
        try:
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
        except Exception:
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
        output.seek(0)
        return output.getvalue()
    except Exception as e:
        st.error(f"خطأ في تصدير Excel: {e}")
        return df.to_csv(index=False).encode('utf-8')

# ==========================================
# SIDEBAR HEADER - MOVED TO TOP (NO MARGIN-TOP)
# ==========================================
with st.sidebar:
    # Header at the very top
    st.markdown("""
        <div style="text-align: center; margin-bottom: 0.5rem; margin-top: -1rem;">
            <h2 style="color: #ffffff; font-weight: 800; font-size: 1.2rem; margin-bottom: 0.3rem;">
                🧬 Advanced Analytics
            </h2>
            <p style="color: #94a3b8; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1.5px; margin: 0;">
                Data Intelligence Engine
            </p>
        </div>
        <hr style='margin: 0.5rem 0; border: none; border-top: 1px solid rgba(255,255,255,0.15);'>
    """, unsafe_allow_html=True)
    
    # ==========================================
    # DARK MODE TOGGLE - IN SIDEBAR (NO SETTINGS LABEL)
    # ==========================================
    dark_mode = st.toggle("🌙 Dark Mode", key="global_dark_mode")
    
    if dark_mode:
        st.markdown("""
        <style>
            html { filter: invert(1) hue-rotate(180deg); }
            img, video, iframe, canvas, svg { 
                filter: invert(1) hue-rotate(180deg); 
            }
            .upload-text-p,
            [data-testid="stFileUploader"] label, 
            [data-testid="stFileUploader"] label p,
            [data-testid="stFileUploaderText"] { 
                color: #1e293b !important; 
                font-weight: 600 !important; 
            }
            .upload-text-header { 
                color: #1e3a8a !important; 
                font-weight: 800 !important; 
            }
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid rgba(255,255,255,0.15);'>", unsafe_allow_html=True)

# ==========================================
# MENU - WHITE TEXT WITH RED PRO
# ==========================================
menu = st.sidebar.radio("", [
    "📂 Data Upload",
    "🔎 Data Exploration",
    "🛡️ Strategic Discovery :red[(Pro)]",
    "🧪 Data Quality Report :red[(Pro)]",
    "🧹 Data Cleaning :red[(Pro)]",
    "🔤 String Functions :red[(Pro)]",
    "🔢 Numeric Functions :red[(Pro)]",
    "📊 Visualization Studio :red[(Pro)]",
    "🔬 Statistical Testing :red[(Pro)]",
    "📝 Final Report & Export :red[(Pro)]"
])

# ==========================================
# 3. Module Definitions
# ==========================================

def render_pro_restriction(section_name):
    clean_section = section_name.replace(":red[(Pro)]", "").strip()
    st.markdown(f"""
        <style>
            @keyframes fadeInUp {{
                from {{ opacity: 0; transform: translateY(30px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            @keyframes pulseLock {{
                0% {{ transform: scale(1); }}
                50% {{ transform: scale(1.1); }}
                100% {{ transform: scale(1); }}
            }}
            .pro-card-container {{
                display: flex;
                justify-content: center;
                align-items: center;
                height: 70vh;
                perspective: 1000px;
            }}
            .pro-card {{
                background: var(--card-bg, rgba(255, 255, 255, 0.9));
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 24px;
                padding: 3rem;
                max-width: 550px;
                text-align: center;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1), 0 0 0 1px rgba(0,0,0,0.05);
                animation: fadeInUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
                transition: all 0.4s ease;
                position: relative;
                overflow: hidden;
            }}
            .pro-card::before {{
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0; height: 6px;
                background: linear-gradient(90deg, #6366f1, #ef4444);
            }}
            .pro-card:hover {{
                transform: translateY(-10px) scale(1.02);
                box-shadow: 0 30px 60px rgba(0,0,0,0.15);
                border-color: rgba(99, 102, 241, 0.3);
            }}
            .lock-icon {{
                font-size: 5rem;
                margin-bottom: 1.5rem;
                display: inline-block;
                animation: pulseLock 3s infinite ease-in-out;
            }}
            .section-title-badge {{
                display: inline-block;
                padding: 10px 24px;
                background: rgba(239, 68, 68, 0.1);
                color: #ef4444;
                border-radius: 100px;
                font-size: 1.8rem;
                font-weight: 800;
                margin-bottom: 1.5rem;
                letter-spacing: 1px;
            }}
            .pro-header {{
                font-size: 3.5rem;
                font-weight: 900;
                margin: 0.5rem 0;
                background: linear-gradient(135deg, #111827 30%, #4b5563);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .pro-description {{
                font-size: 1.2rem;
                color: #4b5563;
                line-height: 1.6;
                margin-top: 1rem;
            }}
            @media (prefers-color-scheme: dark) {{
                .pro-card {{
                    background: rgba(31, 41, 55, 0.8);
                    box-shadow: 0 20px 40px rgba(0,0,0,0.4);
                }}
                .pro-header {{
                    background: linear-gradient(135deg, #f9fafb 30%, #d1d5db);
                    -webkit-background-clip: text;
                }}
                .pro-description {{ color: #9ca3af; }}
            }}
        </style>
        <div class="pro-card-container">
            <div class="pro-card">
                <div class="lock-icon">🔒</div>
                <div class="section-title-badge">{clean_section}</div>
                <h1 class="pro-header">Pro</h1>
                <p class="pro-description">
                    This advanced intelligence module is exclusively available in the Pro Version.
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_data_upload():
    if upload_bg_base64:
        st.markdown(f"""
            <style>
                .stApp {{
                    background-image: url("data:image/png;base64,{upload_bg_base64}");
                    background-size: cover;
                    background-position: center;
                    background-attachment: fixed;
                }}
            </style>
        """, unsafe_allow_html=True)

    # FIX: WHITE TEXT FOR DATA UPLOAD HEADER
    st.markdown("""
        <div class="page-header-container" style="margin-top: 1rem; padding-top: 0.5rem;">
            <h1 class="upload-header-white" style="color: #ffffff; font-size: 2.5rem; font-weight: 800; margin-bottom: 0.5rem; text-shadow: 0 2px 4px rgba(0,0,0,0.4);">
                📂 Data Upload & Initialization
            </h1>
            <p class="upload-subheader-white" style="color: #e2e8f0; font-size: 1.1rem; font-weight: 500; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 2px solid rgba(255,255,255,0.3); text-shadow: 0 1px 2px rgba(0,0,0,0.3);">
                Upload your dataset to begin the intelligence pipeline.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload CSV or Excel File", type=["csv", "xlsx"])
    
    if uploaded_file is not None:
        with st.spinner("file is loading ...."):
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                    
                st.session_state.df = df.copy()
                st.session_state.original_df = df.copy()
                
                date_keywords = ['date', 'timestamp', '_at', 'deadline', 'valid_until']
                converted_cols = []
                for col in st.session_state.df.columns:
                    if st.session_state.df[col].dtype == 'object':
                        if any(kw in col.lower() for kw in date_keywords):
                            try:
                                temp_series = pd.to_datetime(st.session_state.df[col], errors='coerce')
                                if temp_series.notna().sum() > len(temp_series) * 0.5:
                                    st.session_state.df[col] = temp_series
                                    converted_cols.append(col)
                            except:
                                pass
                
                add_to_log(f"Loaded dataset: {uploaded_file.name} with shape {df.shape}")
                if converted_cols:
                    add_to_log(f"Auto-detected date columns: {', '.join(converted_cols)}")
                
                st.success("File Uploaded Successfully!")
                if converted_cols:
                    st.info(f"💡 Smart Detection: Converted {len(converted_cols)} columns to datetime: {', '.join(converted_cols)}")
                
                styled_table(df.head(10))

            except Exception as e:
                st.error(f"Error loading file: {e}")

def render_data_exploration():
    # FIX: Page header with proper top margin
    st.markdown("""
        <div class="page-header-container" style="margin-top: 1rem; padding-top: 0.5rem;">
            <h1 class="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-indigo-600 tracking-tight mb-2">
                🔎 Data Exploration
            </h1>
            <p class="text-gray-600 mb-4">Quick overview and basic pandas operations for initial data understanding.</p>
        </div>
    """, unsafe_allow_html=True)
    
    df = st.session_state.df

    st.markdown("""
        <style>
        div[data-testid="stButton"] button {
            white-space: nowrap !important;
            word-break: keep-all !important;
            overflow: visible !important;
            padding: 1px 6px !important;
            height: auto !important;
            min-height: 28px !important;
            width: 100% !important;
            font-size: 11px !important;
            border-radius: 6px !important;
        }
        div.stColumn { margin-bottom: -0.75rem !important; }
        div[data-testid="column"] { padding: 0 2px !important; }
        </style>
    """, unsafe_allow_html=True)

    # Section 1: Dataset Properties
    st.markdown("### 1. Dataset Properties")
    p1, p2, p3, p4 = st.columns(4)
    p1.markdown(create_color_card("Shape (Rows × Cols)", f"{df.shape[0]:,} × {df.shape[1]:,}", "#fdf4ff", "#fae8ff", "#c026d3", "#701a75", "#701a75", val_font_size="1.10rem"), unsafe_allow_html=True)
    p2.markdown(create_color_card("Total Rows", f"{df.shape[0]:,}", "#eff6ff", "#dbeafe", "#2563eb", "#1e3a8a", "#1e3a8a"), unsafe_allow_html=True)
    p3.markdown(create_color_card("Total Columns", f"{df.shape[1]:,}", "#ecfdf5", "#d1fae5", "#059669", "#064e3b", "#064e3b"), unsafe_allow_html=True)
    p4.markdown(create_color_card("Total Size (Cells)", f"{df.size:,}", "#fffbeb", "#fef3c7", "#d97706", "#78350f", "#78350f"), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    with st.expander("Show Column Names (df.columns)"):
        st.write(list(df.columns))
    with st.expander("Show Data Types (df.dtypes)"):
        styled_table(df.dtypes.astype(str).to_frame(name="Data Type").reset_index().rename(columns={"index": "Column Name"}), height=300)

    # Section 2: Data Preview
    st.markdown("---")
    st.markdown("### 2. View Data")
    custom_n = st.number_input("🔢 Customize the row numbers:", min_value=1, max_value=len(df), value=5, step=5)
    
    view_nav_items = [
        ("🔼", f"VIEW HEAD"),
        ("🔽", f"VIEW TAIL"),
        ("🔀", f"RANDOM VIEW")
    ]
        
    v_cols = st.columns(3)
    for i in range(3):
        with v_cols[i]:
            label = f"{view_nav_items[i][0]} {view_nav_items[i][1]}"
            is_active = st.session_state.dx_selected_view == i
            if st.button(label, key=f"dx_view_{i}", use_container_width=True, type="primary" if is_active else "secondary"):
                st.session_state.dx_selected_view = i
                st.rerun()
                
    st.markdown("<hr style='margin: 1.25rem 0; border: none; border-top: 1px solid #e5e7eb;'>", unsafe_allow_html=True)
    
    if st.session_state.dx_selected_view == 0:
        styled_table(df.head(custom_n))
    elif st.session_state.dx_selected_view == 1:
        styled_table(df.tail(custom_n))
    elif st.session_state.dx_selected_view == 2:
        styled_table(df.sample(min(custom_n, len(df))))

    # Section 3: Data Type Classification
    st.markdown("---")
    st.markdown("### 3. 🧠 Data Type Classification Summary")
    
    float_cols = df.select_dtypes(include=['float']).columns.tolist()
    int_cols   = df.select_dtypes(include=['int', 'integer']).columns.tolist()
    string_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    bool_cols   = df.select_dtypes(include=['bool']).columns.tolist()
    dt_cols     = df.select_dtypes(include=['datetime']).columns.tolist()
    
    t1, t2, t3, t4, t5 = st.columns(5)
    t1.markdown(create_color_card("string",   f"{len(string_cols)}", "#fdf4ff", "#fae8ff", "#c026d3", "#701a75", "#701a75"), unsafe_allow_html=True)
    t2.markdown(create_color_card("float",    f"{len(float_cols)}",  "#eff6ff", "#dbeafe", "#2563eb", "#1e3a8a", "#1e3a8a"), unsafe_allow_html=True)
    t3.markdown(create_color_card("int",     f"{len(int_cols)}",    "#ecfdf5", "#d1fae5", "#059669", "#064e3b", "#064e3b"), unsafe_allow_html=True)
    t4.markdown(create_color_card("boolean",  f"{len(bool_cols)}",   "#f0fdf4", "#dcfce7", "#16a34a", "#14532d", "#14532d"), unsafe_allow_html=True)
    t5.markdown(create_color_card("datetime", f"{len(dt_cols)}",     "#fffbeb", "#fef3c7", "#d97706", "#78350f", "#78350f"), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
    with st.expander("View Columns per Type"):
        for _typ, _cs in [("string", string_cols), ("float", float_cols),
                          ("int", int_cols), ("boolean", bool_cols), ("datetime", dt_cols)]:
            if _cs:
                st.write(f"**{_typ}:** {', '.join(_cs)}")

    # Section 4: Missing Values
    st.markdown("---")
    st.markdown("### 4. Missing Values Check")
    
    try:
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Total Missing by Column**")
            missing_df = df.isnull().sum().to_frame(name="Missing Count").reset_index().rename(columns={"index": "Column Name"})
            styled_missing = missing_df.style.applymap(
                lambda v: 'background-color: #fee2e2; color: #b91c1c; font-weight: bold' if isinstance(v, (int, float)) and v > 0 else '', 
                subset=['Missing Count']
            )
            styled_table(styled_missing, height=300)
            
        with col2:
            st.write("**Missing Percentage**")
            missing_pct_df = (df.isnull().mean() * 100).round(2).to_frame(name="% Missing").reset_index().rename(columns={"index": "Column Name"})
            styled_missing_pct = missing_pct_df.style.applymap(
                lambda v: 'background-color: #fee2e2; color: #b91c1c; font-weight: bold' if isinstance(v, (int, float)) and v > 0 else '', 
                subset=['% Missing']
            )
            styled_table(styled_missing_pct, height=300)
        
        total_missing_all = df.isnull().sum().sum()
        total_cells = df.size
        total_missing_pct = (total_missing_all / total_cells) * 100 if total_cells > 0 else 0
        
        m1, m2 = st.columns(2)
        with m1:
            st.markdown(f"""
                <div style="background-color: #fee2e2; padding: 15px; border-radius: 10px; border-left: 5px solid #dc2626; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <div style="font-size: 0.85rem; font-weight: 600; color: #991b1b; margin-bottom: 4px;">📂 Total Missing Cells</div>
                    <div style="font-size: 1.8rem; font-weight: 800; color: #dc2626;">{total_missing_all:,}</div>
                </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
                <div style="background-color: #fff7ed; padding: 15px; border-radius: 10px; border-left: 5px solid #f97316; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <div style="font-size: 0.85rem; font-weight: 600; color: #9a3412; margin-bottom: 4px;">📊 Total Missing Percentage %</div>
                    <div style="font-size: 1.8rem; font-weight: 800; color: #ea580c;">{total_missing_pct:.2f}%</div>
                </div>
            """, unsafe_allow_html=True)
        
        if not missing_df.empty:
            missing_summary = missing_df.copy()
            missing_summary["% Missing"] = missing_pct_df["% Missing"].values
            
            excel_data = to_excel(missing_summary)
            if excel_data:
                st.download_button(
                    label="📥 Download Missing Values Report (Excel)",
                    data=excel_data,
                    file_name="missing_values_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_missing_summary"
                )
                
    except Exception as e:
        st.error(f"Error in Missing Values section: {str(e)}")
        st.info("Please ensure xlsxwriter is installed: pip install xlsxwriter")

    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("Show Rows with Missing Values", key="btn_missing_rows"):
            missing_rows_df = df[df.isnull().any(axis=1)]
            if not missing_rows_df.empty:
                styled_table(missing_rows_df)
                excel_data = to_excel(missing_rows_df)
                if excel_data:
                    st.download_button(
                        label="📥 Download Missing Rows (Excel)", 
                        data=excel_data, 
                        file_name="missing_rows_data.xlsx", 
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="dl_missing_rows"
                    )
            else:
                st.success("No rows with missing values found!")
                
    with col_btn2:
        if st.button("Show Columns with Missing Values", key="btn_missing_cols"):
            cols_with_missing = df.columns[df.isnull().any()].tolist()
            if cols_with_missing:
                st.write("Columns with missing values:", cols_with_missing)
            else:
                st.success("No columns with missing values found!")

    # Section 5: Duplicates
    st.markdown("---")
    st.markdown("### 5. 🔁 Duplicate Rows Analysis")
    dup_count = df.duplicated().sum()
    dup_pct = (dup_count / len(df)) * 100 if len(df) > 0 else 0
    d1, d2, d3 = st.columns(3)
    d1.markdown(create_color_card("Total Duplicate Rows", f"{dup_count:,}", "#fef2f2", "#fee2e2", "#dc2626", "#7f1d1d", "#7f1d1d"), unsafe_allow_html=True)
    d2.markdown(create_color_card("Duplicate %", f"{dup_pct:.2f}%", "#fffbeb", "#fef3c7", "#d97706", "#78350f", "#78350f"), unsafe_allow_html=True)
    d3.markdown(create_color_card("Unique Rows", f"{len(df) - dup_count:,}", "#f0fdf4", "#dcfce7", "#16a34a", "#14532d", "#14532d"), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
    if dup_count > 0:
        with st.expander(f"👁️ View {dup_count} Duplicate Rows"):
            dup_df = df[df.duplicated(keep=False)].sort_values(by=list(df.columns))
            styled_dup = dup_df.style.set_properties(**{'background-color': '#fee2e2', 'color': '#b91c1c'})
            styled_table(styled_dup)
    else:
        st.success("✅ No duplicate rows found in the dataset.")

    # Section 6: Statistical Summary
    st.markdown("---")
    st.markdown("### 6. Quick Statistical Summary (df.describe)")
    styled_table(df.describe().reset_index().rename(columns={"index": "Statistic"}))

    # Section 7: Outlier Detection
    st.markdown("---")
    st.markdown("### 7. 📊 Outlier Detection — Per Column Summary")
    num_cols_out = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(num_cols_out) > 0:
        tab_iqr, tab_z = st.tabs(["📦 IQR Method", "📐 Z-Score Method"])
        with tab_iqr:
            iqr_data = []
            for _c in num_cols_out:
                q1  = df[_c].quantile(0.25)
                q3  = df[_c].quantile(0.75)
                iqr = q3 - q1
                lb  = q1 - 1.5 * iqr
                ub  = q3 + 1.5 * iqr
                n_o = int(((df[_c] < lb) | (df[_c] > ub)).sum())
                iqr_data.append({"Column": _c, "Q1": round(q1, 3), "Q3": round(q3, 3),
                                  "IQR": round(iqr, 3), "Lower Bound": round(lb, 3),
                                  "Upper Bound": round(ub, 3), "Outlier Count": n_o,
                                  "Outlier %": round(n_o / len(df) * 100, 2) if len(df) > 0 else 0})
            iqr_df = pd.DataFrame(iqr_data)
            st.metric("Total Outliers (IQR)", f"{iqr_df['Outlier Count'].sum():,}")
            styled_table(iqr_df.style.background_gradient(cmap="Reds", subset=["Outlier Count", "Outlier %"]))
            
            excel_data = to_excel(iqr_df)
            if excel_data:
                st.download_button(
                    label="📥 Download IQR Outliers (Excel)", 
                    data=excel_data, 
                    file_name="outliers_iqr.xlsx", 
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_iqr"
                )
                
        with tab_z:
            z_thresh = st.slider("Z-Score Threshold", 1.5, 4.0, 3.0, 0.1, key="exp_z_thresh")
            z_data = []
            for _c in num_cols_out:
                cc = df[_c].dropna()
                if len(cc) < 3: 
                    continue
                zs  = np.abs(stats.zscore(cc))
                n_o = int((zs > z_thresh).sum())
                z_data.append({"Column": _c, "Mean": round(cc.mean(), 3), "Std": round(cc.std(), 3),
                               "Outlier Count": n_o, "Outlier %": round(n_o / len(df) * 100, 2) if len(df) > 0 else 0})
            z_df = pd.DataFrame(z_data)
            st.metric(f"Total Outliers (Z > {z_thresh})", f"{z_df['Outlier Count'].sum():,}")
            styled_table(z_df.style.background_gradient(cmap="Oranges", subset=["Outlier Count", "Outlier %"]))
            
            excel_data = to_excel(z_df)
            if excel_data:
                st.download_button(
                    label="📥 Download Z-Score Outliers (Excel)", 
                    data=excel_data, 
                    file_name="outliers_zscore.xlsx", 
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_z"
                )
    else:
        st.info("No numeric columns available for outlier detection.")

    # Section 8: Cardinality
    st.markdown("---")
    st.markdown("### 8. 🔢 Unique Values & Cardinality Classification (df.nunique)")
    nunique_df = df.nunique().reset_index()
    nunique_df.columns = ["Column", "Unique Values"]
    nunique_df["% of Total Rows"] = (nunique_df["Unique Values"] / len(df) * 100).round(2) if len(df) > 0 else 0
    nunique_df["Dtype"] = [str(df[c].dtype) for c in nunique_df["Column"]]
    
    def classify_cardinality(row):
        pct = row["% of Total Rows"]
        n   = row["Unique Values"]
        if pct >= 90 or n == len(df): 
            return "🔑 ID-like"
        elif n <= 10:                  
            return "🟢 Low Cardinality"
        else:                          
            return "🔴 High Cardinality"
            
    nunique_df["Cardinality Class"] = nunique_df.apply(classify_cardinality, axis=1)
    cn1, cn2 = st.columns([2, 1])
    with cn1:
        styled_table(nunique_df.style.background_gradient(cmap="YlOrRd", subset=["Unique Values"]))
    with cn2:
        card_counts = nunique_df["Cardinality Class"].value_counts().to_dict()
        low = card_counts.get("🟢 Low Cardinality", 0)
        high = card_counts.get("🔴 High Cardinality", 0)
        id_  = card_counts.get("🔑 ID-like", 0)
        st.markdown(create_color_card("🟢 Low Cardinality",  f"{low} cols",  "#f0fdf4", "#dcfce7", "#16a34a", "#14532d", "#14532d"), unsafe_allow_html=True)
        st.markdown("<div style='margin:8px 0'></div>", unsafe_allow_html=True)
        st.markdown(create_color_card("🔴 High Cardinality", f"{high} cols", "#fef2f2", "#fee2e2", "#dc2626", "#7f1d1d", "#7f1d1d"), unsafe_allow_html=True)
        st.markdown("<div style='margin:8px 0'></div>", unsafe_allow_html=True)
        st.markdown(create_color_card("🔑 ID-like Columns",  f"{id_} cols",  "#fdf4ff", "#fae8ff", "#c026d3", "#701a75", "#701a75"), unsafe_allow_html=True)

    excel_data = to_excel(nunique_df)
    if excel_data:
        st.download_button(
            label="📥 Download Cardinality Report (Excel)", 
            data=excel_data, 
            file_name="cardinality_report.xlsx", 
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_cardinality"
        )

    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
    
    # Section 9: df.info + Memory
    st.markdown("---")
    st.markdown("### 9. 📋 df.info() — Full Structure & Memory Usage")
    mem_total = df.memory_usage(deep=True).sum()
    mem_mb = mem_total / (1024 ** 2)
    mi1, mi2 = st.columns(2)
    mi1.markdown(create_color_card("Total Memory Usage", f"{mem_mb:.3f} MB", "#f0fdf4", "#dcfce7", "#16a34a", "#14532d", "#14532d"), unsafe_allow_html=True)
    mi2.markdown(create_color_card("Total Cells", f"{df.size:,}", "#eff6ff", "#dbeafe", "#2563eb", "#1e3a8a", "#1e3a8a"), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
    with st.expander("📄 Show Full df.info() — Column Types & Non-Null Counts"):
        info_data = []
        for _col in df.columns:
            info_data.append({
                "Column": _col,
                "Non-Null Count": int(df[_col].notna().sum()),
                "Null Count": int(df[_col].isna().sum()),
                "Dtype": str(df[_col].dtype),
                "Memory (KB)": round(df[_col].memory_usage(deep=True) / 1024, 2)
            })
        info_df = pd.DataFrame(info_data)
        styled_table(info_df.style.background_gradient(cmap="Blues", subset=["Memory (KB)"]))
        st.caption(f"Total Memory: **{mem_mb:.3f} MB** | RangeIndex: {len(df)} entries | {df.shape[1]} columns")

    # Section 10: Memory Optimization
    st.markdown("---")
    st.markdown("### 🧾 10. Memory Optimization Suggestions")
    current_mem = df.memory_usage(deep=True).sum() / (1024**2)
    suggestions = []
    for _col in df.columns:
        _dtype    = str(df[_col].dtype)
        _n_unique = df[_col].nunique()
        _col_kb   = df[_col].memory_usage(deep=True) / 1024
        if _dtype == "object" and _n_unique / len(df) < 0.5:
            _saving = _col_kb - (df[_col].astype("category").memory_usage(deep=True) / 1024)
            suggestions.append({"Column": _col, "Current Dtype": _dtype, "Suggested": "category",
                                 "Current (KB)": round(_col_kb, 2), "Est. Saving (KB)": round(max(_saving, 0), 2)})
        elif _dtype == "float64":
            suggestions.append({"Column": _col, "Current Dtype": _dtype, "Suggested": "float32",
                                 "Current (KB)": round(_col_kb, 2), "Est. Saving (KB)": round(_col_kb * 0.5, 2)})
        elif _dtype == "int64":
            col_data = df[_col].dropna()
            if len(col_data) == 0: 
                continue
            cmin, cmax = col_data.min(), col_data.max()
            if   cmin >= -128 and cmax <= 127:          
                tgt, ratio = "int8",  0.875
            elif cmin >= -32768 and cmax <= 32767:      
                tgt, ratio = "int16", 0.75
            elif cmin >= -2147483648 and cmax <= 2147483647: 
                tgt, ratio = "int32", 0.5
            else:                                       
                tgt = None
            if tgt:
                suggestions.append({"Column": _col, "Current Dtype": _dtype, "Suggested": tgt,
                                     "Current (KB)": round(_col_kb, 2), "Est. Saving (KB)": round(_col_kb * ratio, 2)})
    if suggestions:
        sug_df = pd.DataFrame(suggestions)
        total_saving = sug_df["Est. Saving (KB)"].sum() / 1024
        opt_mem = max(0, current_mem - total_saving)
        m1, m2, m3 = st.columns(3)
        m1.markdown(create_color_card("Current Memory",          f"{current_mem:.3f} MB", "#fef2f2", "#fee2e2", "#dc2626", "#7f1d1d", "#7f1d1d"), unsafe_allow_html=True)
        m2.markdown(create_color_card("Est. After Optimization", f"{opt_mem:.3f} MB",     "#f0fdf4", "#dcfce7", "#16a34a", "#14532d", "#14532d"), unsafe_allow_html=True)
        m3.markdown(create_color_card("Potential Saving",         f"{total_saving:.3f} MB","#fffbeb", "#fef3c7", "#d97706", "#78350f", "#78350f"), unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
        styled_table(sug_df.style.background_gradient(cmap="Greens", subset=["Est. Saving (KB)"]))
    else:
        st.success("✅ Memory is already well-optimized for this dataset.")

def render_strategic_discovery():
    pass

def render_data_quality():
    pass

def render_data_cleaning():
    pass

def render_visualization():
    pass

def render_statistics():
    pass

def render_report():
    pass

def render_numeric_functions():
    pass

def render_string_functions():
    pass

# ==========================================
# 4. Main Execution Route
# ==========================================

if st.session_state.df is None and not menu.startswith("📂 Data Upload"):
    st.warning("⚠️ Please upload data in the 'Data Upload' module first.")
    render_data_upload()
else:
    if menu.startswith("📂 Data Upload"):
        render_data_upload()
    elif menu.startswith("🔎 Data Exploration"):
        render_data_exploration()
    elif ":red[(Pro)]" in menu:
        render_pro_restriction(menu)
    else:
        st.info(f"The module '{menu}' is currently under construction in the V2 overhaul.")
