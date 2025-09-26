import strawberry
from typing import List, Optional
from strawberry.types import Info
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
                is_completed=project.is_completed,
                user_id=project.user_id,
                created_at=project.created_at,
                updated_at=project.updated_at
            )
        finally:
            db.close()