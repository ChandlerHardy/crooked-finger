import strawberry
from datetime import datetime
from typing import List, Optional

@strawberry.type
class User:
    id: int
    email: str
    is_active: bool
    is_verified: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

@strawberry.type
class CrochetProject:
    id: int
    name: str
    pattern_text: Optional[str] = None
    translated_text: Optional[str] = None
    difficulty_level: Optional[str] = None
    estimated_time: Optional[str] = None
    yarn_weight: Optional[str] = None
    hook_size: Optional[str] = None
    notes: Optional[str] = None
    image_data: Optional[str] = None
    is_completed: bool
    user_id: int
    created_at: datetime
    updated_at: datetime

@strawberry.type
class Conversation:
    id: int
    title: str
    user_id: int
    created_at: datetime
    updated_at: datetime
    message_count: int

@strawberry.type
class ChatMessage:
    id: int
    message: str
    response: str
    message_type: str
    conversation_id: Optional[int] = None
    project_id: Optional[int] = None
    user_id: int
    created_at: datetime

@strawberry.type
class ProjectDiagram:
    id: int
    diagram_data: str
    diagram_type: str
    diagram_format: str
    project_id: int
    created_at: datetime

@strawberry.type
class AuthResponse:
    user: User
    access_token: str
    token_type: str

@strawberry.input
class RegisterInput:
    email: str
    password: str

@strawberry.input
class LoginInput:
    email: str
    password: str

@strawberry.input
class CreateConversationInput:
    title: Optional[str] = "New Chat"

@strawberry.input
class UpdateConversationInput:
    title: Optional[str] = None

@strawberry.input
class CreateProjectInput:
    name: str
    pattern_text: Optional[str] = None
    difficulty_level: Optional[str] = None
    estimated_time: Optional[str] = None
    yarn_weight: Optional[str] = None
    hook_size: Optional[str] = None
    notes: Optional[str] = None
    image_data: Optional[str] = None

@strawberry.input
class UpdateProjectInput:
    name: Optional[str] = None
    pattern_text: Optional[str] = None
    translated_text: Optional[str] = None
    difficulty_level: Optional[str] = None
    estimated_time: Optional[str] = None
    yarn_weight: Optional[str] = None
    hook_size: Optional[str] = None
    notes: Optional[str] = None
    image_data: Optional[str] = None
    is_completed: Optional[bool] = None

@strawberry.type
class PatternAnalysis:
    total_rounds: int
    pattern_type: str
    estimated_size: str
    stitch_count_by_round: List[int]

@strawberry.type
class TranslationResponse:
    original_pattern: str
    translated_instructions: str
    analysis: PatternAnalysis

@strawberry.type
class ChatResponse:
    message: str
    diagram_svg: Optional[str] = None
    diagram_png: Optional[str] = None
    has_pattern: bool = False

@strawberry.type
class ModelUsageStats:
    model_name: str
    current_usage: int
    daily_limit: int
    remaining: int
    percentage_used: float
    priority: int
    use_case: str
    total_input_characters: int
    total_output_characters: int
    total_input_tokens: int
    total_output_tokens: int

@strawberry.type
class AIUsageDashboard:
    total_requests_today: int
    total_remaining: int
    models: List[ModelUsageStats]

@strawberry.type
class ResetUsageResponse:
    success: bool
    message: str
    reset_date: Optional[str] = None

@strawberry.type
class YouTubeTranscriptResponse:
    success: bool
    video_id: Optional[str] = None
    transcript: Optional[str] = None
    word_count: Optional[int] = None
    language: Optional[str] = None
    thumbnail_url: Optional[str] = None
    thumbnail_url_hq: Optional[str] = None
    error: Optional[str] = None

@strawberry.type
class ExtractedPattern:
    success: bool
    pattern_name: Optional[str] = None
    pattern_notation: Optional[str] = None
    pattern_instructions: Optional[str] = None
    difficulty_level: Optional[str] = None
    materials: Optional[str] = None
    estimated_time: Optional[str] = None
    video_id: Optional[str] = None
    thumbnail_url: Optional[str] = None
    error: Optional[str] = None