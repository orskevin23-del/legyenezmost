from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging
from datetime import datetime
from openai import AsyncOpenAI
import os

from models import Script, ScriptGenerateRequest, Hook
from models_analytics import OptimizedScriptRequest
from routes.auth import get_current_user
from utils.script_helpers import (
    extract_hook_from_script,
    detect_hook_type_and_tags,
    count_characters,
    truncate_to_length,
    generate_german_script_prompt
)
from utils.ml_optimizer import get_top_performing_patterns, generate_optimized_prompt
from database import db

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize OpenAI client
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@router.post("/generate-optimized")
async def generate_optimized_script(request: OptimizedScriptRequest, current_user = Depends(get_current_user)):
    """
    Generate ML-optimized script using analytics data.
    Uses top performing hooks, dominance lines, open loops, and close patterns.
    """
    try:
        topic = request.topic or "Glaube und innere Kraft"
        
        # Check if analytics optimization is enabled
        if request.use_analytics:
            # Get top performing patterns from analytics data
            patterns = await get_top_performing_patterns(current_user["id"], request.top_n_examples)
            
            # Check if we have analytics data
            if not patterns["top_hooks"] and not patterns["top_scripts"]:
                logger.warning(f"No analytics data found for user {current_user['id']}, falling back to normal generation")
                request.use_analytics = False
        
        # Generate prompt
        if request.use_analytics and patterns:
            system_prompt, user_prompt = generate_optimized_prompt(
                topic, request.keywords, request.mode, patterns
            )
            logger.info(f"Using ML-optimized prompt with {len(patterns.get('top_hooks', []))} top hooks")
        else:
            system_prompt, user_prompt = generate_german_script_prompt(
                topic, request.keywords, request.mode
            )
            logger.info("Using standard script generation")
        
        # Call OpenAI
        response = await openai_client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.85,
            max_tokens=200
        )
        
        script_text = response.choices[0].message.content.strip()
        
        # Truncate if too long
        script_text = truncate_to_length(script_text, 350)
        
        # Extract hook
        hook_text = extract_hook_from_script(script_text)
        
        # Detect hook type and tags
        hook_type, detected_mode, tags = detect_hook_type_and_tags(hook_text, topic)
        
        # Count characters
        char_count = count_characters(script_text)
        
        # Create Script object
        script = Script(
            user_id=current_user["id"],
            topic=topic,
            mode=request.mode,
            script=script_text,
            hook_text=hook_text,
            hook_type=hook_type,
            tags=tags,
            character_count=char_count,
            keywords=request.keywords
        )
        
        # Create Hook object (auto-insert to hook library)
        hook = Hook(
            user_id=current_user["id"],
            hook_text=hook_text,
            mode=detected_mode,
            hook_type=hook_type,
            tags=tags,
            topic=topic,
            script_id=script.id,
            source="generated"
        )
        
        # Save to database
        script_dict = script.model_dump()
        script_dict['created_at'] = script_dict['created_at'].isoformat()
        script_dict['hook_id'] = hook.id
        script_dict['ml_optimized'] = request.use_analytics  # Mark if ML-optimized
        await db.scripts.insert_one(script_dict)
        
        hook_dict = hook.model_dump()
        hook_dict['created_at'] = hook_dict['created_at'].isoformat()
        await db.hooks.insert_one(hook_dict)
        
        logger.info(f"Generated {'ML-optimized' if request.use_analytics else 'standard'} script {script.id} with hook {hook.id}")
        
        return {
            "id": script.id,
            "script": script.script,
            "hook_text": script.hook_text,
            "hook_type": script.hook_type,
            "mode": script.mode,
            "tags": script.tags,
            "character_count": script.character_count,
            "hook_id": hook.id,
            "ml_optimized": request.use_analytics,
            "created_at": script.created_at.isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error generating optimized script: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating script: {str(e)}")

@router.post("/generate")
async def generate_script(request: ScriptGenerateRequest, current_user = Depends(get_current_user)):
    """
    Generate German Faith-niche script using OpenAI GPT-4o-mini.
    Automatically extracts hook, detects type, generates tags, and saves to database.
    """
    try:
        topic = request.topic or "Glaube und innere Kraft"
        
        # Generate prompt
        system_prompt, user_prompt = generate_german_script_prompt(
            topic, request.keywords, request.mode
        )
        
        # Call OpenAI
        response = await openai_client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.85,
            max_tokens=200
        )
        
        script_text = response.choices[0].message.content.strip()
        
        # Truncate if too long
        script_text = truncate_to_length(script_text, 350)
        
        # Extract hook
        hook_text = extract_hook_from_script(script_text)
        
        # Detect hook type and tags
        hook_type, detected_mode, tags = detect_hook_type_and_tags(hook_text, topic)
        
        # Count characters
        char_count = count_characters(script_text)
        
        # Create Script object
        script = Script(
            user_id=current_user["id"],
            topic=topic,
            mode=request.mode,
            script=script_text,
            hook_text=hook_text,
            hook_type=hook_type,
            tags=tags,
            character_count=char_count,
            keywords=request.keywords
        )
        
        # Create Hook object (auto-insert to hook library)
        hook = Hook(
            user_id=current_user["id"],
            hook_text=hook_text,
            mode=detected_mode,
            hook_type=hook_type,
            tags=tags,
            topic=topic,
            script_id=script.id,
            source="generated"
        )
        
        # Save to database
        script_dict = script.model_dump()
        script_dict['created_at'] = script_dict['created_at'].isoformat()
        script_dict['hook_id'] = hook.id
        await db.scripts.insert_one(script_dict)
        
        hook_dict = hook.model_dump()
        hook_dict['created_at'] = hook_dict['created_at'].isoformat()
        await db.hooks.insert_one(hook_dict)
        
        logger.info(f"Generated script {script.id} with hook {hook.id} for user {current_user['id']}")
        
        return {
            "id": script.id,
            "script": script.script,
            "hook_text": script.hook_text,
            "hook_type": script.hook_type,
            "mode": script.mode,
            "tags": script.tags,
            "character_count": script.character_count,
            "hook_id": hook.id,
            "created_at": script.created_at.isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error generating script: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating script: {str(e)}")

@router.get("", response_model=List[dict])
async def get_scripts(current_user = Depends(get_current_user), limit: int = 50, skip: int = 0):
    """
    Get user's scripts with pagination.
    """
    scripts = await db.scripts.find(
        {"user_id": current_user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
    
    return scripts

@router.get("/{script_id}")
async def get_script(script_id: str, current_user = Depends(get_current_user)):
    """
    Get single script by ID.
    """
    script = await db.scripts.find_one(
        {"id": script_id, "user_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    
    return script


@router.put("/{script_id}")
async def update_script(
    script_id: str, 
    script_update: dict,
    current_user = Depends(get_current_user)
):
    """
    Update script text.
    """
    # Validate script exists and belongs to user
    existing_script = await db.scripts.find_one({
        "id": script_id,
        "user_id": current_user["id"]
    })
    
    if not existing_script:
        raise HTTPException(status_code=404, detail="Script not found")
    
    # Update script text and character count
    new_script_text = script_update.get("script", existing_script["script"])
    character_count = count_characters(new_script_text)
    
    await db.scripts.update_one(
        {"id": script_id, "user_id": current_user["id"]},
        {
            "$set": {
                "script": new_script_text,
                "character_count": character_count
            }
        }
    )
    
    logger.info(f"Updated script {script_id} for user {current_user['id']}")
    
    return {
        "id": script_id,
        "script": new_script_text,
        "character_count": character_count,
        "message": "Script updated successfully"
    }

@router.delete("/{script_id}")
async def delete_script(script_id: str, current_user = Depends(get_current_user)):
    """
    Delete script.
    """
    result = await db.scripts.delete_one({
        "id": script_id,
        "user_id": current_user["id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Script not found")
    
    return {"message": "Script deleted"}