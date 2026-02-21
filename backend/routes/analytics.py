from fastapi import APIRouter, Depends
import logging
from typing import Dict, List

from routes.auth import get_current_user
from database import db

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/overview")
async def get_analytics_overview(current_user = Depends(get_current_user)):
    """
    Get aggregated analytics overview.
    Includes: total views, likes, comments, subs, avg retention, avg swipe rate.
    """
    pipeline = [
        {"$match": {"user_id": current_user["id"]}},
        {
            "$group": {
                "_id": None,
                "total_views": {"$sum": "$views"},
                "total_likes": {"$sum": "$likes"},
                "total_comments": {"$sum": "$comments"},
                "total_subs": {"$sum": "$subs"},
                "avg_retention": {"$avg": "$retention_percent"},
                "avg_swipe_rate": {"$avg": "$swipe_rate"},
                "total_metrics": {"$sum": 1}
            }
        }
    ]
    
    results = await db.metrics.aggregate(pipeline).to_list(length=1)
    
    if not results:
        return {
            "total_views": 0,
            "total_likes": 0,
            "total_comments": 0,
            "total_subs": 0,
            "avg_retention": 0.0,
            "avg_swipe_rate": 0.0,
            "total_metrics": 0
        }
    
    data = results[0]
    data.pop("_id", None)
    
    return data

@router.get("/hook-performance")
async def get_hook_performance(current_user = Depends(get_current_user)):
    """
    Get hook type performance analytics.
    Returns retention % by hook type.
    """
    pipeline = [
        {
            "$lookup": {
                "from": "hooks",
                "localField": "hook_used",
                "foreignField": "hook_text",
                "as": "hook_data"
            }
        },
        {"$unwind": {"path": "$hook_data", "preserveNullAndEmptyArrays": True}},
        {"$match": {"user_id": current_user["id"]}},
        {
            "$group": {
                "_id": "$hook_data.hook_type",
                "avg_retention": {"$avg": "$retention_percent"},
                "total_views": {"$sum": "$views"},
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"avg_retention": -1}}
    ]
    
    results = await db.metrics.aggregate(pipeline).to_list(length=100)
    
    # Format results
    formatted = []
    for item in results:
        formatted.append({
            "hook_type": item["_id"] or "unknown",
            "avg_retention": round(item["avg_retention"], 2),
            "total_views": item["total_views"],
            "count": item["count"]
        })
    
    return formatted

@router.get("/time-series")
async def get_time_series_data(current_user = Depends(get_current_user), limit: int = 10):
    """
    Get time series data for views and likes over time.
    Returns last N metrics sorted by date.
    """
    metrics = await db.metrics.find(
        {"user_id": current_user["id"]},
        {"_id": 0, "created_at": 1, "views": 1, "likes": 1, "retention_percent": 1}
    ).sort("created_at", -1).limit(limit).to_list(length=limit)
    
    # Reverse to show oldest first
    metrics.reverse()
    
    return metrics

@router.get("/top-hooks")
async def get_top_hooks(current_user = Depends(get_current_user), limit: int = 10):
    """
    Get top performing hooks by retention.
    """
    hooks = await db.hooks.find(
        {"user_id": current_user["id"], "usage_count": {"$gt": 0}},
        {"_id": 0}
    ).sort("avg_retention", -1).limit(limit).to_list(length=limit)
    
    return hooks