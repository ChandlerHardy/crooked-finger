# Claude Code Project Information

## Project Overview
Crooked Finger - A crochet and knitting pattern assistant with AI-powered pattern translation and diagram generation.

## Tech Stack
- **Frontend**: Next.js 15 + TypeScript, Tailwind CSS, Apollo GraphQL
- **Backend**: FastAPI + Strawberry GraphQL, PostgreSQL
- **AI**: z.ai Anthropic-compatible proxy (routes to GLM-4.7 for translation, GLM-4.5-Air for chat)
- **Diagram Generation**: Professional matplotlib charts + traditional SVG generators
- **Deployment**: Vercel (frontend) + Oracle Cloud Infrastructure (backend)

## 🖥️ Server Access
**OCI Server:**
- **SSH**: `ssh ubuntu@<your-oci-ip> -i /Users/chandlerhardy/.ssh/ampere.key`
- **Location**: `/home/ubuntu/crooked-finger/`

## Port Allocation
**CryptAssist uses:** Port 8000, 5432 (PostgreSQL), 6379 (Redis)
**Crooked-Finger uses:** Port 8001 (Backend API), 5433 (PostgreSQL), 6380 (Redis)

## 🚀 Live Production URLs
- **Main App**: https://crookedfinger.chandlerhardy.com
- **Backend API**: https://backend.chandlerhardy.com
- **GraphQL**: https://backend.chandlerhardy.com/crooked-finger/graphql
- **Health Check**: https://backend.chandlerhardy.com/crooked-finger/health

## ⚙️ Key Environment Variables
**Backend (.env on OCI server):**
- `ZAI_API_KEY=***` (z.ai subscription key - DO NOT COMMIT)
- `CORS_ORIGINS=https://crookedfinger.chandlerhardy.com,https://crooked-finger-app.vercel.app,https://backend.chandlerhardy.com,http://localhost:3000,http://localhost:3001`
- `ADMIN_SECRET=***` (DO NOT COMMIT)
- `DATABASE_URL=postgresql://crochet_user:***@postgres:5432/crooked_finger_db`

**Frontend (.env.local):**
- `NEXT_PUBLIC_GRAPHQL_URL=http://localhost:8001/crooked-finger/graphql`

**Frontend (Vercel):**
- `NEXT_PUBLIC_GRAPHQL_URL=https://backend.chandlerhardy.com/crooked-finger/graphql`

## Core Features
1. **Pattern Translation**: Convert crochet/knitting notation to readable instructions
2. **AI Assistant**: z.ai proxy (Anthropic-compatible) with image and PDF support
3. **Conversation Management**: Cross-platform chat sync with conversation history
4. **Professional Diagram Generation**: matplotlib-based crochet charts with authentic symbols
5. **Pattern Library**: Browse, save, and manage patterns with image galleries and PDF support
7. **Project Management**: Track projects with images, notes, and chat history
8. **Professional Image Viewer**: Zoom, pan, and navigate project/pattern images
9. **User Authentication**: JWT-based login/register with Argon2 password hashing

## 📁 Project Structure
```
crooked-finger/
├── backend/                              # FastAPI + GraphQL backend
│   ├── app/
│   │   ├── main.py                       # FastAPI entry point
│   │   ├── core/config.py                # Environment configuration (.env loading)
│   │   ├── database/models.py            # User, Project, Chat, Conversation models
│   │   ├── schemas/
│   │   │   ├── queries.py                # GraphQL queries
│   │   │   ├── mutations.py              # GraphQL mutations
│   │   │   └── types.py                  # GraphQL types (Conversation, ChatMessage, etc.)
│   │   ├── services/
│   │   │   ├── ai_service.py             # Multi-model Gemini integration
│   │   │   ├── pattern_service.py        # Pattern parsing & diagram generation
│   │   │   ├── matplotlib_crochet_service.py # Professional chart generation
│   │   │   ├── granny_square_service.py  # Granny square charts (SVG)
│   │   └── utils/auth.py                 # JWT authentication (Argon2 hashing)
│   ├── migrations/
│   │   └── add_conversations_table.py    # Database migration for conversations
│   ├── .env                              # Local development environment variables
│   └── requirements.txt
│
├── frontend/                             # Next.js web application
│   ├── src/
│   │   ├── app/page.tsx                  # Main application
│   │   ├── components/
│   │   │   ├── Navigation.tsx            # Sidebar navigation
│   │   │   ├── ChatInterface.tsx         # AI chat interface
│   │   │   ├── PatternLibrary.tsx        # Pattern browsing & management
│   │   │   ├── ProjectDetailPage.tsx     # Project management with image viewer
│   │   └── lib/
│   │       ├── apollo-client.ts          # GraphQL client
│   │       └── graphql/mutations.ts      # GraphQL mutations
│   ├── .env.local                        # Local frontend environment variables
│   ├── package.json
│   └── next.config.ts
│
├── vercel.json                           # Vercel deployment configuration
├── deploy-backend-to-oci.sh             # Backend deployment script
├── docker-compose.backend.yml           # Production backend containers
├── docker-compose.dev.yml               # Local development database
└── CLAUDE.md                            # This file
```

