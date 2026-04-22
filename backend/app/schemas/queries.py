import strawberry
from typing import List, Optional
from strawberry.types import Info
from sqlalchemy import func
from app.database.connection import get_db
from app.database import models
from app.schemas.types import User, CrochetProject, Conversation, ChatMessage, ProjectDiagram

@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello from Crooked Finger API!"

    @strawberry.field
    def projects(
        self,
        info: Info
    ) -> List[CrochetProject]:
        """Get all projects for the authenticated user"""
        user = info.context.get("user")
        if not user:
            return []

        db = next(get_db())
        try:
            db_projects = db.query(models.CrochetProject).filter(
                models.CrochetProject.user_id == user.id
            ).all()

            return [
                CrochetProject(
                    id=project.id,
                    name=project.name,
                    pattern_text=project.pattern_text,
                    translated_text=project.translated_text,
                    difficulty_level=project.difficulty_level,
                    estimated_time=project.estimated_time,
                    yarn_weight=project.yarn_weight,
                    hook_size=project.hook_size,
                    notes=project.notes,
                    image_data=project.image_data,
                    is_completed=project.is_completed,
                    user_id=project.user_id,
                    created_at=project.created_at,
                    updated_at=project.updated_at
                )
                for project in db_projects
            ]
        finally:
            db.close()

    @strawberry.field
    def project(
        self,
        info: Info,
        project_id: int
    ) -> Optional[CrochetProject]:
        """Get a specific project by ID"""
        user = info.context.get("user")
        if not user:
            return None

        db = next(get_db())
        try:
            project = db.query(models.CrochetProject).filter(
                models.CrochetProject.id == project_id,
                models.CrochetProject.user_id == user.id
            ).first()

            if not project:
                return None

            return CrochetProject(
                id=project.id,
                name=project.name,
                pattern_text=project.pattern_text,
                translated_text=project.translated_text,
                difficulty_level=project.difficulty_level,
                estimated_time=project.estimated_time,
                yarn_weight=project.yarn_weight,
                hook_size=project.hook_size,
                notes=project.notes,
                image_data=project.image_data,
                is_completed=project.is_completed,
                user_id=project.user_id,
                created_at=project.created_at,
                updated_at=project.updated_at
            )
        finally:
            db.close()

    @strawberry.field
    def chat_messages(
        self,
        info: Info,
        conversation_id: Optional[int] = None,
        project_id: Optional[int] = None,
        limit: int = 100
    ) -> List[ChatMessage]:
        """Get chat messages, optionally filtered by conversation or project"""
        user = info.context.get("user")
        if not user:
            return []

        db = next(get_db())
        try:
            query = db.query(models.ChatMessage).filter(
                models.ChatMessage.user_id == user.id
            )

            if conversation_id:
                query = query.filter(models.ChatMessage.conversation_id == conversation_id)

            if project_id:
                query = query.filter(models.ChatMessage.project_id == project_id)

            chat_messages = query.order_by(
                models.ChatMessage.created_at.asc()  # Changed to asc for chronological order
            ).limit(limit).all()

            return [
                ChatMessage(
                    id=msg.id,
                    message=msg.message,
                    response=msg.response,
                    message_type=msg.message_type,
                    conversation_id=msg.conversation_id,
                    project_id=msg.project_id,
                    user_id=msg.user_id,
                    created_at=msg.created_at
                )
                for msg in chat_messages
            ]
        finally:
            db.close()

    @strawberry.field
    def conversations(
        self,
        info: Info,
        limit: int = 50
    ) -> List[Conversation]:
        """Get all conversations for the authenticated user"""
        user = info.context.get("user")
        if not user:
            return []

        db = next(get_db())
        try:
            # Single query with LEFT JOIN + GROUP BY to get message counts
            rows = db.query(
                models.Conversation,
                func.count(models.ChatMessage.id).label("message_count")
            ).outerjoin(
                models.ChatMessage,
                models.ChatMessage.conversation_id == models.Conversation.id
            ).filter(
                models.Conversation.user_id == user.id
            ).group_by(
                models.Conversation.id
            ).order_by(
                models.Conversation.updated_at.desc()
            ).limit(limit).all()

            return [
                Conversation(
                    id=conv.id,
                    title=conv.title,
                    user_id=conv.user_id,
                    created_at=conv.created_at,
                    updated_at=conv.updated_at,
                    message_count=message_count
                )
                for conv, message_count in rows
            ]
        finally:
            db.close()

    @strawberry.field
    def conversation(
        self,
        info: Info,
        conversation_id: int
    ) -> Optional[Conversation]:
        """Get a specific conversation by ID"""
        user = info.context.get("user")
        if not user:
            return None

        db = next(get_db())
        try:
            row = db.query(
                models.Conversation,
                func.count(models.ChatMessage.id).label("message_count")
            ).outerjoin(
                models.ChatMessage,
                models.ChatMessage.conversation_id == models.Conversation.id
            ).filter(
                models.Conversation.id == conversation_id,
                models.Conversation.user_id == user.id
            ).group_by(
                models.Conversation.id
            ).first()

            if not row:
                return None

            conv, message_count = row
            return Conversation(
                id=conv.id,
                title=conv.title,
                user_id=conv.user_id,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=message_count
            )
        finally:
            db.close()

