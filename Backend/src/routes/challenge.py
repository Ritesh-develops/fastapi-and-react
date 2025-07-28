from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database.db import (get_challenge_quota, create_challenge, create_challenge_quota, reset_quota_if_needed, get_user_challenges)
from ..utils import authenticate_and_get_user_details
from ..database.models import get_db
import json
from datetime import datetime
from ..ai_generator import generate_challenge_with_ai

router = APIRouter()

class ChallengeRequest(BaseModel):
    difficulty: str

    class Config:
        json_schema_extra = {"example": {"difficulty": "easy"}}

@router.post("/generate-challenge")
async def generate_challenge(request: ChallengeRequest, request_obj: Request ,db: Session = Depends(get_db)):
    try:
        user_details = authenticate_and_get_user_details(request_obj)
        user_id = user_details.get("user_id")

        quota = get_challenge_quota(db, user_id)
        if not quota:
            quota=create_challenge_quota(db, user_id)

        quota = reset_quota_if_needed(db, quota)
        if quota.quota_remaining<=0:
            raise HTTPException(status_code=429, detail="Quota exhausted")
        
        challenge_data = generate_challenge_with_ai(request.difficulty)

        new_challenge = create_challenge(
            db=db,
            difficulty=request.difficulty,
            created_by=user_id,
            title=challenge_data["title"],
            options=json.dumps(challenge_data["options"]),
            correct_answer_id=challenge_data["correct_answer_id"],
            explanation=challenge_data["explanation"]
        )

        # TODO Challenge


        quota.quota_remaining-=1
        db.commit()
        return {
            "id": new_challenge.id,
            "difficulty": request.difficulty,
            "title": new_challenge.title,
            "options": json.loads(new_challenge.options),
            "correct_answer_id": new_challenge.correct_answer_id,
            "explanation": new_challenge.explanation,
            "timestamp": new_challenge.date_created.isoformat() 
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/my-history")
async def my_history(request: Request, db: Session = Depends(get_db)):
    user_details = authenticate_and_get_user_details(request)
    user_id = user_details.get("user_id")

    challenges = get_user_challenges(db, user_id)
    processed_challenges = []
    for challenge in challenges:
        challenge_dict = {
            "id": challenge.id,
            "difficulty": challenge.difficulty,
            "date_created": challenge.date_created.isoformat(),
            "created_by": challenge.created_by,
            "title": challenge.title,
            "options": json.loads(challenge.options) if isinstance(challenge.options, str) else [],
            "correct_answer_id": challenge.correct_answer_id,
            "explanation": challenge.explanation
        }

        processed_challenges.append(challenge_dict)
    return {"challenges": processed_challenges}

@router.get("/quota")
async def get_quota(request: Request, db: Session = Depends(get_db)):
    user_details = authenticate_and_get_user_details(request)
    user_id = user_details.get("user_id")

    quota = get_challenge_quota(db, user_id)
    if not quota:
        return {
           "user_id": user_id,
           "quota_remaining": 0,
           "last_reset_date": datetime.now()
        }
    quota = reset_quota_if_needed(db, quota)
    return quota

