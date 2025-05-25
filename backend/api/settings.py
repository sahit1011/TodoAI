"""
API endpoints for user settings
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict

from backend.database import get_db
from backend.models.user import User
from backend.auth import get_current_user
from backend.config import ASSISTANT_MODES

router = APIRouter(prefix="/api/settings", tags=["settings"])

@router.get("/assistant-mode")
async def get_assistant_mode(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Get the current assistant mode for the user"""
    return {"mode": current_user.preferred_assistant_mode}

@router.post("/assistant-mode")
async def set_assistant_mode(
    mode: Dict[str, str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Set the assistant mode for the user"""
    # Validate the mode
    if mode["mode"] not in [ASSISTANT_MODES["PLAN"], ASSISTANT_MODES["ACT"]]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode. Must be one of: {ASSISTANT_MODES['PLAN']}, {ASSISTANT_MODES['ACT']}"
        )
    
    # Update the user's preferred mode
    user = db.query(User).filter(User.id == current_user.id).first()
    user.preferred_assistant_mode = mode["mode"]
    db.commit()
    
    return {"mode": user.preferred_assistant_mode}
