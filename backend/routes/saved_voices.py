from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from models import SavedVoice, SavedVoiceCreate
from routes.auth import get_current_user

router = APIRouter(prefix="/saved-voices", tags=["saved_voices"])

@router.get("")
async def get_saved_voices(current_user: dict = Depends(get_current_user)):
    """Get all saved voices for current user"""
    from database import db
    
    voices = await db.saved_voices.find(
        {"user_id": current_user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    return voices

@router.post("")
async def create_saved_voice(
    voice_data: SavedVoiceCreate,
    current_user: dict = Depends(get_current_user)
):
    """Save a new voice"""
    from database import db
    
    # Check if voice already exists
    existing = await db.saved_voices.find_one({
        "user_id": current_user["id"],
        "voice_id": voice_data.voice_id
    })
    
    if existing:
        raise HTTPException(status_code=400, detail="Voice already saved")
    
    voice = SavedVoice(
        user_id=current_user["id"],
        voice_id=voice_data.voice_id,
        name=voice_data.name,
        language=voice_data.language,
        is_favorite=voice_data.is_favorite
    )
    
    await db.saved_voices.insert_one(voice.model_dump())
    
    return voice

@router.put("/{voice_id}")
async def update_saved_voice(
    voice_id: str,
    voice_data: SavedVoiceCreate,
    current_user: dict = Depends(get_current_user)
):
    """Update a saved voice"""
    from database import db
    
    result = await db.saved_voices.update_one(
        {"id": voice_id, "user_id": current_user["id"]},
        {"$set": voice_data.model_dump()}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Voice not found")
    
    return {"message": "Voice updated"}

@router.delete("/{voice_id}")
async def delete_saved_voice(
    voice_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a saved voice"""
    from database import db
    
    result = await db.saved_voices.delete_one({
        "id": voice_id,
        "user_id": current_user["id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Voice not found")
    
    return {"message": "Voice deleted"}

@router.patch("/{voice_id}/favorite")
async def toggle_favorite(
    voice_id: str,
    is_favorite: bool,
    current_user: dict = Depends(get_current_user)
):
    """Toggle favorite status"""
    from database import db
    
    result = await db.saved_voices.update_one(
        {"id": voice_id, "user_id": current_user["id"]},
        {"$set": {"is_favorite": is_favorite}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Voice not found")
    
    return {"message": "Favorite status updated"}
