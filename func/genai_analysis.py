# func/genai_analysis.py

import google.generativeai as genai
import re

# Initialize the GeminiAPI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

def analyze_candidate_skills(cv_text, job_pos):
    response = model.generate_content(f"""
    (if any of the provided data is not in english language, you can translate it first before analyzing it)
    Analyze the following resume text and assess how well it matches these job specifications:\n
        {cv_text}\n
    compared to Job specifications listed below:\n
        {job_pos}\n
    Provide a comprehensive analysis summary based on core competencies parameter: 
    - STRIVE FOR EXCELLENCE: Goes the extra mile to achieve team's goals. (Weight 16)
    - DEMONSTRATING INTEGRITY: Takes actions based on principles and values in spite of the consequences. (Weight 16)
    - TEAMWORK: Promotes cross-function collaboration, provides opportunity for team working and development. (Weight 16)
    - CUSTOMER DRIVEN: Anticipates and adapts to customer's needs. (Weight 16)
    - CONTINUOUS IMPROVEMENT: Identify improvement opportunity to streamlines function's work process. (Weight 36)            
    
    From Core Competencies Parameter result, calculate scoring weight into these 3 categories with Output format:
    'Skills Score: X, Experience Score: Y, Soft Skills Score: Z'

    Result must includes this Format text below as an output
    Candidate:
    Position:
    Conclusion:
    Analysis:
    Skills Score: 
    Experience Score: 
    Soft Skills Score: 

    Notes:
    - Address the candidate using neutral gender
    - if there is a mention of willingness to work in certain location, do not measure it as a parameter on analysis
    - if the person does not recommended for the job position, make a recommendation or alternative for suitable job position.
    - make a recommendation on what training should the candidate take to be qualify for taking the job
    - the text result must be using Unicode font that compatible to Times New Roman Font
    - the output should not contain any table
    - lastly, recommend insightful and targeted interview questions based on your assessment.
    
    """)

    return response.text

def extract_scores_from_analysis(analysis_text):
    # Initialize scores to 0 in case of failures
    skills_score = 0
    experience_score = 0
    soft_skills_score = 0

    # Debugging: Log the analysis text to verify if it contains scores
    print("Analysis Text for Scoring:", analysis_text)

    # Extract scores using regex
    try:
        skills_score = int(re.search(r"Skills Score:\s*(\d+)", analysis_text).group(1))
    except AttributeError:
        print("Skills Score not found in analysis text.")

    try:
        experience_score = int(re.search(r"Experience Score:\s*(\d+)", analysis_text).group(1))
    except AttributeError:
        print("Experience Score not found in analysis text.")

    try:
        soft_skills_score = int(re.search(r"Soft Skills Score:\s*(\d+)", analysis_text).group(1))
    except AttributeError:
        print("Soft Skills Score not found in analysis text.")

    return skills_score, experience_score, soft_skills_score

def weighted_score(skills_score, experience_score, soft_skills_score, weights):
    # Calculate weighted score based on provided weights
    total_weight = weights['skills'] + weights['experience'] + weights['soft_skills']
    weighted_total = (
        skills_score * weights['skills'] +
        experience_score * weights['experience'] +
        soft_skills_score * weights['soft_skills']
    )
    
    return weighted_total / total_weight if total_weight > 0 else 0