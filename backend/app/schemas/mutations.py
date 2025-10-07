import strawberry
from datetime import datetime
from typing import Optional
from strawberry.types import Info
from app.database.connection import get_db
from app.database import models
from app.schemas.types import (
    User, AuthResponse, CrochetProject, Conversation, ChatResponse, ResetUsageResponse,
    YouTubeTranscriptResponse, ExtractedPattern, RegisterInput, LoginInput,
    CreateProjectInput, UpdateProjectInput, CreateConversationInput, UpdateConversationInput
)
from app.utils.auth import (
    get_password_hash, authenticate_user, create_access_token
)
from app.core.config import settings
from app.services.ai_service import ai_service
from app.services.pattern_service import pattern_service
from app.services.granny_square_service import granny_square_service
from app.services.flowing_granny_service import flowing_granny_service
from app.services.matplotlib_crochet_service import matplotlib_crochet_service
from app.services.rag_service import rag_service
from app.services.youtube_service_rapidapi import youtube_service_rapidapi
import re
from sqlalchemy.orm import Session

@strawberry.type
class Mutation:
    @strawberry.field
    async def register(
        self,
        input: RegisterInput
    ) -> AuthResponse:
        """Register a new user"""
        db = next(get_db())
        try:
            # Check if user already exists
            existing_user = db.query(models.User).filter(models.User.email == input.email).first()
            if existing_user:
                raise Exception("User with this email already exists")

            # Create new user
            hashed_password = get_password_hash(input.password)
            db_user = models.User(
                email=input.email,
                hashed_password=hashed_password,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            db.add(db_user)
            db.commit()
            db.refresh(db_user)

            # Create access token
            access_token = create_access_token(data={"sub": db_user.email})

            return AuthResponse(
                user=User(
                    id=db_user.id,
                    email=db_user.email,
                    is_active=db_user.is_active,
                    is_verified=db_user.is_verified,
                    is_admin=db_user.is_admin,
                    created_at=db_user.created_at,
                    updated_at=db_user.updated_at,
                    last_login=db_user.last_login
                ),
                access_token=access_token,
                token_type="bearer"
            )
        finally:
            db.close()

    @strawberry.field
    async def login(
        self,
        input: LoginInput
    ) -> AuthResponse:
        """Login user"""
        db = next(get_db())
        try:
            user = authenticate_user(db, input.email, input.password)
            if not user:
                raise Exception("Incorrect email or password")

            # Update last login
            user.last_login = datetime.utcnow()
            db.commit()

            # Create access token
            access_token = create_access_token(data={"sub": user.email})

            return AuthResponse(
                user=User(
                    id=user.id,
                    email=user.email,
                    is_active=user.is_active,
                    is_verified=user.is_verified,
                    is_admin=user.is_admin,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                    last_login=user.last_login
                ),
                access_token=access_token,
                token_type="bearer"
            )
        finally:
            db.close()

    @strawberry.field
    async def create_project(
        self,
        info: Info,
        input: CreateProjectInput
    ) -> CrochetProject:
        """Create a new crochet project"""
        user = info.context.get("user")
        if not user:
            raise Exception("Authentication required")

        db = next(get_db())
        try:
            db_project = models.CrochetProject(
                name=input.name,
                pattern_text=input.pattern_text,
                translated_text=input.translated_text,
                difficulty_level=input.difficulty_level,
                estimated_time=input.estimated_time,
                yarn_weight=input.yarn_weight,
                hook_size=input.hook_size,
                notes=input.notes,
                image_data=input.image_data,
                is_completed=False,
                user_id=user.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            db.add(db_project)
            db.commit()
            db.refresh(db_project)

            return CrochetProject(
                id=db_project.id,
                name=db_project.name,
                pattern_text=db_project.pattern_text,
                translated_text=db_project.translated_text,
                difficulty_level=db_project.difficulty_level,
                estimated_time=db_project.estimated_time,
                yarn_weight=db_project.yarn_weight,
                hook_size=db_project.hook_size,
                notes=db_project.notes,
                is_completed=db_project.is_completed,
                user_id=db_project.user_id,
                created_at=db_project.created_at,
                updated_at=db_project.updated_at
            )
        finally:
            db.close()

    @strawberry.field
    async def update_project(
        self,
        info: Info,
        project_id: int,
        input: UpdateProjectInput
    ) -> CrochetProject:
        """Update an existing crochet project"""
        user = info.context.get("user")
        if not user:
            raise Exception("Authentication required")

        db = next(get_db())
        try:
            db_project = db.query(models.CrochetProject).filter(
                models.CrochetProject.id == project_id,
                models.CrochetProject.user_id == user.id
            ).first()

            if not db_project:
                raise Exception("Project not found")

            # Update fields if provided
            if input.name is not None:
                db_project.name = input.name
            if input.pattern_text is not None:
                db_project.pattern_text = input.pattern_text
            if input.translated_text is not None:
                db_project.translated_text = input.translated_text
            if input.difficulty_level is not None:
                db_project.difficulty_level = input.difficulty_level
            if input.estimated_time is not None:
                db_project.estimated_time = input.estimated_time
            if input.yarn_weight is not None:
                db_project.yarn_weight = input.yarn_weight
            if input.hook_size is not None:
                db_project.hook_size = input.hook_size
            if input.notes is not None:
                db_project.notes = input.notes
            if input.image_data is not None:
                db_project.image_data = input.image_data
            if input.is_completed is not None:
                db_project.is_completed = input.is_completed

            db_project.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_project)

            return CrochetProject(
                id=db_project.id,
                name=db_project.name,
                pattern_text=db_project.pattern_text,
                translated_text=db_project.translated_text,
                difficulty_level=db_project.difficulty_level,
                estimated_time=db_project.estimated_time,
                yarn_weight=db_project.yarn_weight,
                hook_size=db_project.hook_size,
                notes=db_project.notes,
                image_data=db_project.image_data,
                is_completed=db_project.is_completed,
                user_id=db_project.user_id,
                created_at=db_project.created_at,
                updated_at=db_project.updated_at
            )
        finally:
            db.close()

    @strawberry.field
    async def delete_project(
        self,
        info: Info,
        project_id: int
    ) -> bool:
        """Delete a crochet project"""
        user = info.context.get("user")
        if not user:
            raise Exception("Authentication required")

        db = next(get_db())
        try:
            db_project = db.query(models.CrochetProject).filter(
                models.CrochetProject.id == project_id,
                models.CrochetProject.user_id == user.id
            ).first()

            if not db_project:
                raise Exception("Project not found")

            db.delete(db_project)
            db.commit()
            return True
        finally:
            db.close()

    @strawberry.field
    async def create_conversation(
        self,
        info: Info,
        input: CreateConversationInput
    ) -> Conversation:
        """Create a new conversation"""
        user = info.context.get("user")
        if not user:
            raise Exception("Authentication required")

        db = next(get_db())
        try:
            db_conversation = models.Conversation(
                title=input.title or "New Chat",
                user_id=user.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            db.add(db_conversation)
            db.commit()
            db.refresh(db_conversation)

            # Count messages in this conversation
            message_count = db.query(models.ChatMessage).filter(
                models.ChatMessage.conversation_id == db_conversation.id
            ).count()

            return Conversation(
                id=db_conversation.id,
                title=db_conversation.title,
                user_id=db_conversation.user_id,
                created_at=db_conversation.created_at,
                updated_at=db_conversation.updated_at,
                message_count=message_count
            )
        finally:
            db.close()

    @strawberry.field
    async def update_conversation(
        self,
        info: Info,
        conversation_id: int,
        input: UpdateConversationInput
    ) -> Conversation:
        """Update an existing conversation"""
        user = info.context.get("user")
        if not user:
            raise Exception("Authentication required")

        db = next(get_db())
        try:
            db_conversation = db.query(models.Conversation).filter(
                models.Conversation.id == conversation_id,
                models.Conversation.user_id == user.id
            ).first()

            if not db_conversation:
                raise Exception("Conversation not found")

            # Update fields if provided
            if input.title is not None:
                db_conversation.title = input.title

            db_conversation.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_conversation)

            # Count messages in this conversation
            message_count = db.query(models.ChatMessage).filter(
                models.ChatMessage.conversation_id == db_conversation.id
            ).count()

            return Conversation(
                id=db_conversation.id,
                title=db_conversation.title,
                user_id=db_conversation.user_id,
                created_at=db_conversation.created_at,
                updated_at=db_conversation.updated_at,
                message_count=message_count
            )
        finally:
            db.close()

    @strawberry.field
    async def delete_conversation(
        self,
        info: Info,
        conversation_id: int
    ) -> bool:
        """Delete a conversation and all its messages"""
        user = info.context.get("user")
        if not user:
            raise Exception("Authentication required")

        db = next(get_db())
        try:
            db_conversation = db.query(models.Conversation).filter(
                models.Conversation.id == conversation_id,
                models.Conversation.user_id == user.id
            ).first()

            if not db_conversation:
                raise Exception("Conversation not found")

            db.delete(db_conversation)
            db.commit()
            return True
        finally:
            db.close()

    @strawberry.field
    async def chat_with_assistant(
        self,
        message: str,
        context: Optional[str] = None
    ) -> str:
        """Chat with AI assistant about crochet patterns and techniques"""
        db = next(get_db())
        try:
            # Get recent chat history for context (generous limit with 1M token context window)
            chat_history = get_recent_chat_history(db, limit=100)

            # Check if user is requesting a diagram
            if requests_diagram(message):
                # Generate diagram and include it in the response
                response = await _chat_with_diagram_generation(message, context, chat_history)
            else:
                # Regular chat with history
                response = await ai_service.chat_about_pattern(
                    message=message,
                    project_context=context or "",
                    chat_history=chat_history
                )

            # Store the conversation in database
            store_chat_message(db, message, response)

            return response
        except Exception as e:
            return f"I'm having trouble responding right now. Please try again in a moment. (Error: {str(e)})"
        finally:
            db.close()

    @strawberry.field
    async def chat_with_assistant_enhanced(
        self,
        info: Info,
        message: str,
        conversation_id: Optional[int] = None,
        context: Optional[str] = None
    ) -> ChatResponse:
        """Enhanced chat with AI assistant that can generate pattern diagrams"""
        user = info.context.get("user")

        db = next(get_db())
        try:
            # Get recent chat history for context (generous limit with 1M token context window)
            # If conversation_id is provided, filter by that conversation
            if conversation_id:
                chat_history = get_conversation_chat_history(db, conversation_id, limit=100)
            else:
                chat_history = get_recent_chat_history(db, user.id if user else None, limit=100)

            # Analyze user request for pattern type and diagram needs
            user_analysis = rag_service.analyze_user_request(message)

            # Use the AI service to get response with chat history
            ai_response = await ai_service.chat_about_pattern(
                message=message,
                project_context=context or "",
                chat_history=chat_history
            )

            # Check if the message or response contains pattern information
            has_pattern = contains_pattern_info(message + " " + ai_response)

            diagram_svg = None
            diagram_png = None

            # TODO: Diagram generation temporarily disabled - see CLAUDE.md for details
            # Frontend SVG rendering needs better detection logic to avoid duplicate rendering
            # Temporarily disabled until frontend rendering is fixed

            # Check if user is requesting a diagram AND we have pattern content
            if False:  # Temporarily disabled
                pass

            # Store the conversation in database
            store_chat_message(db, message, ai_response, user.id if user else None, None, conversation_id)

            return ChatResponse(
                message=ai_response,
                diagram_svg=diagram_svg,
                diagram_png=diagram_png,
                has_pattern=has_pattern
            )

        except Exception as e:
            # Return a friendly error message for users
            return ChatResponse(
                message=f"I'm having trouble responding right now. Please try again in a moment. (Error: {str(e)})",
                has_pattern=False
            )
        finally:
            db.close()

    @strawberry.field
    async def reset_daily_usage(self) -> ResetUsageResponse:
        """Reset all AI model usage for today"""
        try:
            result = ai_service.reset_daily_usage()
            return ResetUsageResponse(
                success=result["success"],
                message=result["message"],
                reset_date=result["reset_date"]
            )
        except Exception as e:
            return ResetUsageResponse(
                success=False,
                message=f"Failed to reset usage: {str(e)}",
                reset_date=None
            )

    @strawberry.field
    async def fetch_youtube_transcript(
        self,
        video_url: str,
        languages: Optional[list[str]] = None
    ) -> YouTubeTranscriptResponse:
        """Fetch transcript from a YouTube video"""
        try:
            result = youtube_service_rapidapi.get_transcript(video_url, languages)
            return YouTubeTranscriptResponse(
                success=result["success"],
                video_id=result.get("video_id"),
                transcript=result.get("transcript"),
                word_count=result.get("word_count"),
                language=result.get("language"),
                thumbnail_url=result.get("thumbnail_url"),
                thumbnail_url_hq=result.get("thumbnail_url_hq"),
                error=result.get("error")
            )
        except Exception as e:
            return YouTubeTranscriptResponse(
                success=False,
                error=f"Unexpected error: {str(e)}"
            )

    @strawberry.field
    async def extract_pattern_from_transcript(
        self,
        transcript: str,
        video_id: Optional[str] = None,
        thumbnail_url: Optional[str] = None
    ) -> ExtractedPattern:
        """Extract crochet pattern from YouTube video transcript using AI"""
        try:
            # Use AI to extract pattern information from transcript
            # Gemini 2.5 Flash has 1M token context, so we can use most of the transcript
            # Limit to ~100k characters (~25k tokens) to be safe
            prompt = f"""Analyze this YouTube video transcript and extract a crochet pattern if present.

Transcript:
{transcript[:100000]}

Please extract and format:
1. Pattern Name: A descriptive name for the pattern
2. Pattern Notation: The abbreviated crochet notation (e.g., "ch 4, 12 dc in ring, sl st")
3. Pattern Instructions: Step-by-step instructions in plain English
4. Difficulty Level: beginner, intermediate, or advanced
5. Materials: What yarn weight, hook size, etc. are mentioned
6. Estimated Time: If mentioned, how long to complete

If no clear pattern is found, return null for pattern fields and explain what was found instead.

Format your response as:
NAME: [pattern name]
NOTATION: [abbreviated notation]
INSTRUCTIONS: [detailed instructions]
DIFFICULTY: [level]
MATERIALS: [materials list]
TIME: [estimated time]
"""

            # Get AI response
            ai_response = await ai_service.chat_about_pattern(
                message=prompt,
                project_context="",
                chat_history=""
            )

            # Parse the AI response
            pattern_data = _parse_pattern_response(ai_response)

            if pattern_data:
                return ExtractedPattern(
                    success=True,
                    pattern_name=pattern_data.get("name"),
                    pattern_notation=pattern_data.get("notation"),
                    pattern_instructions=pattern_data.get("instructions"),
                    difficulty_level=pattern_data.get("difficulty"),
                    materials=pattern_data.get("materials"),
                    estimated_time=pattern_data.get("time"),
                    video_id=video_id,
                    thumbnail_url=thumbnail_url,
                    error=None
                )
            else:
                return ExtractedPattern(
                    success=False,
                    error="Could not extract a clear crochet pattern from the transcript",
                    video_id=video_id,
                    thumbnail_url=thumbnail_url
                )

        except Exception as e:
            return ExtractedPattern(
                success=False,
                error=f"Error extracting pattern: {str(e)}",
                video_id=video_id,
                thumbnail_url=thumbnail_url
            )

async def _chat_with_diagram_generation(message: str, context: Optional[str], chat_history: str = "") -> str:
    """Handle chat requests that include diagram generation"""
    try:
        # Get AI response first
        ai_response = await ai_service.chat_about_pattern(
            message=message,
            project_context=context or "",
            chat_history=chat_history
        )

        # Try to extract pattern from message or AI response for diagram
        pattern_text = extract_pattern_text(message, ai_response)

        if pattern_text:
            # Generate diagram
            pattern_data = pattern_service.parse_pattern_structure(pattern_text)

            if pattern_data.get('rounds') and len(pattern_data['rounds']) > 0:
                # Generate SVG diagram
                diagram_svg = pattern_service.generate_stitch_diagram_svg(pattern_data)

                # Append diagram info to response
                diagram_info = f"\n\n📊 **Pattern Diagram Generated:**\n"
                diagram_info += f"- Rounds: {pattern_data['total_rounds']}\n"
                diagram_info += f"- Pattern Type: {pattern_data['pattern_type']}\n"
                diagram_info += f"- Estimated Size: {pattern_data['estimated_size']}\n"
                diagram_info += f"- SVG diagram has been created with stitch symbols and legend\n"

                return ai_response + diagram_info
            else:
                return ai_response + "\n\n⚠️ I couldn't create a diagram from this pattern. Please provide a clearer pattern with round/row structure."
        else:
            # If no pattern found, offer to create an example
            example_response = f"\n\n📊 **I can create diagrams when you provide a crochet pattern!**\n\n"
            example_response += "Here's what I can visualize:\n"
            example_response += "- Round-based patterns (like amigurumi or granny squares)\n"
            example_response += "- Row-based patterns (like scarves or blankets)\n"
            example_response += "- Individual stitch techniques\n\n"
            example_response += "Just share a pattern like: 'Round 1: ch 3, 11 dc in magic ring, sl st to join' and I'll create a visual diagram for you!"

            return ai_response + example_response

    except Exception as e:
        return f"I had trouble generating the diagram: {str(e)}"


def requests_diagram(message: str) -> bool:
    """Check if user is explicitly requesting a diagram"""
    # More comprehensive diagram request patterns
    diagram_keywords = [
        # Direct diagram requests
        'diagram', 'visual', 'chart', 'drawing', 'picture',
        # Action words + diagram words
        'show', 'create', 'make', 'generate', 'draw', 'visualize',
        # Combined phrases
        'show me', 'can you draw', 'make a', 'create a'
    ]

    message_lower = message.lower()

    # Check for explicit diagram-related words
    has_diagram_word = any(word in message_lower for word in ['diagram', 'visual', 'chart', 'drawing', 'picture'])
    has_action_word = any(word in message_lower for word in ['show', 'create', 'make', 'generate', 'draw', 'visualize'])

    # If both are present, it's likely a diagram request
    if has_diagram_word and has_action_word:
        return True

    # Check for specific phrases
    specific_phrases = [
        'can you draw',
        'show me',
        'make a diagram',
        'create a visual',
        'visualize this',
        'draw a diagram',
        'show diagram',
        'create diagram'
    ]

    return any(phrase in message_lower for phrase in specific_phrases)


def contains_pattern_info(text: str) -> bool:
    """Check if text contains crochet pattern information"""
    pattern_indicators = [
        r'\b(?:round|rnd|row)\s*\d+',
        r'\b(?:sc|dc|hdc|tc|sl st|ch)\b',
        r'magic ring|magic circle',
        r'\d+\s*(?:sc|dc|hdc|tc)',
        r'foundation(?:\s+chain)?',
        r'(?:increase|decrease|inc|dec)',
        r'stitch(?:es)?\s+into',
        r'chain\s+\d+',
        r'pattern:',
        r'instructions:'
    ]

    text_lower = text.lower()
    return any(re.search(pattern, text_lower) for pattern in pattern_indicators)


def extract_pattern_text(message: str, ai_response: str) -> Optional[str]:
    """Extract pattern text from message or AI response"""
    combined_text = message + "\n" + ai_response

    # Look for explicit pattern sections
    pattern_match = re.search(r'(?:pattern:|instructions?:)(.*?)(?:\n\n|\Z)', combined_text, re.DOTALL | re.IGNORECASE)
    if pattern_match:
        return pattern_match.group(1).strip()

    # Look for round/row based patterns
    round_matches = re.findall(r'(?:round|rnd|row)\s*\d+:.*?(?=(?:round|rnd|row)\s*\d+|$)', combined_text, re.IGNORECASE | re.DOTALL)
    if round_matches:
        return "\n".join(round_matches)

    # If message looks like it contains a pattern, return the whole message
    if contains_pattern_info(message) and len(message.split()) > 5:
        return message

    return None


def get_recent_chat_history(db: Session, user_id: int = None, limit: int = 100) -> str:
    """Get recent chat history formatted for AI context"""
    query = db.query(models.ChatMessage)

    if user_id:
        query = query.filter(models.ChatMessage.user_id == user_id)

    # Get recent messages ordered by creation time
    recent_messages = query.order_by(models.ChatMessage.created_at.desc()).limit(limit).all()

    if not recent_messages:
        return ""

    # Format as conversation history (reverse to chronological order)
    history_parts = []
    for msg in reversed(recent_messages):
        history_parts.append(f"User: {msg.message}")
        history_parts.append(f"Assistant: {msg.response}")

    return "\n".join(history_parts)


def get_conversation_chat_history(db: Session, conversation_id: int, limit: int = 100) -> str:
    """Get chat history for a specific conversation formatted for AI context"""
    # Get messages in this conversation ordered by creation time
    messages = db.query(models.ChatMessage).filter(
        models.ChatMessage.conversation_id == conversation_id
    ).order_by(models.ChatMessage.created_at.desc()).limit(limit).all()

    if not messages:
        return ""

    # Format as conversation history (reverse to chronological order)
    history_parts = []
    for msg in reversed(messages):
        history_parts.append(f"User: {msg.message}")
        history_parts.append(f"Assistant: {msg.response}")

    return "\n".join(history_parts)


def store_chat_message(db: Session, user_message: str, ai_response: str, user_id: int = None, project_id: int = None, conversation_id: int = None) -> None:
    """Store chat message and response in database"""
    chat_message = models.ChatMessage(
        message=user_message,
        response=ai_response,
        user_id=user_id,
        project_id=project_id,
        conversation_id=conversation_id,
        created_at=datetime.utcnow()
    )

    db.add(chat_message)
    db.commit()

    # Update conversation's updated_at timestamp if conversation_id is provided
    if conversation_id:
        conversation = db.query(models.Conversation).filter(
            models.Conversation.id == conversation_id
        ).first()
        if conversation:
            conversation.updated_at = datetime.utcnow()
            db.commit()


def _parse_pattern_response(ai_response: str) -> Optional[dict]:
    """Parse AI response for pattern extraction"""
    try:
        pattern_data = {}

        # Extract fields using regex
        name_match = re.search(r'NAME:\s*(.+?)(?:\n|$)', ai_response, re.IGNORECASE)
        notation_match = re.search(r'NOTATION:\s*(.+?)(?=\nINSTRUCTIONS:|$)', ai_response, re.IGNORECASE | re.DOTALL)
        instructions_match = re.search(r'INSTRUCTIONS:\s*(.+?)(?=\nDIFFICULTY:|$)', ai_response, re.IGNORECASE | re.DOTALL)
        difficulty_match = re.search(r'DIFFICULTY:\s*(.+?)(?:\n|$)', ai_response, re.IGNORECASE)
        materials_match = re.search(r'MATERIALS:\s*(.+?)(?=\nTIME:|$)', ai_response, re.IGNORECASE | re.DOTALL)
        time_match = re.search(r'TIME:\s*(.+?)(?:\n|$)', ai_response, re.IGNORECASE)

        if name_match:
            pattern_data["name"] = name_match.group(1).strip()
        if notation_match:
            pattern_data["notation"] = notation_match.group(1).strip()
        if instructions_match:
            pattern_data["instructions"] = instructions_match.group(1).strip()
        if difficulty_match:
            difficulty = difficulty_match.group(1).strip().lower()
            # Validate difficulty
            if difficulty in ['beginner', 'intermediate', 'advanced']:
                pattern_data["difficulty"] = difficulty
        if materials_match:
            pattern_data["materials"] = materials_match.group(1).strip()
        if time_match:
            pattern_data["time"] = time_match.group(1).strip()

        # Return pattern data if at least name and notation are found
        if pattern_data.get("name") and pattern_data.get("notation"):
            return pattern_data

        return None

    except Exception:
        return None