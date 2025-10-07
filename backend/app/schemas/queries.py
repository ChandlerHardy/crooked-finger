import strawberry
from typing import List, Optional
from strawberry.types import Info
from app.database.connection import get_db
from app.database import models
from app.schemas.types import User, CrochetProject, Conversation, ChatMessage, ProjectDiagram, AIUsageDashboard, ModelUsageStats, AIProviderConfig
from app.services.ai_service import ai_service

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
            db_conversations = db.query(models.Conversation).filter(
                models.Conversation.user_id == user.id
            ).order_by(
                models.Conversation.updated_at.desc()
            ).limit(limit).all()

            result = []
            for conv in db_conversations:
                # Count messages in this conversation
                message_count = db.query(models.ChatMessage).filter(
                    models.ChatMessage.conversation_id == conv.id
                ).count()

                result.append(Conversation(
                    id=conv.id,
                    title=conv.title,
                    user_id=conv.user_id,
                    created_at=conv.created_at,
                    updated_at=conv.updated_at,
                    message_count=message_count
                ))

            return result
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
            conv = db.query(models.Conversation).filter(
                models.Conversation.id == conversation_id,
                models.Conversation.user_id == user.id
            ).first()

            if not conv:
                return None

            # Count messages in this conversation
            message_count = db.query(models.ChatMessage).filter(
                models.ChatMessage.conversation_id == conv.id
            ).count()

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

    @strawberry.field
    def ai_usage_dashboard(self) -> AIUsageDashboard:
        """Get AI model usage statistics dashboard"""
        stats = ai_service.get_usage_stats()

        # Convert to GraphQL types
        model_stats = []
        total_requests = 0
        total_remaining = 0

        for model_name, data in stats.items():
            model_stats.append(ModelUsageStats(
                model_name=model_name,
                current_usage=data["current_usage"],
                daily_limit=data["daily_limit"],
                remaining=data["remaining"],
                percentage_used=data["percentage_used"],
                priority=data["priority"],
                use_case=data["use_case"],
                total_input_characters=data["total_input_characters"],
                total_output_characters=data["total_output_characters"],
                total_input_tokens=data["total_input_tokens"],
                total_output_tokens=data["total_output_tokens"]
            ))
            total_requests += data["current_usage"]
            # Only count limited models in total remaining (exclude unlimited with 999999 limit)
            if data["daily_limit"] < 999999:
                total_remaining += data["remaining"]

        return AIUsageDashboard(
            total_requests_today=total_requests,
            total_remaining=total_remaining,
            models=model_stats
        )

    @strawberry.field
    def ai_provider_config(self) -> AIProviderConfig:
        """Get current AI provider configuration"""
        config = ai_service.get_ai_provider_config()
        return AIProviderConfig(
            use_openrouter=config["use_openrouter"],
            current_provider=config["current_provider"],
            selected_model=config.get("selected_model"),
            available_models=config.get("available_models", []),
            model_priority_order=config.get("model_priority_order", [])
        )