import strawberry
from datetime import datetime
from typing import Optional
from strawberry.types import Info
from app.database.connection import get_db
from app.database import models
from app.schemas.types import (
    User, AuthResponse, CrochetProject, ChatResponse, ResetUsageResponse,
    RegisterInput, LoginInput, CreateProjectInput
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
                difficulty_level=input.difficulty_level,
                estimated_time=input.estimated_time,
                yarn_weight=input.yarn_weight,
                hook_size=input.hook_size,
                notes=input.notes,
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
        message: str,
        context: Optional[str] = None
    ) -> ChatResponse:
        """Enhanced chat with AI assistant that can generate pattern diagrams"""
        db = next(get_db())
        try:
            # Get recent chat history for context (generous limit with 1M token context window)
            chat_history = get_recent_chat_history(db, limit=100)

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
            store_chat_message(db, message, ai_response)

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


def store_chat_message(db: Session, user_message: str, ai_response: str, user_id: int = None, project_id: int = None) -> None:
    """Store chat message and response in database"""
    chat_message = models.ChatMessage(
        message=user_message,
        response=ai_response,
        user_id=user_id,
        project_id=project_id,
        created_at=datetime.utcnow()
    )

    db.add(chat_message)
    db.commit()