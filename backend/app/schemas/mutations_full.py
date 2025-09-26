import strawberry
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from app.database.connection import get_db
from app.database import models
from app.schemas.types import (
    User, AuthResponse, CrochetProject, ChatMessage, ProjectDiagram,
    RegisterInput, LoginInput, CreateProjectInput, UpdateProjectInput,
    TranslationResponse, PatternAnalysis
)
from app.utils.auth import (
    get_password_hash, authenticate_user, create_access_token,
    get_current_user_from_token, is_user_admin
)
from app.services.ai_service import ai_service
from app.services.pattern_service import pattern_service
from app.core.config import settings

@strawberry.type
class Mutation:
    @strawberry.field
    async def register(
        self,
        input: RegisterInput,
        db: Session = Depends(get_db)
    ) -> AuthResponse:
        """Register a new user"""
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

    @strawberry.field
    async def login(
        self,
        input: LoginInput,
        db: Session = Depends(get_db)
    ) -> AuthResponse:
        """Login user"""
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

    @strawberry.field
    async def create_admin_user(
        self,
        email: str,
        password: str,
        admin_secret: str,
        db: Session = Depends(get_db)
    ) -> AuthResponse:
        """Create an admin user (requires admin secret)"""
        if admin_secret != settings.admin_secret:
            raise Exception("Invalid admin secret")

        # Check if user already exists
        existing_user = db.query(models.User).filter(models.User.email == email).first()
        if existing_user:
            raise Exception("User with this email already exists")

        # Create admin user
        hashed_password = get_password_hash(password)
        db_user = models.User(
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            is_admin=True,
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

    @strawberry.field
    async def create_project(
        self,
        info: strawberry.Info,
        input: CreateProjectInput,
        db: Session = Depends(get_db)
    ) -> CrochetProject:
        """Create a new crochet project"""
        user = getattr(info.context.get("request", {}), "user", None)
        if not user:
            raise Exception("Authentication required")

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

    @strawberry.field
    async def update_project(
        self,
        info: strawberry.Info,
        project_id: int,
        input: UpdateProjectInput,
        db: Session = Depends(get_db)
    ) -> Optional[CrochetProject]:
        """Update an existing project"""
        user = getattr(info.context.get("request", {}), "user", None)
        if not user:
            raise Exception("Authentication required")

        project = db.query(models.CrochetProject).filter(
            models.CrochetProject.id == project_id,
            models.CrochetProject.user_id == user.id
        ).first()

        if not project:
            raise Exception("Project not found")

        # Update fields if provided
        if input.name is not None:
            project.name = input.name
        if input.pattern_text is not None:
            project.pattern_text = input.pattern_text
        if input.translated_text is not None:
            project.translated_text = input.translated_text
        if input.difficulty_level is not None:
            project.difficulty_level = input.difficulty_level
        if input.estimated_time is not None:
            project.estimated_time = input.estimated_time
        if input.yarn_weight is not None:
            project.yarn_weight = input.yarn_weight
        if input.hook_size is not None:
            project.hook_size = input.hook_size
        if input.notes is not None:
            project.notes = input.notes
        if input.is_completed is not None:
            project.is_completed = input.is_completed

        project.updated_at = datetime.utcnow()
        db.commit()

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
    async def translate_pattern(
        self,
        info: strawberry.Info,
        pattern_text: str,
        project_id: Optional[int] = None,
        db: Session = Depends(get_db)
    ) -> TranslationResponse:
        """Translate crochet pattern using AI"""
        user = getattr(info.context.get("request", {}), "user", None)
        if not user:
            raise Exception("Authentication required")

        # Get project context if provided
        project_context = ""
        if project_id:
            project = db.query(models.CrochetProject).filter(
                models.CrochetProject.id == project_id,
                models.CrochetProject.user_id == user.id
            ).first()
            if project:
                project_context = f"Project: {project.name}"
                if project.yarn_weight:
                    project_context += f", Yarn: {project.yarn_weight}"
                if project.hook_size:
                    project_context += f", Hook: {project.hook_size}"

        # Translate pattern using AI
        translated_instructions = await ai_service.translate_crochet_pattern(
            pattern_text, project_context
        )

        # Analyze pattern structure
        pattern_data = pattern_service.parse_pattern_structure(pattern_text)
        analysis = PatternAnalysis(
            total_rounds=pattern_data['total_rounds'],
            pattern_type=pattern_data['pattern_type'],
            estimated_size=pattern_data['estimated_size'],
            stitch_count_by_round=[r['stitches'] for r in pattern_data['rounds']]
        )

        # Update project if provided
        if project_id:
            project = db.query(models.CrochetProject).filter(
                models.CrochetProject.id == project_id,
                models.CrochetProject.user_id == user.id
            ).first()
            if project:
                project.translated_text = translated_instructions
                project.updated_at = datetime.utcnow()
                db.commit()

        return TranslationResponse(
            original_pattern=pattern_text,
            translated_instructions=translated_instructions,
            analysis=analysis
        )

    @strawberry.field
    async def chat_with_assistant(
        self,
        info: strawberry.Info,
        message: str,
        project_id: Optional[int] = None,
        db: Session = Depends(get_db)
    ) -> str:
        """Chat with AI assistant about crochet"""
        user = getattr(info.context.get("request", {}), "user", None)
        if not user:
            raise Exception("Authentication required")

        # Get project context
        project_context = ""
        if project_id:
            project = db.query(models.CrochetProject).filter(
                models.CrochetProject.id == project_id,
                models.CrochetProject.user_id == user.id
            ).first()
            if project:
                project_context = f"Current project: {project.name}\n"
                if project.pattern_text:
                    project_context += f"Pattern: {project.pattern_text[:200]}...\n"
                if project.translated_text:
                    project_context += f"Translation: {project.translated_text[:200]}...\n"

        # Get recent chat history
        recent_chats = db.query(models.ChatMessage).filter(
            models.ChatMessage.user_id == user.id,
            models.ChatMessage.project_id == project_id if project_id else True
        ).order_by(models.ChatMessage.created_at.desc()).limit(3).all()

        chat_history = ""
        for chat in reversed(recent_chats):
            chat_history += f"User: {chat.message}\nAssistant: {chat.response}\n\n"

        # Get AI response
        response = await ai_service.chat_about_pattern(message, project_context, chat_history)

        # Save chat message
        chat_message = models.ChatMessage(
            message=message,
            response=response,
            message_type="question",
            project_id=project_id,
            user_id=user.id,
            created_at=datetime.utcnow()
        )

        db.add(chat_message)
        db.commit()

        return response

    @strawberry.field
    async def generate_diagram(
        self,
        info: strawberry.Info,
        project_id: int,
        diagram_type: str = "stitch_diagram",
        db: Session = Depends(get_db)
    ) -> Optional[ProjectDiagram]:
        """Generate a diagram for a project"""
        user = getattr(info.context.get("request", {}), "user", None)
        if not user:
            raise Exception("Authentication required")

        # Get project
        project = db.query(models.CrochetProject).filter(
            models.CrochetProject.id == project_id,
            models.CrochetProject.user_id == user.id
        ).first()

        if not project or not project.pattern_text:
            raise Exception("Project not found or has no pattern")

        # Parse pattern and generate diagram
        pattern_data = pattern_service.parse_pattern_structure(project.pattern_text)

        if diagram_type == "stitch_diagram":
            diagram_data = pattern_service.generate_stitch_diagram_svg(pattern_data)
            diagram_format = "svg"
        elif diagram_type == "pattern_chart":
            diagram_data = pattern_service.generate_pattern_chart_png(pattern_data)
            diagram_format = "png"
        else:
            raise Exception("Unsupported diagram type")

        # Save diagram
        db_diagram = models.ProjectDiagram(
            diagram_data=diagram_data,
            diagram_type=diagram_type,
            diagram_format=diagram_format,
            project_id=project_id,
            created_at=datetime.utcnow()
        )

        db.add(db_diagram)
        db.commit()
        db.refresh(db_diagram)

        return ProjectDiagram(
            id=db_diagram.id,
            diagram_data=db_diagram.diagram_data,
            diagram_type=db_diagram.diagram_type,
            diagram_format=db_diagram.diagram_format,
            project_id=db_diagram.project_id,
            created_at=db_diagram.created_at
        )