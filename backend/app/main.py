import os
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from sqlalchemy.orm import Session
from app.schemas.schema import schema
from app.database.connection import create_tables, get_db
from app.database.models import User
from app.utils.auth import get_current_user_from_token, is_user_admin
from app.core.config import settings

app = FastAPI(
    title="Crooked Finger Crochet Assistant API",
    description="AI-powered crochet pattern translation and diagram generation",
    version="1.0.0"
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()
    print("✅ Database tables created")
    print(f"🚀 Crooked Finger API starting on port 8001")
    print(f"🔧 Environment: {settings.environment}")
    print(f"🎯 GraphQL endpoint: /crooked-finger/graphql")

# CORS middleware
cors_origins = settings.cors_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication middleware for GraphQL context
async def get_context(request: Request, db: Session = Depends(get_db)):
    """Add user to GraphQL context if authenticated"""
    context = {"request": request}

    authorization = request.headers.get("authorization", "")
    if authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        try:
            user = get_current_user_from_token(token, db)
            if user:
                # Add user to request for GraphQL resolvers
                request.user = user
                context["user"] = user
        except Exception:
            pass  # Invalid token, continue without user

    # TODO: Re-enable auth requirement when bcrypt is fixed
    # In debug mode, provide a default user if no auth token
    if settings.debug and "user" not in context:
        # Get or create a default debug user
        default_user = db.query(User).filter(User.email == "debug@crookedfinger.com").first()
        if not default_user:
            # Create default debug user if it doesn't exist
            from app.utils.auth import get_password_hash
            default_user = User(
                email="debug@crookedfinger.com",
                hashed_password=get_password_hash("debug"),
                is_active=True,
                is_verified=True,
                is_admin=False
            )
            db.add(default_user)
            db.commit()
            db.refresh(default_user)
        request.user = default_user
        context["user"] = default_user

    return context

# GraphQL endpoint access control (similar to CryptAssist)
async def check_admin_or_debug_access(request: Request):
    """Check if user has admin access or if we're in debug mode"""
    # Always allow in debug mode (local development)
    if settings.debug:
        return True

    # In production, check if user is admin
    authorization = request.headers.get("authorization", "")
    if not authorization.startswith("Bearer "):
        return False

    token = authorization.split(" ")[1]

    from app.database.connection import get_db

    db = next(get_db())
    try:
        current_user = get_current_user_from_token(token, db)
        return is_user_admin(current_user)
    except:
        return False
    finally:
        db.close()

class AdminControlledGraphQLRouter(GraphQLRouter):
    async def render_graphiql_page(self, request: Request):
        """Override GraphiQL rendering to check admin access"""
        is_allowed = await check_admin_or_debug_access(request)
        if not is_allowed:
            raise HTTPException(
                status_code=403,
                detail="GraphQL playground access restricted to administrators. Please login with admin credentials."
            )
        return await super().render_graphiql_page(request)

# Create GraphQL router with admin controls
graphql_app = AdminControlledGraphQLRouter(
    schema,
    graphiql=True,
    context_getter=get_context
)
app.include_router(graphql_app, prefix="/crooked-finger/graphql")

@app.get("/")
async def root():
    return {
        "message": "Crooked Finger Crochet Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "graphql": "/crooked-finger/graphql",
            "health": "/crooked-finger/health"
        }
    }

@app.get("/crooked-finger/health")
async def health():
    return {
        "status": "healthy",
        "service": "crooked-finger",
        "version": "1.0.0"
    }