# Claude Code Project Information

## Project Overview
Crooked Finger - A crochet pattern assistant with AI-powered pattern translation and diagram generation.

## Tech Stack
- **Frontend**: Next.js 15 + TypeScript, Tailwind CSS, Apollo GraphQL
- **Backend**: FastAPI + Strawberry GraphQL, PostgreSQL
- **AI**: Multi-Model Gemini System (Pro + Flash Preview + Flash + Flash-Lite)
- **Diagram Generation**: Professional matplotlib charts + traditional SVG generators
- **Deployment**: Vercel (frontend) + Oracle Cloud Infrastructure (backend)

## 🖥️ Server Access
**OCI Server:**
- **IP**: `150.136.38.166`
- **SSH**: `ssh ubuntu@150.136.38.166 -i /Users/chandlerhardy/.ssh/ampere.key`
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
- `GEMINI_API_KEY=AIzaSyDlKJxbfq93MThxC_CGUdZChDmaZPZ4vpg` (Google AI Studio API key)
- `CORS_ORIGINS=https://crookedfinger.chandlerhardy.com,https://crooked-finger-app.vercel.app,https://backend.chandlerhardy.com,http://localhost:3000,http://localhost:3001`
- `ADMIN_SECRET=change-this-in-production`
- `DATABASE_URL=postgresql://crochet_user:crochet_password@postgres:5432/crooked_finger_db`

**Frontend (.env.local):**
- `NEXT_PUBLIC_GRAPHQL_URL=http://localhost:8001/crooked-finger/graphql`
- `GEMINI_API_KEY=AIzaSyDlKJxbfq93MThxC_CGUdZChDmaZPZ4vpg`

**Frontend (Vercel):**
- `NEXT_PUBLIC_GRAPHQL_URL=https://backend.chandlerhardy.com/crooked-finger/graphql`

## Core Features
1. **Pattern Translation**: Convert crochet notation to readable instructions
2. **AI Assistant**: Multi-model Gemini chat interface for pattern clarification
3. **Professional Diagram Generation**: matplotlib-based crochet charts with authentic symbols
4. **YouTube Transcript Extraction**: Extract patterns from crochet tutorial videos
5. **Pattern Library**: Browse, save, and manage crochet patterns with image galleries
6. **Project Management**: Track crochet projects with images, notes, and chat history
7. **Professional Image Viewer**: Zoom, pan, and navigate project/pattern images

## 📁 Project Structure
```
crooked-finger/
├── backend/                              # FastAPI + GraphQL backend
│   ├── app/
│   │   ├── main.py                       # FastAPI entry point
│   │   ├── core/config.py                # Environment configuration (.env loading)
│   │   ├── database/models.py            # User, Project, Chat models
│   │   ├── schemas/
│   │   │   ├── queries.py                # GraphQL queries
│   │   │   └── mutations.py              # GraphQL mutations
│   │   ├── services/
│   │   │   ├── ai_service.py             # Multi-model Gemini integration
│   │   │   ├── pattern_service.py        # Pattern parsing & diagram generation
│   │   │   ├── matplotlib_crochet_service.py # Professional chart generation
│   │   │   ├── granny_square_service.py  # Granny square charts (SVG)
│   │   │   └── youtube_service.py        # YouTube transcript extraction
│   │   └── utils/auth.py                 # JWT authentication
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
│   │   │   └── YouTubeTest.tsx           # YouTube transcript testing
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
ssh ubuntu@150.136.38.166 -i /Users/chandlerhardy/.ssh/ampere.key

# Check backend status
cd crooked-finger && docker-compose -f docker-compose.backend.yml ps

# Restart backend
cd crooked-finger && docker-compose -f docker-compose.backend.yml restart backend

# Deploy backend updates
./deploy-backend-to-oci.sh 150.136.38.166

# Test GraphQL chatWithAssistant mutation
curl -X POST "https://backend.chandlerhardy.com/crooked-finger/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { chatWithAssistant(message: \"What does sc2tog mean?\") }"}'

# Test AI usage dashboard
curl -X POST "https://backend.chandlerhardy.com/crooked-finger/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query":"query { aiUsageDashboard { totalRequestsToday totalRemaining models { modelName currentUsage dailyLimit remaining percentageUsed } } }"}'

# Test YouTube transcript fetching
curl -X POST "https://backend.chandlerhardy.com/crooked-finger/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { fetchYoutubeTranscript(videoUrl: \"dQw4w9WgXcQ\") { success videoId wordCount language error transcript } }"}'

# View backend logs
cd crooked-finger && docker-compose -f docker-compose.backend.yml logs backend
```

## 🚨 Common Issues & Solutions

### CORS Issues
**Symptoms**: Browser console shows "blocked by CORS policy"

