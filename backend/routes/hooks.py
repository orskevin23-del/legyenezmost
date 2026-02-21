from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import logging

from models import Hook, HookCreate
from routes.auth import get_current_user
from database import db

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("", response_model=List[dict])
async def get_hooks(
    current_user = Depends(get_current_user),
    hook_type: Optional[str] = None,
    mode: Optional[str] = None,
    sort_by: str = "created_at",
    limit: int = 100
):
    """
    Get user's hook library with filtering and sorting.
    
    - filter by hook_type: emotional_trigger, urgency, identity_filter, etc.
    - filter by mode: STATE_BASED, FAITH_EXPLICIT
    - sort_by: created_at, avg_retention, usage_count
    """
    query = {"user_id": current_user["id"]}
    
    if hook_type:
        query["hook_type"] = hook_type
    
    if mode:
        query["mode"] = mode
    
    # Determine sort field
    sort_field = "created_at"
    sort_order = -1  # DESC
    
    if sort_by == "avg_retention":
        sort_field = "avg_retention"
    elif sort_by == "usage_count":
        sort_field = "usage_count"
    
    hooks = await db.hooks.find(
        query,
        {"_id": 0}
    ).sort(sort_field, sort_order).limit(limit).to_list(length=limit)
    
    return hooks

@router.post("", response_model=dict)
async def create_hook(hook_data: HookCreate, current_user = Depends(get_current_user)):
    """
    Manually create a hook (for pre-built or manual entries).
    """
    hook = Hook(
        user_id=current_user["id"],
        hook_text=hook_data.hook_text,
        mode=hook_data.mode,
        hook_type=hook_data.hook_type,
        tags=hook_data.tags,
        source="manual",
        avg_retention=hook_data.avg_retention
    )
    
    hook_dict = hook.model_dump()
    hook_dict['created_at'] = hook_dict['created_at'].isoformat()
    
    await db.hooks.insert_one(hook_dict)
    
    return {
        "id": hook.id,
        "hook_text": hook.hook_text,
        "mode": hook.mode,
        "hook_type": hook.hook_type,
        "tags": hook.tags,
        "source": hook.source,
        "created_at": hook.created_at.isoformat()
    }

@router.delete("/{hook_id}")
async def delete_hook(hook_id: str, current_user = Depends(get_current_user)):
    """
    Delete hook from library.
    """
    result = await db.hooks.delete_one({
        "id": hook_id,
        "user_id": current_user["id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Hook not found")
    
    return {"message": "Hook deleted"}