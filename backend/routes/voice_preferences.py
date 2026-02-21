from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from models import VoicePreferences, VoicePreferencesCreate
from routes.auth import get_current_user

router = APIRouter()

@router.get("")
async def get_voice_preferences(current_user: dict = Depends(get_current_user)):
    """Get user's voice preferences (returns default if exists)"""
    from database import db
    
    # Find default preference
    pref = await db.voice_preferences.find_one(
        {"user_id": current_user["id"], "is_default": True},
        {"_id": 0}
    )
    
    return pref

@router.post("")
async def save_voice_preferences(
    pref_data: VoicePreferencesCreate,
    current_user: dict = Depends(get_current_user)
):
    """Save or update voice preferences"""
    from database import db
    
    # If setting as default, unset other defaults first
    if pref_data.is_default:
        await db.voice_preferences.update_many(
            {"user_id": current_user["id"]},
            {"$set": {"is_default": False}}
        )
    
    # Check if preference already exists for this voice
    existing = await db.voice_preferences.find_one({
        "user_id": current_user["id"],
        "voice_id": pref_data.voice_id
    })
    
    if existing:
        # Update existing
        await db.voice_preferences.update_one(
            {"user_id": current_user["id"], "voice_id": pref_data.voice_id},
            {
                "$set": {
                    "voice_settings": pref_data.voice_settings,
                    "is_default": pref_data.is_default,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return {"message": "Voice preferences updated"}
    else:
        # Create new
        pref = VoicePreferences(
            user_id=current_user["id"],
            voice_id=pref_data.voice_id,
            voice_settings=pref_data.voice_settings,
            is_default=pref_data.is_default
        )
        
        pref_dict = pref.model_dump()
        pref_dict['created_at'] = pref_dict['created_at'].isoformat()
        pref_dict['updated_at'] = pref_dict['updated_at'].isoformat()
        
        await db.voice_preferences.insert_one(pref_dict)
        return pref

@router.delete("")
async def delete_voice_preferences(current_user: dict = Depends(get_current_user)):
    """Delete all voice preferences for user"""
    from database import db
    
    await db.voice_preferences.delete_many({"user_id": current_user["id"]})
    return {"message": "Voice preferences deleted"}
