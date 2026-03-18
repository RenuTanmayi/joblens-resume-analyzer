# matching.py
from sentence_transformers import SentenceTransformer, util

# -------------------------------
# 1️⃣ Load model ONCE globally
# -------------------------------
# This ensures the model is loaded only once per session
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ SentenceTransformer model loaded!")
    return _model

# -------------------------------
# 2️⃣ Compute Match Function
# -------------------------------
def compute_match(resume_skills, jd_skills, threshold=0.8):
    """
    Compute embedding-based match score and missing skills.
    
    Args:
        resume_skills (list): skills extracted from resume
        jd_skills (list): skills extracted from JD
        threshold (float): similarity threshold to consider skill as matched
    
    Returns:
        match_score (float): overall match percentage
        missing_skills (list): JD skills not in resume
    """
    model = get_model()
    
    if not resume_skills or not jd_skills:
        return 0, jd_skills
    
    # Convert skills to embeddings
    resume_embeddings = model.encode(resume_skills, convert_to_tensor=True)
    jd_embeddings = model.encode(jd_skills, convert_to_tensor=True)
    
    # Cosine similarity
    cos_sim = util.cos_sim(resume_embeddings, jd_embeddings)
    max_sim_scores = cos_sim.max(dim=0).values  # best match for each JD skill
    
    # Overall match percentage
    match_score = round(max_sim_scores.mean().item() * 100, 2)
    
    # Missing skills
    missing_skills = [jd_skills[i] for i, sim in enumerate(max_sim_scores) if sim < threshold]
    
    return match_score, missing_skills