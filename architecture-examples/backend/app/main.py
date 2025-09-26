import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from app.schemas.schema import schema
from app.database.connection import create_tables
from app.services.cache_refresh import cache_refresh_service

app = FastAPI(
    title="Crypto Portfolio Analyzer API",
    description="Real-time cryptocurrency portfolio tracking and analysis",
    version="1.0.0"
)

# Create database tables and start background services on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

    # Start background cache refresh service
    await cache_refresh_service.start_background_refresh()

    # Warm up the cache on startup
    await cache_refresh_service.manual_refresh("warm_cache")

@app.on_event("shutdown")
async def shutdown_event():
    # Stop background cache refresh service
    await cache_refresh_service.stop_background_refresh()

# CORS middleware
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GraphQL endpoint with admin-only playground access  
async def check_admin_or_debug_access(request):
    """Check if user has admin access or if we're in debug mode"""
    # Always allow in debug mode (local development)
    debug_mode = os.getenv("DEBUG", "false").lower() == "true"
    if debug_mode:
        return True
    
    # In production, check if user is admin
    authorization = request.headers.get("authorization", "")
    if not authorization.startswith("Bearer "):
        return False
    
    token = authorization.split(" ")[1]
    
    from app.database.connection import get_db
    from app.utils.auth import get_current_user_from_token, is_user_admin
    
    db = next(get_db())
    try:
        current_user = get_current_user_from_token(token, db)
        return is_user_admin(current_user)
    except:
        return False
    finally:
        db.close()

# Custom GraphQL app with admin-only playground in production
from strawberry.fastapi import GraphQLRouter
from fastapi import HTTPException

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
graphql_app = AdminControlledGraphQLRouter(schema, graphiql=True)
app.include_router(graphql_app, prefix="/cryptassist/graphql")

@app.get("/")
async def root():
    return {"message": "Crypto Portfolio Analyzer API"}

@app.get("/cryptassist/health")
async def health():
    return {"status": "healthy"}