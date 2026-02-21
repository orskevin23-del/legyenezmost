from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Literal
from datetime import datetime
import uuid

# ===== AUTH MODELS =====
class UserRegister(BaseModel):
    email: str
    password: str
    name: str

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    token: str
    user: dict

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ===== SCRIPT MODELS =====
class ScriptGenerateRequest(BaseModel):
    topic: Optional[str] = None
    mode: Literal["STATE_BASED", "FAITH_EXPLICIT"] = "FAITH_EXPLICIT"
    keywords: List[str] = Field(default_factory=list)
    
    @field_validator('topic')
    @classmethod
    def validate_topic(cls, v):
        if v and len(v.strip()) < 3:
            raise ValueError("Topic must be at least 3 characters")
        return v

class Script(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    topic: str
    mode: str
    script: str
    hook_text: str
    hook_type: str
    tags: List[str] = Field(default_factory=list)
    character_count: int
    keywords: List[str] = Field(default_factory=list)
    hook_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ===== HOOK MODELS =====
class HookCreate(BaseModel):
    hook_text: str
    mode: Literal["STATE_BASED", "FAITH_EXPLICIT"]
    hook_type: str
    tags: List[str] = Field(default_factory=list)
    avg_retention: Optional[float] = 0.0

class Hook(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    hook_text: str
    mode: str
    hook_type: str
    tags: List[str] = Field(default_factory=list)
    topic: Optional[str] = None
    script_id: Optional[str] = None
    source: Literal["generated", "pre_built", "manual"] = "generated"
    avg_retention: float = 0.0
    usage_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ===== METRICS MODELS =====
class MetricCreate(BaseModel):
    script_id: str
    hook_used: str
    views: int = 0
    likes: int = 0
    comments: int = 0
    subs: int = 0
    retention_percent: float = 0.0
    swipe_rate: float = 0.0

class Metric(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    script_id: str
    hook_used: str
    views: int
    likes: int
    comments: int
    subs: int
    retention_percent: float
    swipe_rate: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ===== VIDEO MODELS =====
class VideoGenerateRequest(BaseModel):
    script_id: str
    voice_id: Optional[str] = None
    voice_settings: Optional[dict] = None
    background_music: Optional[str] = None
    b_roll_search: Optional[str] = None

class Video(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    script_id: str
    status: Literal["queued", "processing", "completed", "failed"] = "queued"
    video_url: Optional[str] = None
    audio_url: Optional[str] = None
    duration: Optional[float] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ===== SAVED VOICE MODELS =====
class SavedVoice(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    voice_id: str
    name: str
    language: Optional[str] = "Multilingual"
    is_favorite: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SavedVoiceCreate(BaseModel):
    voice_id: str
    name: str
    language: Optional[str] = "Multilingual"
    is_favorite: bool = False

# ===== VOICE PREFERENCES MODELS =====
class VoicePreferences(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    voice_id: str
    voice_settings: dict = Field(default_factory=lambda: {
        "stability": 0.7,
        "similarity_boost": 0.75,
        "style": 0.5,
        "speed": 1.0,
        "use_speaker_boost": True
    })
    is_default: bool = True  # Auto-load on startup
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class VoicePreferencesCreate(BaseModel):
    voice_id: str
    voice_settings: dict
    is_default: bool = True