from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging

from models import Metric, MetricCreate
from routes.auth import get_current_user
from database import db

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("", response_model=dict)
async def create_metric(metric_data: MetricCreate, current_user = Depends(get_current_user)):
    """
    Create metric for script performance tracking.
    """
    metric = Metric(
        user_id=current_user["id"],
        script_id=metric_data.script_id,
        hook_used=metric_data.hook_used,
        views=metric_data.views,
        likes=metric_data.likes,
        comments=metric_data.comments,
        subs=metric_data.subs,
        retention_percent=metric_data.retention_percent,
        swipe_rate=metric_data.swipe_rate
    )
    
    metric_dict = metric.model_dump()
    metric_dict['created_at'] = metric_dict['created_at'].isoformat()
    
    await db.metrics.insert_one(metric_dict)
    
    # Update hook retention if exists
    await update_hook_retention(metric_data.hook_used, metric_data.retention_percent, current_user["id"])
    
    logger.info(f"Created metric {metric.id} for script {metric_data.script_id}")
    
    return metric_dict

async def update_hook_retention(hook_text: str, retention: float, user_id: str):
    """
    Update hook's average retention based on new metric.
    """
    hook = await db.hooks.find_one({"hook_text": hook_text, "user_id": user_id})
    
    if hook:
        # Simple average (can be improved with weighted average)
        old_retention = hook.get("avg_retention", 0.0)
        usage_count = hook.get("usage_count", 0)
        
        new_avg_retention = ((old_retention * usage_count) + retention) / (usage_count + 1)
        new_usage_count = usage_count + 1
        
        await db.hooks.update_one(
            {"id": hook["id"]},
            {
                "$set": {
                    "avg_retention": new_avg_retention,
                    "usage_count": new_usage_count
                }
            }
        )

@router.get("", response_model=List[dict])
async def get_metrics(current_user = Depends(get_current_user), limit: int = 50, skip: int = 0):
    """
    Get user's metrics with pagination.
    """
    metrics = await db.metrics.find(
        {"user_id": current_user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
    
    return metrics

@router.put("/{metric_id}")
async def update_metric(metric_id: str, metric_data: MetricCreate, current_user = Depends(get_current_user)):
    """
    Update metric values.
    """
    update_data = metric_data.model_dump()
    
    result = await db.metrics.update_one(
        {"id": metric_id, "user_id": current_user["id"]},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Metric not found")
    
    return {"message": "Metric updated"}