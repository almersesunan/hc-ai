# func/genai_analysis.py

import google.generativeai as genai

# Initialize the GeminiAPI
genai.configure(api_key='AIzaSyCFxqFcV15_eBk3_k-t42jqzyKqA_X0bMo')
model = genai.GenerativeModel("gemini-2.5-flash")

def analyze_candidate_skills(cv_text, job_pos):
    response = model.generate_content(f"""
    (if any of the provided data is not in english language, you can translate it first before analyzing it)
    Can you analyze the Position Suitability based on this Candidate Curiculum Vitae (CV) describe below:
        {cv_text}
    compared to Job Position description listed below:
        {job_pos}
    make a comprehensive analysis described from Candidate CV based on core competencies parameter: 
    - STRIVE FOR EXCELLENCE: Goes the extra mile to achieve team's goals. (Weight 16)
    - DEMONSTRATING INTEGRITY: Takes actions based on principles and values in spite of the consequences. (Weight 16)
    - TEAMWORK: Promotes cross-function collaboration, provides opportunity for team working and development. (Weight 16)
    - CUSTOMER DRIVEN: Anticipates and adapts to customer's needs. (Weight 16)
    - CONTINUOUS IMPROVEMENT: Identify improvement opportunity to streamlines function's work process. (Weight 36)            
    and determine the suitability score along with how to calculate the score
    suitability score from 1 to 100 with conclusion range describe as
    - score above 65 as RECOMMENDED
    - score between 50 and 64 as CONSIDERED 
    - score below 50 as NOT RECOMMENDED 
    Address the candidate using neutral gender
    if there is a mention of willingness to work in certain location, do not measure it as a parameter on analysis
    if the person does not recommended for the job position, make a recommendation or alternative for suitable job position.
    make a recommendation on what training should the candidate take to be qualify for taking the job
    the text result must be using Unicode font that compatible to Times New Roman Font
    the output should not contain any table
    lastly, recommend insightful and targeted interview questions based on your assessment.
    Result must includes this Format text below as an output
    Candidate:
    Position:
    Conclusion:
    Analysis:
    """)

    return response.text