## 🛠️ Common Commands

### Local Development Database (PostgreSQL in Docker)
```bash
# Start PostgreSQL development database
docker-compose -f docker-compose.dev.yml up -d

# Stop and delete all data (fresh start)
docker-compose -f docker-compose.dev.yml down -v

# View PostgreSQL logs
docker-compose -f docker-compose.dev.yml logs -f postgres-dev

# Connect to PostgreSQL CLI
docker exec -it crooked-finger-dev-db psql -U crochet_dev_user -d crooked_finger_dev
```

### Production Server
```bash
# SSH to server
ssh ubuntu@<your-oci-ip> -i /Users/chandlerhardy/.ssh/ampere.key

# Check backend status
cd crooked-finger && docker-compose -f docker-compose.backend.yml ps

# Restart backend
cd crooked-finger && docker-compose -f docker-compose.backend.yml restart backend

# Deploy backend updates
./deploy-backend-to-oci.sh <your-oci-ip>

# Test GraphQL chatWithAssistant mutation
curl -X POST "https://backend.chandlerhardy.com/crooked-finger/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { chatWithAssistant(message: \"What does sc2tog mean?\") }"}'

# View backend logs
cd crooked-finger && docker-compose -f docker-compose.backend.yml logs backend
```

## 🚨 Common Issues & Solutions

### CORS Issues
**Symptoms**: Browser console shows "blocked by CORS policy"

**Solution**: Update CORS_ORIGINS in `.env` on server:
```bash
ssh ubuntu@<your-oci-ip> -i /Users/chandlerhardy/.ssh/ampere.key
cd crooked-finger
# Edit .env and update CORS_ORIGINS, then:
docker-compose -f docker-compose.backend.yml down
docker-compose -f docker-compose.backend.yml --env-file .env up -d
```

**Note**: The backend config uses `case_sensitive = False` to properly read `CORS_ORIGINS` from environment.

### AI Service Not Working
**Symptoms**: "AI service not configured"

**Root Cause**: `ZAI_API_KEY` must be set in `.env` on the server

**Solution**:
1. Get key from https://z.ai
2. Set in server `.env`: `ZAI_API_KEY=your_key_here`
3. Restart with env file:
   ```bash
   docker-compose -f docker-compose.backend.yml down
   docker-compose -f docker-compose.backend.yml --env-file .env up -d
   ```
4. Verify it's loaded: `docker-compose -f docker-compose.backend.yml exec backend printenv | grep ZAI`

## 🤖 AI Integration
**z.ai Anthropic-compatible proxy** ⭐ **FULLY OPERATIONAL**

### Model
- Routes through z.ai to **GLM-4.7** (translation) and **GLM-4.5-Air** (chat)
- Single `ZAI_API_KEY` env var — no quota tracking, no model selection UI

### Features
- ✅ Expert in both crochet and knitting patterns
- ✅ Multimodal support (images, PDFs)

## 🎨 Professional Diagram Generation
**matplotlib-based crochet charts with authentic symbols** (knitting charts coming soon)

### Current Support: Crochet Charts
- Traditional T-shaped double crochet symbols with crossbars
- Chain oval symbols for corner spaces
- Square-framework construction matching published patterns
- Intelligent pattern detection for diagram requests

### Diagram Services
- `matplotlib_crochet_service.py` - Primary chart generation
- `granny_square_service.py` - SVG granny squares (multiple styles)

## 🖼️ Professional Image Viewer
**Zoom, pan, and navigate project/pattern images** ✅ **COMPLETED**

### Features
- **Mouse Wheel Zoom**: 0.5x to 5x with zoom-to-cursor
- **Click & Drag Panning**: Natural pan at any zoom level
- **Double-Click Zoom**: Quick 1x/2x toggle
- **Reset Zoom Button**: Appears when zoomed
- **Keyboard Navigation**: ESC to close, arrows for gallery
- **Container-Scoped**: Only covers detail view, not entire page

### Technical Implementation
- Native wheel event listeners with `{ passive: false }` (no console warnings)
- Relative positioning for tab-specific overlays
- localStorage persistence with base64 encoding
- Identical implementation in Projects and Pattern Library
- React Hooks for state management

## 📊 Key Differences from CryptAssist
1. **Port**: 8001 instead of 8000
2. **Endpoint**: `/crooked-finger/graphql` instead of `/cryptassist/graphql`
3. **Database**: `crooked_finger_db` instead of `crypto_portfolio`
4. **Focus**: Pattern translation + diagrams instead of portfolio tracking
5. **Python Libraries**: matplotlib, PIL for diagram generation
6. **No Redis needed** (unless caching patterns)

