# job_scorer.py
from typing import Dict, Any
from job.Utils.config_manager import CONFIG

def score_job(job: Dict[str, Any]) -> int:
    """Score a job based on included and excluded keywords"""
    text = " ".join(str(v).lower() for v in job.values())
    score = 0
    
    for keyword in CONFIG["give_points_keywords"]["include"]:
        if keyword.lower() in text:
            score += 2
    
    for keyword in CONFIG["give_points_keywords"]["deduct_points_keywords"]:
        if keyword.lower() in text:
            score -= 1
    
    return score
