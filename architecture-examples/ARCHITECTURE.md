# Architecture File Structure

```
architecture-examples/
├── README.md                           # Architecture overview and getting started
├── CLAUDE.md                          # Complete setup documentation
├── ARCHITECTURE.md                    # This file - structure diagram
│
├── deploy-backend-to-oci.sh          # Backend deployment script
├── docker-compose.backend-postgres.yml # Production Docker configuration
│
├── backend/                           # FastAPI + GraphQL Backend
│   ├── Dockerfile                     # Backend container definition
│   ├── requirements.txt               # Python dependencies
│   └── app/
│       ├── main.py                    # FastAPI application entry point
│       ├── core/
│       │   └── config.py              # Environment configuration
│       ├── database/
│       │   └── models.py              # SQLAlchemy database models
│       ├── schemas/                   # GraphQL schema definitions
│       │   ├── queries.py             # GraphQL queries
│       │   └── mutations.py           # GraphQL mutations
│       └── utils/
│           └── auth.py                # JWT authentication utilities
│
└── frontend/                          # Next.js Frontend (Vercel deployment)
    ├── package.json                   # Dependencies and scripts
    ├── next.config.js                 # Next.js configuration
    └── src/
        └── lib/
            └── apollo-client.ts       # GraphQL client setup
```

## Key Architecture Components

### Deployment Pattern
```
┌─────────────────┐    GraphQL/HTTP    ┌─────────────────┐
│   Vercel CDN    │ ────────────────► │   OCI Server    │
│   (Frontend)    │                   │   (Backend)     │
│   Next.js App   │ ◄──────────────── │   FastAPI +     │
│                 │                   │   PostgreSQL    │
└─────────────────┘                   └─────────────────┘
```

### Backend Stack
- **FastAPI**: Python web framework
- **Strawberry GraphQL**: GraphQL schema and resolvers
- **PostgreSQL**: Database with Docker persistence
- **JWT Authentication**: Token-based auth with bcrypt
- **Docker**: Containerized deployment

### Frontend Stack
- **Next.js 15**: React framework with TypeScript
- **Apollo Client**: GraphQL client with caching
- **Vercel**: Auto-deployment from Git

### Environment Variables

**Backend (.env on OCI server):**
```
CORS_ORIGINS=https://your-frontend-domain.com
GITHUB_TOKEN=ghp_***
ADMIN_SECRET=your-admin-secret
DATABASE_URL=postgresql://...
```

**Frontend (Vercel environment):**
```
NEXT_PUBLIC_GRAPHQL_URL=https://your-backend-domain.com/cryptassist/graphql
```

## Deployment Workflow

1. **Backend**: Push to Git → Run `./deploy-backend-to-oci.sh IP_ADDRESS`
2. **Frontend**: Push to Git → Vercel auto-deploys
3. **Database**: Persistent via Docker volumes

## Essential Files for Replication

1. **`deploy-backend-to-oci.sh`** - Deployment automation
2. **`docker-compose.backend-postgres.yml`** - Production setup
3. **`backend/app/main.py`** - FastAPI + GraphQL setup
4. **`backend/app/core/config.py`** - Environment management
5. **`frontend/src/lib/apollo-client.ts`** - GraphQL client config
6. **`CLAUDE.md`** - Complete documentation