## ✅ Deployment Status
- ✅ Backend structure with FastAPI + GraphQL
- ✅ PostgreSQL database with crochet schema
- ✅ Multi-model Gemini AI integration
- ✅ Professional matplotlib diagram generation
- ✅ Pattern library with image management
- ✅ Professional image viewer with zoom/pan
- ✅ Deployed to OCI with port 8001
- ✅ Frontend development complete
- ✅ Apollo GraphQL client integration
- ✅ AI usage tracking dashboard
- ✅ **HTTPS Production Deployment** (nginx + Let's Encrypt SSL)
- ✅ **Production URLs**: crookedfinger.chandlerhardy.com + backend.chandlerhardy.com
- ✅ **CORS Configuration**: Fixed case-sensitive env var issue
- ✅ **Hydration Fix**: Countdown timer SSR/client mismatch resolved
- ✅ **Conversation Backend**: Database schema, GraphQL API, cross-platform sync (Oct 5, 2025)
- ✅ **Docker Healthcheck**: Fixed from curl to Python urllib (Oct 5, 2025)

## 📱 iOS App Development
**Status**: ✅ **FEATURE PARITY WITH WEB APP**

### Key Implementation Notes
- **SwiftUI** app with tab navigation (Chat, Projects, Patterns, Settings)
- **Custom GraphQL Client**: URLSession-based (no Apollo codegen needed)
- **Authentication**: JWT with Argon2 password hashing, token storage in UserDefaults
- **Cross-Platform Sync**: Conversations and messages sync with backend PostgreSQL
- **Pattern/Project Distinction**: Filtered by `notes` field (null = pattern template, not null = active project)
- **iOS Repository**: `/Users/chandlerhardy/repos/crooked-finger-ios/`

### Future iOS Enhancements
- Migrate token storage from UserDefaults to Keychain
- Add biometric authentication (Face ID/Touch ID)
- Implement JWT token refresh mechanism

## 🔄 Feature Parity Tracker (iOS ↔ Web)

### ✅ Core Features (Both Platforms)
- Pattern/Project Management, AI Chat, Conversation Management, Authentication
- Multimodal AI (images in chat), GraphQL backend integration, Error handling, Empty states

### Platform-Specific Features
**Web Only**: Diagram generation, Zoom/pan image viewer
**iOS Only**: Pull-to-refresh, Camera integration, Biometric auth (Face ID/Touch ID)

## 🚧 Remaining Tasks
1. **Image Viewer on iOS**: Professional zoom/pan like web
2. **Pattern Sharing**: Enable pattern sharing between users (both platforms)
3. **Advanced Diagram Types**: Beyond granny squares (amigurumi, garments, knitting charts)

## 🔄 Development Workflow
1. **Make changes** locally in `frontend/` or `backend/` directories
2. **Test locally**:
   - Frontend: `cd frontend && npm run dev` (runs on http://localhost:3000)
   - Backend: `cd backend && uvicorn app.main:app --reload --port 8001` (runs on http://localhost:8001)
3. **Build test**: `cd frontend && npm run build` to check for TypeScript errors
4. **Commit & push** to `main` branch
5. **Frontend auto-deploys** via Vercel (triggered by push to `main`)
6. **Backend deploy**: Run `./deploy-backend-to-oci.sh <your-oci-ip>`

## 🏗️ Project Structure Notes
- **Monorepo-style**: Frontend and backend are separate subdirectories
- **Independent deployments**: Frontend (Vercel) and backend (OCI) deploy separately
- **Shared API**: Both web and iOS (future) will use the same GraphQL backend
- **Git branch**: `main` is the production branch (Vercel deploys from `main`)
- **Environment files**:
  - `backend/.env` - Local backend config (not committed)
  - `frontend/.env.local` - Local frontend config (not committed)
  - Production env vars set in Vercel dashboard and OCI server

## 🔒 SSL/HTTPS Configuration
**Status**: ✅ **FULLY OPERATIONAL**

### Nginx Reverse Proxy
- **Server**: backend.chandlerhardy.com
- **SSL Certificate**: Let's Encrypt (auto-renewed)
- **Configuration**: `/etc/nginx/sites-available/backend.chandlerhardy.com`

### Path Routing
Both projects share the same nginx server with different paths:
- **CryptAssist**: `https://backend.chandlerhardy.com/cryptassist/` → localhost:8000
- **Crooked Finger**: `https://backend.chandlerhardy.com/crooked-finger/` → localhost:8001

### Security Headers
- HSTS enabled (max-age: 31536000)
- X-Frame-Options: SAMEORIGIN
- X-Content-Type-Options: nosniff
- TLS 1.2/1.3 only

## 📝 Recent Major Updates
- **April 2026**: Migrated AI cascade to z.ai Anthropic-compatible proxy; dropped Gemini + OpenRouter
- **April 2026**: Removed YouTube tab (RapidAPI ToS risk); dead backend services + UI components purged
- **October 2025**: Knitting expertise added to all AI system prompts alongside crochet
- **October 2025**: Web app reached feature parity with iOS (authentication, conversations, multimodal AI)
- **October 2025**: PDF support with inline rendering and caching

---
*Last Updated: April 22, 2026*
