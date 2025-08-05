import streamlit as st
import pandas as pd
from func.pdf_processing import extract_text_from_pdf
from func.genai_analysis import analyze_candidate_skills

with st.sidebar:
    st.markdown("---")
    st.caption("AI-Powered Human Capital System")
    st.caption("© 2025 HCIS - Sinar Mas Land")

st.title("📝 Candidate Analysis")
st.markdown("""
    **Analyze Candidate CV by compare it to the job position & description.**
""")

# 1. **Input Job Specifications**
st.header("Job Specifications")
job_spec = st.text_area("Enter the job specifications for the role", placeholder="List required skills, experience, and qualifications...")

# 2. **Upload Candidate Resumes**
st.header("Upload Candidate CVs")
uploaded_files = st.file_uploader("Upload candidate CVs (PDF only)", accept_multiple_files=True, type="pdf")

# 3. **Define Scoring Weights**
st.header("Adjust Scoring Weights")
weights = {
    'skills': st.slider("Skills Weight", 0.0, 1.0, 0.5),
    'experience': st.slider("Experience Weight", 0.0, 1.0, 0.3),
    'soft_skills': st.slider("Soft Skills Weight", 0.0, 1.0, 0.2)
}

# 4. **Determine Suitability Degree Function**
def determine_suitability(final_score):
    if final_score >= 8:
        return "Highly Suitable"
    elif 5 <= final_score < 8:
        return "Moderately Suitable"
    else:
        return "Less Suitable"

# Ensure session state initialization
if 'results' not in st.session_state:
    st.session_state.results = []

if 'improvement_recs' not in st.session_state:
    st.session_state.improvement_recs = []

# 5. **Analyze Candidates and Display Results**
if st.button("Analyze Candidates"):
    st.session_state.results.clear()  # Clear previous results to avoid duplication issues
    for uploaded_file in uploaded_files:
        # Extract text from PDF
        profile_text = extract_text_from_pdf(uploaded_file)

        # Analyze candidate skills and job match
        skill_analysis = analyze_candidate_skills(profile_text, job_spec)

        # # Extract individual scores from the analysis text
        # skills_score, experience_score, soft_skills_score = extract_scores_from_analysis(skill_analysis)

        # # Calculate final weighted score
        # final_score = weighted_score(skills_score, experience_score, soft_skills_score, weights)

        # # Determine suitability degree
        # suitability = determine_suitability(final_score)

        st.session_state.results.append({
            "Candidate": uploaded_file.name,
            "Skills Analysis": skill_analysis#,
            # "Final Score": final_score,
            # "Suitability": suitability
        })

    # Display results in a table
    results_df = pd.DataFrame(st.session_state.results)
    st.subheader("Candidate Analysis Results")
    st.write(results_df)