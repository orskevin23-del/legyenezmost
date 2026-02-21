from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
import uuid

# ===== ANALYTICS DATA MODELS =====
class NotionAnalyticsRow(BaseModel):
    """Single row from Notion CSV analytics export."""
    social_file: str  # Video ID/Name
    retention_hook: str  # Hook type
    hook_title: str  # Hook text
    dominance_line: Optional[str] = None
    open_loop: Optional[str] = None
    close: Optional[str] = None
    resolve_script: str  # Full script text
    views: int = 0  # Total views (changed from watch_hours_secs)
    retention_percent: float  # % who watched till end
    swipe_rate: float = 0.0  # % who stayed after first 3 seconds (HOOK effectiveness)
    likes: int = 0
    comments: int = 0
    subs_per_1000_views: Optional[float] = 0.0
    avg_watch_time: Optional[float] = 0.0  # Average watch time in seconds

class AnalyticsData(BaseModel):
    """Analytics data stored in MongoDB."""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    social_file: str
    retention_hook: str
    hook_title: str
    dominance_line: Optional[str] = None
    open_loop: Optional[str] = None
    close: Optional[str] = None
    resolve_script: str
    views: int = 0
    retention_percent: float  # Script effectiveness (3-30s)
    swipe_rate: float = 0.0  # Hook effectiveness (0-3s)
    likes: int = 0
    comments: int = 0
    subs_per_1000_views: float = 0.0
    avg_watch_time: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ===== OPTIMIZED SCRIPT GENERATION =====
class OptimizedScriptRequest(BaseModel):
    """Request for ML-optimized script generation."""
    topic: Optional[str] = None
    mode: str = "FAITH_EXPLICIT"
    keywords: List[str] = Field(default_factory=list)
    use_analytics: bool = True  # Toggle for analytics-based optimization
    top_n_examples: int = 3  # Use top N performing examples

# ===== EDUCATION & INSIGHTS =====
class AlgorithmInsight(BaseModel):
    """Educational insights about YouTube Shorts algorithm."""
    metric_type: str  # hook_swipe_rate, retention_rate, engagement
    benchmark_value: float  # Good performance threshold
    description: str
    recommendation: str

class ScriptAnalysis(BaseModel):
    """Analyze script structure and timing."""
    script_text: str
    hook_length: int  # Characters in hook (0-3s)
    dominance_position: Optional[int] = None  # Where dominance line appears
    open_loop_position: Optional[int] = None  # Where open loop appears
    tension_peaks: List[int] = Field(default_factory=list)  # Positions of tension
    estimated_duration: float  # Estimated duration in seconds
    recommendations: List[str] = Field(default_factory=list)