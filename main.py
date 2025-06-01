import streamlit as st
import pdfplumber
import tempfile
import re
import os
from dotenv import load_dotenv
load_dotenv()
from utils.resume_parser import parse_resume_keywords
from job_search import search_jobs_rapidapi_post

SECTION_KEYWORDS = ['experience', 'education', 'skills', 'summary', 'projects', 'certifications']

def is_pdf(file):
    return file.name.lower().endswith('.pdf')

def extract_text(file_path):
    with pdfplumber.open(file_path) as pdf:
        return "\n".join(page.extract_text() or '' for page in pdf.pages)

def check_resume(text):
    score = 0
    if re.search(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', text):
        score += 1
    if re.search(r'\+?\d[\d\s\-]{8,}\d', text):
        score += 1
    found_sections = [kw for kw in SECTION_KEYWORDS if kw in text.lower()]
    if len(found_sections) >= 2:
        score += 1
    if len(text.split()) > 100:
        score += 1
    return score >= 3

# Page config
st.set_page_config(page_title='Resume-to-Job Matcher', page_icon="🚀", layout="centered")

# CSS styles with background and container styling + alert overrides
custom_css = """
<style>
/* Page background */
body, .stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    background-attachment: fixed;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #fff;
}

/* Main container for the app content */
.main-container {
    max-width: 900px;
    margin: 3rem auto 3rem auto;
    background: rgba(255, 255, 255, 0.12);
    padding: 2rem 3rem;
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
    backdrop-filter: blur(8.5px);
    -webkit-backdrop-filter: blur(8.5px);
    border: 1px solid rgba(255, 255, 255, 0.18);
}

/* Headings */
h1, h2, h3 {
    font-weight: 700;
    text-shadow: 1px 1px 3px rgba(75, 29, 133, 0.7);
}

/* Buttons */
div.stButton > button {
    background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
    border: none;
    color: white;
    padding: 0.6rem 1.5rem;
    font-size: 1rem;
    border-radius: 25px;
    cursor: pointer;
    transition: background 0.3s ease;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #2575fc 0%, #6a11cb 100%);
}

/* Inputs and selects */
.stTextInput>div>input, .stSelectbox>div>div>div>select, .stRadio>div>label {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    font-size: 1rem;
}

/* Placeholder text color */
.stTextInput>div>input::placeholder {
    color: #ddd;
}

/* Keywords box styling */
.keywords-box {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 1rem;
    font-size: 1rem;
    color: white;
    max-height: 150px;
    overflow-y: auto;
    white-space: pre-wrap;
}

/* Link styling */
a {
    color: #ffd166;
    font-weight: 600;
    text-decoration: none;
}
a:hover {
    text-decoration: underline;
}

/* Custom override for success alerts */
div.stAlert > div[role="alert"] {
    background-color: #145214 !important;  /* dark green */
    color: white !important;                /* white text */
    font-weight: 700 !important;
    border-left: 6px solid #0b3a0b !important;
    box-shadow: 0 2px 8px rgba(11, 58, 11, 0.6) !important;
}

/* Custom override for error alerts */
div.stAlert > div[role="alert"][data-testid="stError"] {
    background-color: #e74c3c !important;  /* bright red */
    color: white !important;                /* white text */
    font-weight: 700 !important;
    border-left: 6px solid #c0392b !important;
    box-shadow: 0 2px 8px rgba(192, 57, 43, 0.6) !important;
}
</style>
"""

# Inject the CSS styles
st.markdown(custom_css, unsafe_allow_html=True)

st.title("🚀 Resume-to-Job Matcher App")
st.markdown("Upload your resume and select preferences. We'll use these to find relevant jobs tailored for you.")

uploaded_file = st.file_uploader("📄 Upload your resume (PDF only)", type=["pdf"])
job_location = st.radio("📍 Job Location Preference", ["Remote", "Hybrid", "On-site"], index=0, horizontal=True)
job_type = st.selectbox("💼 Job Type", ["Full-time", "Part-time", "Contract", "Freelance", "Internship"])
st.markdown("---")

if "resume_text" not in st.session_state:
    st.session_state.resume_text = None
if "parsed_keywords" not in st.session_state:
    st.session_state.parsed_keywords = None
if "final_keywords" not in st.session_state:
    st.session_state.final_keywords = None
if "checked" not in st.session_state:
    st.session_state.checked = False

if uploaded_file and st.button("🔍 Check Resume"):
    if not is_pdf(uploaded_file):
        st.error("❌ Please upload a valid PDF file.")
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_path = temp_file.name

        with st.spinner("🔄 Processing your resume..."):
            try:
                text = extract_text(temp_path)
                if not text.strip():
                    st.error("⚠️ No text found in the uploaded PDF.")
                elif check_resume(text):
                    st.success("✅ This looks like a valid resume!")
                    st.session_state.resume_text = text
                    parsed_result = parse_resume_keywords(text)
                    st.session_state.parsed_keywords = parsed_result["keywords"]
                    st.session_state.final_keywords = parsed_result["keywords"]
                    st.session_state.checked = True
                else:
                    st.warning("⚠️ This doesn't seem like a resume. Please check your file.")
            except Exception as e:
                st.error(f"Unexpected error: {e}")
            finally:
                os.remove(temp_path)

if st.session_state.checked and st.session_state.parsed_keywords:
    st.markdown("### ✅ Keywords extracted from your resume:")
    st.markdown(f'<div class="keywords-box">{", ".join(st.session_state.parsed_keywords)}</div>', unsafe_allow_html=True)

    # Styled label for satisfaction question
    st.markdown("""
    <p style="
        font-size: 1.1rem;
        font-weight: 600;
        color: #fff;
        margin-bottom: 0.5rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    ">
        Are you satisfied with these keywords?
    </p>
    """, unsafe_allow_html=True)

    satisfaction = st.radio(
        "",
        ["Yes, proceed", "No, I want to edit them"],
        key="satisfaction_choice",
        horizontal=True
    )

    if satisfaction == "No, I want to edit them":
        custom_keywords = st.text_input(
            "✏️ Edit keywords (comma-separated):",
            value=", ".join(st.session_state.parsed_keywords),
            key="custom_input_box"
        )
        st.session_state.final_keywords = [kw.strip() for kw in custom_keywords.split(",") if kw.strip()]
    else:
        st.session_state.final_keywords = st.session_state.parsed_keywords

    st.markdown("### ✅ Final keywords to be used for job search:")
    st.markdown(f'<div class="keywords-box">{", ".join(st.session_state.final_keywords)}</div>', unsafe_allow_html=True)
    st.markdown(f"**Your Job Preferences:**\n- Location: `{job_location}`\n- Type: `{job_type}`")

job_type_map = {
    "Full-time": "fulltime",
    "Part-time": "parttime",
    "Contract": "contract",
    "Freelance": "freelance",
    "Internship": "internship"
}
api_job_type = job_type_map.get(job_type, "fulltime")

if st.session_state.checked and st.session_state.final_keywords:
    if st.button("🚀 Find Matching Jobs"):
        comma_keywords = ", ".join(st.session_state.final_keywords)
        with st.spinner("🔎 Searching for jobs..."):
            jobs = search_jobs_rapidapi_post(
                comma_keywords,
                job_location,
                api_job_type
            )
            if jobs:
                st.markdown("## 🔥 Matching Jobs")
                for job in jobs:
                    st.markdown(
                        f"""
                        <div style="background: rgba(255,255,255,0.15); padding: 1rem; border-radius: 12px; margin-bottom: 1rem;">
                        <h4 style="margin: 0; color: #ffd166;">{job.get('title', 'No Title')}</h4>
                        <p style="margin: 0; font-style: italic;">{job.get('company', 'Unknown Company')} | {job.get('location', 'N/A')}</p>
                        <a href="{job.get('job_url', '#')}" target="_blank">Apply Here</a>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.warning("No jobs found. Try broadening your keywords or preferences.")

# Close the main container div
st.markdown('</div>', unsafe_allow_html=True)