**Solution**: Update CORS_ORIGINS in `.env` on server:
```bash
ssh ubuntu@150.136.38.166 -i /Users/chandlerhardy/.ssh/ampere.key
cd crooked-finger
# Edit .env and update CORS_ORIGINS, then:
docker-compose -f docker-compose.backend.yml down
docker-compose -f docker-compose.backend.yml --env-file .env up -d
```

**Note**: The backend config uses `case_sensitive = False` to properly read `CORS_ORIGINS` from environment.

### AI Service Not Working
**Symptoms**: "AI service not configured" or Gemini API errors

**Root Cause**: GEMINI_API_KEY must be explicitly added to docker-compose.backend.yml environment section

**Solution**:
1. Get API key from https://aistudio.google.com/apikey
2. Set in server `.env`: `GEMINI_API_KEY=your_key_here`
3. **IMPORTANT**: Add to docker-compose.backend.yml under `backend.environment`:
   ```yaml
   - GEMINI_API_KEY=${GEMINI_API_KEY:-}
   ```
4. Restart with env file:
   ```bash
   docker-compose -f docker-compose.backend.yml down
   docker-compose -f docker-compose.backend.yml --env-file .env up -d
   ```
5. Verify it's loaded: `docker-compose -f docker-compose.backend.yml exec backend printenv | grep GEMINI`

**Note**: Simply having the key in `.env` is NOT enough - it must be explicitly passed in docker-compose.yml

## 🤖 AI Integration - Google AI Studio (Gemini)
**Multi-Model Smart Routing System** ⭐ **FULLY OPERATIONAL**

### 4-Tier Model System
- **Gemini 2.5 Pro**: 100 requests/day - Premium quality for complex pattern analysis
- **Gemini 2.5 Flash Preview**: 250 requests/day - Latest features and fast performance
- **Gemini 2.5 Flash**: 400 requests/day - Balanced speed and quality
- **Gemini 2.5 Flash-Lite**: 1,000 requests/day - High-speed for simple queries
- **Total Daily Quota**: 1,600 requests (5x increase from single model)

### Features
- ✅ Smart model selection based on query complexity
- ✅ Real-time usage tracking with dashboard
- ✅ Character and token count tracking
- ✅ Manual usage reset capability
- ✅ Auto-refreshing frontend dashboard with progress bars

## 🎨 Professional Diagram Generation
**matplotlib-based crochet charts with authentic symbols**

### Granny Square Charts
- Traditional T-shaped double crochet symbols with crossbars
- Chain oval symbols for corner spaces
- Square-framework construction matching published patterns
- Proper corner positioning (fixed Round 2 ch-2 chains)
- Intelligent pattern detection for diagram requests

### Diagram Services
- `matplotlib_crochet_service.py` - Primary chart generation
- `granny_square_service.py` - SVG granny squares
- `flowing_granny_service.py` - Flowing granny variants
- `rag_service.py` - Chart knowledge enhancement

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

## 📺 YouTube Transcript Extraction
**Extract patterns from crochet tutorial videos** ✅ **OPERATIONAL**

### Features
- Fetch transcripts from YouTube videos (youtube-transcript-api v1.2.2)
- Support for auto-generated and manual captions
- Automatic thumbnail fetching (maxresdefault + hqdefault fallback)
- Rate limiting protection (2-second delays)
- Multiple URL formats: youtube.com/watch?v=, youtu.be/, video IDs

### Pattern Library Integration
- YouTube patterns save to library with thumbnails
- localStorage persistence (PostgreSQL integration pending)
- Pattern detail pages with full metadata
- Multi-image galleries with lightbox viewer

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
- ✅ YouTube transcript extraction
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

## 🚧 Remaining Tasks
1. **PostgreSQL Integration for Pattern Library**: Migrate from localStorage to database
2. **User Authentication**: Add login/register with JWT tokens
3. **Pattern Sharing**: Enable pattern sharing between users
4. **Advanced Diagram Types**: Beyond granny squares (amigurumi, garments)

## 🔄 Development Workflow
1. **Make changes** locally in `frontend/` or `backend/` directories
2. **Test locally**:
   - Frontend: `cd frontend && npm run dev` (runs on http://localhost:3000)
   - Backend: `cd backend && uvicorn app.main:app --reload --port 8001` (runs on http://localhost:8001)
3. **Build test**: `cd frontend && npm run build` to check for TypeScript errors
4. **Commit & push** to `main` branch
5. **Frontend auto-deploys** via Vercel (triggered by push to `main`)
6. **Backend deploy**: Run `./deploy-backend-to-oci.sh 150.136.38.166`

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
- **Server**: backend.chandlerhardy.com (150.136.38.166)
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

---
*Last Updated: October 2025 - HTTPS Production Deployment*
