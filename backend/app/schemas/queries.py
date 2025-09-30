import strawberry
from typing import List, Optional
from strawberry.types import Info
from app.database.connection import get_db
from app.database import models
from app.schemas.types import User, CrochetProject, ChatMessage, ProjectDiagram, AIUsageDashboard, ModelUsageStats
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
            total_remaining += data["remaining"]

        return AIUsageDashboard(
            total_requests_today=total_requests,
            total_remaining=total_remaining,
            models=model_stats
        )