import streamlit as st
import ollama
import numpy as np
import fitz  # PyMuPDF for PDF text extraction
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from dotenv import load_dotenv
import pandas as pd
import time
import base64

# Download NLTK data
nltk.download("punkt")
nltk.download("stopwords")

load_dotenv()

# Load a better embedding model
EMBEDDING_MODEL = SentenceTransformer("all-mpnet-base-v2")

def get_embedding(text):
    return EMBEDDING_MODEL.encode(text, convert_to_numpy=True)

def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = "".join(page.get_text("text") + "\n" for page in doc).strip()
    return text

def extract_skills(text):
    words = word_tokenize(text)
    stop_words = set(stopwords.words("english"))
    keywords = [word.lower() for word in words if word.isalpha() and word.lower() not in stop_words]
    return list(set(keywords))

def similarity_score(resume_text, jd_text):
    resume_emb = get_embedding(resume_text).reshape(1, -1)
    jd_emb = get_embedding(jd_text).reshape(1, -1)
    return round(cosine_similarity(resume_emb, jd_emb)[0][0] * 100, 2)

def get_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="match_results.csv">📥 Download Results</a>'
    return href

st.set_page_config(page_title="Job Description Matcher", layout="wide")
st.title("🔍 Job Description Matcher using Local Ollama & Sentence Transformers")

st.markdown("---")
st.sidebar.header("Upload & Settings")
uploaded_file = st.sidebar.file_uploader("📄 Upload Your Resume (PDF)", type=["pdf"])
job_description = st.sidebar.text_area("📌 Paste the Entire Job Description", height=200, help="Paste the full job description here.")

if st.sidebar.button("🔎 Match JD"):
    if uploaded_file and job_description:
        with st.spinner("Processing... Please wait."):
            resume_text = extract_text_from_pdf(uploaded_file)
            resume_skills = extract_skills(resume_text)
            jd_skills = extract_skills(job_description)
            score = similarity_score(resume_text, job_description)
            missing_skills = [skill for skill in jd_skills if skill not in resume_skills]
        
        st.success("✅ Matching Completed!")
        st.subheader("📊 Match Results:")
        st.markdown(f"### 🎯 **{score}% Match**")
        
        with st.expander("📄 View Job Description"):
            st.write(job_description)
        
        with st.expander("📄 View Extracted Resume Skills"):
            st.write(", ".join(resume_skills))
        
        with st.expander("📄 View Extracted JD Skills"):
            st.write(", ".join(jd_skills))
        
        if missing_skills:
            st.error(f"🚨 **Missing Skills:** {', '.join(missing_skills)}")
        else:
            st.success("✅ You match all key skills!")

        results_df = pd.DataFrame({"Match Score": [score], "Missing Skills": [', '.join(missing_skills) if missing_skills else "None"]})
        st.markdown(get_download_link(results_df), unsafe_allow_html=True)
    else:
        st.sidebar.warning("⚠️ Please upload a Resume PDF and enter a Job Description.")
