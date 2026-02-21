from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import List
import logging
import csv
import io
from datetime import datetime

from models_analytics import NotionAnalyticsRow, AnalyticsData, AlgorithmInsight
from routes.auth import get_current_user
from database import db

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/import-csv")
async def import_notion_csv(file: UploadFile = File(...), current_user = Depends(get_current_user)):
    """
    Import Notion CSV export with analytics data.
    Columns: Social File, Retention Hook, Hook Title, Dominance Line, Open Loop, 
             Close, Resolve Script, Views, Retention %, Swipe Rate, Like, Comments, Sub-2/1000 views
    """
    try:
        content = await file.read()
        decoded = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(decoded))
        
        imported_count = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                # Map CSV columns to model fields
                analytics_row = NotionAnalyticsRow(
                    social_file=row.get('Social File', '').strip(),
                    retention_hook=row.get('Retention Hook', '').strip(),
                    hook_title=row.get('Hook Title', '').strip(),
                    dominance_line=row.get('Dominance Line', '').strip() or None,
                    open_loop=row.get('Open Loop', '').strip() or None,
                    close=row.get('Close', '').strip() or None,
                    resolve_script=row.get('Resolve Script', '').strip(),
                    views=int(row.get('Views', 0) or 0),
                    retention_percent=float(row.get('Retention %', 0) or 0),
                    swipe_rate=float(row.get('Swipe Rate', 0) or 0),
                    likes=int(row.get('Like', 0) or 0),
                    comments=int(row.get('Comments', 0) or 0),
                    subs_per_1000_views=float(row.get('Sub-2/1000 views', 0) or 0),
                    avg_watch_time=float(row.get('Avg Watch Time', 0) or 0)
                )
                
                analytics_data = AnalyticsData(
                    user_id=current_user["id"],
                    **analytics_row.model_dump()
                )
                
                data_dict = analytics_data.model_dump()
                data_dict['created_at'] = data_dict['created_at'].isoformat()
                
                await db.analytics_data.insert_one(data_dict)
                imported_count += 1
            
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
                logger.error(f"Error importing row {row_num}: {str(e)}")
        
        logger.info(f"Imported {imported_count} analytics rows for user {current_user['id']}")
        
        return {
            "success": True,
            "imported_count": imported_count,
            "total_rows": imported_count + len(errors),
            "errors": errors if errors else None
        }
    
    except Exception as e:
        logger.error(f"Error importing CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"CSV import failed: {str(e)}")

@router.get("/export-csv")
async def export_analytics_csv(current_user = Depends(get_current_user)):
    """Export user's analytics data as CSV."""
    try:
        analytics = await db.analytics_data.find(
            {"user_id": current_user["id"]},
            {"_id": 0}
        ).sort("retention_percent", -1).to_list(length=1000)
        
        if not analytics:
            raise HTTPException(status_code=404, detail="No analytics data found")
        
        output = io.StringIO()
        fieldnames = [
            'social_file', 'retention_hook', 'hook_title', 'dominance_line',
            'open_loop', 'close', 'resolve_script', 'views', 'swipe_rate',
            'retention_percent', 'likes', 'comments', 'subs_per_1000_views',
            'avg_watch_time', 'created_at'
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in analytics:
            writer.writerow({
                'social_file': row.get('social_file', ''),
                'retention_hook': row.get('retention_hook', ''),
                'hook_title': row.get('hook_title', ''),
                'dominance_line': row.get('dominance_line', ''),
                'open_loop': row.get('open_loop', ''),
                'close': row.get('close', ''),
                'resolve_script': row.get('resolve_script', ''),
                'views': row.get('views', 0),
                'swipe_rate': row.get('swipe_rate', 0),
                'retention_percent': row.get('retention_percent', 0),
                'likes': row.get('likes', 0),
                'comments': row.get('comments', 0),
                'subs_per_1000_views': row.get('subs_per_1000_views', 0),
                'avg_watch_time': row.get('avg_watch_time', 0),
                'created_at': row.get('created_at', '')
            })
        
        output.seek(0)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=analytics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )
    
    except Exception as e:
        logger.error(f"Error exporting CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"CSV export failed: {str(e)}")

@router.get("/insights")
async def get_analytics_insights(current_user = Depends(get_current_user)):
    """
    Get analytics insights with HOOK vs SCRIPT separation.
    
    Hook Effectiveness = Swipe Rate (0-3s, stay or swipe?)
    Script Effectiveness = Retention Rate (3-30s, watch till end?)
    """
    try:
        # Top hooks by SWIPE RATE (hook effectiveness)
        top_hooks_by_swipe = await db.analytics_data.find(
            {"user_id": current_user["id"]},
            {"_id": 0, "hook_title": 1, "retention_hook": 1, "swipe_rate": 1, "views": 1}
        ).sort("swipe_rate", -1).limit(10).to_list(length=10)
        
        # Top scripts by RETENTION RATE (script effectiveness)
        top_scripts_by_retention = await db.analytics_data.find(
            {"user_id": current_user["id"]},
            {"_id": 0, "resolve_script": 1, "retention_percent": 1, "views": 1}
        ).sort("retention_percent", -1).limit(10).to_list(length=10)
        
        # Top dominance lines
        top_dominance = await db.analytics_data.find(
            {"user_id": current_user["id"], "dominance_line": {"$ne": None}},
            {"_id": 0, "dominance_line": 1, "retention_percent": 1, "swipe_rate": 1}
        ).sort("retention_percent", -1).limit(10).to_list(length=10)
        
        # Top open loops
        top_open_loops = await db.analytics_data.find(
            {"user_id": current_user["id"], "open_loop": {"$ne": None}},
            {"_id": 0, "open_loop": 1, "retention_percent": 1}
        ).sort("retention_percent", -1).limit(10).to_list(length=10)
        
        # Top close patterns
        top_closes = await db.analytics_data.find(
            {"user_id": current_user["id"], "close": {"$ne": None}},
            {"_id": 0, "close": 1, "retention_percent": 1}
        ).sort("retention_percent", -1).limit(10).to_list(length=10)
        
        # Hook type performance (swipe rate by hook type)
        hook_type_pipeline = [
            {"$match": {"user_id": current_user["id"]}},
            {
                "$group": {
                    "_id": "$retention_hook",
                    "avg_swipe_rate": {"$avg": "$swipe_rate"},
                    "avg_retention": {"$avg": "$retention_percent"},
                    "total_views": {"$sum": "$views"},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"avg_swipe_rate": -1}}
        ]
        
        hook_type_performance = await db.analytics_data.aggregate(hook_type_pipeline).to_list(length=100)
        
        # Overall averages
        pipeline = [
            {"$match": {"user_id": current_user["id"]}},
            {
                "$group": {
                    "_id": None,
                    "avg_swipe_rate": {"$avg": "$swipe_rate"},
                    "avg_retention": {"$avg": "$retention_percent"},
                    "avg_likes": {"$avg": "$likes"},
                    "avg_comments": {"$avg": "$comments"},
                    "total_views": {"$sum": "$views"},
                    "total_videos": {"$sum": 1}
                }
            }
        ]
        
        avg_stats = await db.analytics_data.aggregate(pipeline).to_list(length=1)
        
        return {
            "hook_effectiveness": {
                "top_hooks_by_swipe_rate": top_hooks_by_swipe,
                "hook_type_performance": hook_type_performance,
                "explanation": "Swipe Rate = Hook effectiveness (0-3s). High swipe rate = people STAY, low = people SWIPE away."
            },
            "script_effectiveness": {
                "top_scripts_by_retention": top_scripts_by_retention,
                "top_dominance_lines": top_dominance,
                "top_open_loops": top_open_loops,
                "top_close_patterns": top_closes,
                "explanation": "Retention Rate = Script effectiveness (3-30s). High retention = people watch till end."
            },
            "average_stats": avg_stats[0] if avg_stats else None,
            "benchmarks": {
                "swipe_rate_good": 70.0,
                "swipe_rate_excellent": 85.0,
                "retention_good": 60.0,
                "retention_excellent": 75.0
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/algorithm-guide")
async def get_algorithm_guide():
    """
    Educational guide: How YouTube Shorts algorithm works.
    Explains Hook vs Script, Swipe Rate vs Retention, and best practices.
    """
    return {
        "title": "YouTube Shorts Algoritmus Útmutató",
        "sections": [
            {
                "title": "1. A Hook (0-3 másodperc)",
                "metric": "Swipe Rate",
                "description": "Az első 3 másodperc KRITIKUS. Itt dől el, hogy a néző marad vagy továbbgörgeti a videót.",
                "goal": "Magas Swipe Rate = Emberek MARADNAK (nem görgetnek el)",
                "benchmarks": {
                    "excellent": "85%+ (emberek 85%-a marad)",
                    "good": "70-85%",
                    "poor": "<60%"
                },
                "tips": [
                    "Használj érzelmi triggert (Weißt du...? Merkst du...?)",
                    "Kérdezz valamit ami azonnal érdekel",
                    "Teremts azonnali curiosity-t",
                    "NE magyarázz, csak hook-olj!"
                ]
            },
            {
                "title": "2. Dominance Line (3-8 másodperc)",
                "metric": "Early Retention",
                "description": "Erős állítás ami építi a feszültséget és megerősíti, hogy érdemes nézni.",
                "examples": [
                    "Menschen, die das verstehen...",
                    "Es gibt einen Grund, warum...",
                    "Die meisten wissen nicht..."
                ],
                "purpose": "Dominancia mutatása, hitelesség építése"
            },
            {
                "title": "3. Open Loop (8-15 másodperc)",
                "metric": "Mid-Retention",
                "description": "Nyitott kérdés vagy mystery ami miatt a néző kíváncsi a válaszra.",
                "examples": [
                    "Aber was bedeutet das wirklich?",
                    "Und genau hier liegt das Geheimnis...",
                    "Doch es gibt noch etwas..."
                ],
                "purpose": "Feszültség fenntartása, kíváncsiság fokozása"
            },
            {
                "title": "4. Body (15-25 másodperc)",
                "metric": "Mid-to-Late Retention",
                "description": "A fő üzenet átadása, value delivery.",
                "tips": [
                    "Tömör, lényegretörő",
                    "Érzelmi mélység",
                    "Gyakorlati példa vagy insight"
                ]
            },
            {
                "title": "5. Close (25-30 másodperc)",
                "metric": "Complete Retention",
                "description": "Lezárás, CTA, vagy inspiráló gondolat ami miatt like-olnak/follow-olnak.",
                "types": [
                    "Reflection close: És te mit gondolsz erről?",
                    "Inspiration close: Genau das ist deine Kraft.",
                    "CTA close: Folge für mehr..."
                ],
                "purpose": "Engagement növelése, követés ösztönzése"
            }
        ],
        "key_metrics_explained": {
            "swipe_rate": {
                "what": "Hány % marad az első 3mp után",
                "controlled_by": "HOOK minősége",
                "optimization": "Top performing hook-ok használata analytics alapján"
            },
            "retention_rate": {
                "what": "Hány % nézi végig a videót",
                "controlled_by": "SCRIPT minősége (Dominance, Open Loop, Body, Close)",
                "optimization": "Top performing script struktúrák használata"
            }
        },
        "tension_positioning": {
            "description": "A feszültség pozícionálása kulcsfontosságú a retention szempontjából.",
            "ideal_curve": [
                "0-3s: Azonnali hook (high intensity)",
                "3-8s: Dominance (build up)",
                "8-15s: Open loop (peak curiosity)",
                "15-25s: Value delivery (slight drop, then rise)",
                "25-30s: Close (final peak)"
            ],
            "tip": "Az Open Loop a tension csúcspont - itt a legnagyobb a kíváncsiság!"
        }
    }

@router.get("/data", response_model=List[dict])
async def get_analytics_data(
    current_user = Depends(get_current_user),
    limit: int = 100,
    skip: int = 0
):
    """Get user's analytics data with pagination."""
    analytics = await db.analytics_data.find(
        {"user_id": current_user["id"]},
        {"_id": 0}
    ).sort("retention_percent", -1).skip(skip).limit(limit).to_list(length=limit)
    
    return analytics

@router.delete("/data/{analytics_id}")
async def delete_analytics_data(analytics_id: str, current_user = Depends(get_current_user)):
    """Delete analytics data entry."""
    result = await db.analytics_data.delete_one({
        "id": analytics_id,
        "user_id": current_user["id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Analytics data not found")
    
    return {"message": "Analytics data deleted"}