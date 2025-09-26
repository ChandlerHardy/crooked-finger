import strawberry
from typing import List, Optional
from app.database.connection import get_db
from app.database import models
from app.schemas.types import User, CrochetProject, ChatMessage, ProjectDiagram

@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello from Crooked Finger API!"

    @strawberry.field
    def projects(
        self,
        info: strawberry.Info
    ) -> List[CrochetProject]:
        """Get all projects for the authenticated user"""
        # Get user from context (will be set by authentication middleware)
        user = getattr(info.context.get("request", {}), "user", None)
        if not user:
            return []

        # Get database session from context
        db = next(get_db())
        try:
            db_projects = db.query(models.CrochetProject).filter(
                models.CrochetProject.user_id == user.id
            ).all()
        finally:
            db.close()

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
                is_completed=project.is_completed,
                user_id=project.user_id,
                created_at=project.created_at,
                updated_at=project.updated_at
            )
            for project in db_projects
        ]

    @strawberry.field
    def project(
        self,
        info: strawberry.Info,
        project_id: int
    ) -> Optional[CrochetProject]:
        """Get a specific project by ID"""
        user = getattr(info.context.get("request", {}), "user", None)
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
        finally:
            db.close()

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
            is_completed=project.is_completed,
            user_id=project.user_id,
            created_at=project.created_at,
            updated_at=project.updated_at
        )

    @strawberry.field
    def chat_history(
        self,
        info: strawberry.Info,
        project_id: Optional[int] = None,
        limit: int = 50,
        db: Session = Depends(get_db)
    ) -> List[ChatMessage]:
        """Get chat history for a user, optionally filtered by project"""
        user = getattr(info.context.get("request", {}), "user", None)
        if not user:
            return []

        query = db.query(models.ChatMessage).filter(
            models.ChatMessage.user_id == user.id
        )

        if project_id:
            query = query.filter(models.ChatMessage.project_id == project_id)

        messages = query.order_by(models.ChatMessage.created_at.desc()).limit(limit).all()

        return [
            ChatMessage(
                id=message.id,
                message=message.message,
                response=message.response,
                message_type=message.message_type,
                project_id=message.project_id,
                user_id=message.user_id,
                created_at=message.created_at
            )
            for message in messages
        ]

    @strawberry.field
    def project_diagrams(
        self,
        info: strawberry.Info,
        project_id: int,
        db: Session = Depends(get_db)
    ) -> List[ProjectDiagram]:
        """Get all diagrams for a specific project"""
        user = getattr(info.context.get("request", {}), "user", None)
        if not user:
            return []

        # Verify user owns the project
        project = db.query(models.CrochetProject).filter(
            models.CrochetProject.id == project_id,
            models.CrochetProject.user_id == user.id
        ).first()

        if not project:
            return []

        diagrams = db.query(models.ProjectDiagram).filter(
            models.ProjectDiagram.project_id == project_id
        ).all()

        return [
            ProjectDiagram(
                id=diagram.id,
                diagram_data=diagram.diagram_data,
                diagram_type=diagram.diagram_type,
                diagram_format=diagram.diagram_format,
                project_id=diagram.project_id,
                created_at=diagram.created_at
            )
            for diagram in diagrams
        ]