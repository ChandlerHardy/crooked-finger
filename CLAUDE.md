# Claude Code Project Information

## Project Overview
Crooked Finger - A crochet pattern assistant with AI-powered pattern translation and diagram generation.

## Tech Stack
- **Frontend**: Next.js 15 + TypeScript, Tailwind CSS, Apollo GraphQL
- **Backend**: FastAPI + Strawberry GraphQL, PostgreSQL
- **AI**: Google Gemini 2.5 Flash via Google AI Studio ⭐ **UPDATED**
- **Diagram Generation**: Professional matplotlib charts + traditional SVG generators
- **Deployment**: Vercel (frontend) + Oracle Cloud Infrastructure (backend)

## 🖥️ Server Access
**OCI Server:**
- **IP**: `150.136.38.166`
- **SSH**: `ssh ubuntu@150.136.38.166 -i /Users/chandlerhardy/.ssh/ampere.key`
- **Location**: `/home/ubuntu/crooked-finger/` (TBD)

## Port Allocation
**CryptAssist currently uses:**
- Port 8000: Backend API
- Port 5432: PostgreSQL (internal Docker network)
- Port 6379: Redis (internal Docker network)

**Crooked-Finger will use:**
- Port 8001: Backend API ⭐ **NEW PORT FOR THIS PROJECT**
- Port 5433: PostgreSQL (internal Docker network mapping)
- Port 6380: Redis (internal Docker network mapping, if needed)

## 🚀 Live Production URLs
- **Main App**: TBD (likely crooked-finger.chandlerhardy.com)
- **Backend API**: http://150.136.38.166:8001
- **GraphQL**: http://150.136.38.166:8001/crooked-finger/graphql
- **Health Check**: http://150.136.38.166:8001/crooked-finger/health

## ⚙️ Key Environment Variables
**Backend (.env on OCI server):**
- `GEMINI_API_KEY=***` (Google AI Studio API key for Gemini 2.5 Flash)
- `CORS_ORIGINS=https://crooked-finger-app.vercel.app,https://backend.chandlerhardy.com`
- `ADMIN_SECRET=change-this-in-production`
- `DATABASE_URL=postgresql://crochet_user:crochet_password@postgres:5432/crooked_finger_db`

**Frontend (.env file created):**
- `NEXT_PUBLIC_GRAPHQL_URL=http://150.136.38.166:8001/crooked-finger/graphql`
- `NEXT_PUBLIC_API_URL=http://localhost:3000`
- `NEXT_PUBLIC_BACKEND_URL=http://150.136.38.166:8001`

**Frontend (Vercel deployment):**
- `NEXT_PUBLIC_GRAPHQL_URL=https://backend.chandlerhardy.com:8001/crooked-finger/graphql`

## Core Features
1. **Pattern Translation**: Convert crochet notation to readable instructions
2. **AI Assistant**: Chat interface for pattern clarification
3. **Professional Diagram Generation**: ✅ **ENHANCED** - Professional crochet charts with matplotlib
   - Traditional granny square charts with proper corner construction
   - Authentic crochet symbols (double crochet with crossbars, chain ovals)
   - Square-framework based granny squares matching published patterns
   - Intelligent pattern detection for diagram requests
4. **Project Management**: Save and track crochet projects
5. **Chat History**: Store conversations for reference

## 📁 Essential Architecture Files (from CryptAssist)
Based on the architecture-examples review, these are the core files needed:

### Deployment & Infrastructure
- `deploy-backend-to-oci.sh` - Modified for port 8001 and crooked-finger paths
- `docker-compose.backend-postgres.yml` - Updated for new ports and database
- `backend/Dockerfile` - Python container setup

### Backend Core Structure
```
backend/
├── app/
│   ├── main.py                 # FastAPI entry point
│   ├── core/
│   │   └── config.py          # Environment configuration
│   ├── database/
│   │   └── models.py          # User, Project, Chat models
│   ├── schemas/
│   │   ├── queries.py         # GraphQL queries
│   │   └── mutations.py       # GraphQL mutations
│   ├── services/
│   │   ├── ai_service.py                    # AI integration (Llama/Claude)
│   │   ├── pattern_service.py               # Pattern parsing & diagram generation
│   │   ├── matplotlib_crochet_service.py    # ✅ ENHANCED Professional chart generation
│   │   ├── granny_square_service.py         # Specialized granny square charts (SVG)
│   │   ├── flowing_granny_service.py        # Flowing granny square variants
│   │   └── rag_service.py                   # Crochet chart knowledge enhancement
│   ├── utils/
│   │   └── auth.py            # JWT authentication
│   └── requirements.txt
```

### Database Schema (Planned)
- **User**: id, email, hashed_password, is_active, is_admin, created_at, updated_at
- **CrochetProject**: id, name, pattern_text, translated_text, user_id, created_at, updated_at
- **ChatMessage**: id, project_id, user_id, message, response, timestamp
- **ProjectDiagram**: id, project_id, diagram_data, diagram_type, created_at

## 🔄 Development Workflow (Same as CryptAssist)
1. **Make changes** locally in frontend/ or backend/
2. **Test locally**: `npm run dev` (frontend) or `uvicorn app.main:app --reload` (backend)
3. **Build test**: `npm run build` to check for TypeScript errors
4. **Commit & push** to main branch
5. **Frontend auto-deploys** via Vercel
6. **Backend deploy**: Run `./deploy/deploy-backend-to-oci.sh 150.136.38.166`

## 🛠️ Common Commands
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
curl -X POST "http://150.136.38.166:8001/crooked-finger/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { chatWithAssistant(message: \"What does sc2tog mean?\") }"}'

# Test enhanced chat with diagram generation
curl -X POST "http://150.136.38.166:8001/crooked-finger/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { chatWithAssistantEnhanced(message: \"Can you show me a granny square diagram?\") { message diagramSvg hasPattern } }"}'

# Test health check
curl http://150.136.38.166:8001/crooked-finger/health

# View backend logs
cd crooked-finger && docker-compose -f docker-compose.backend.yml logs backend
```

## 🚨 Common Issues & Solutions

### CORS Issues (Frontend can't connect to backend)
**Symptoms**: Browser console shows "blocked by CORS policy" or "No 'Access-Control-Allow-Origin' header"

**Solution**: Update CORS_ORIGINS in `.env` file on server:
```bash
# SSH to server and edit .env
ssh ubuntu@150.136.38.166 -i /Users/chandlerhardy/.ssh/ampere.key
cd crooked-finger
# Add your development URL to CORS_ORIGINS:
CORS_ORIGINS=https://crooked-finger-app.vercel.app,https://backend.chandlerhardy.com,http://localhost:3000,http://localhost:3001

# Restart to apply changes
docker-compose -f docker-compose.backend.yml down && docker-compose -f docker-compose.backend.yml up -d
```

### AI Service Not Working
**Symptoms**: "AI service not configured" or Gemini API errors

**Check**:
1. GEMINI_API_KEY is set in `.env` (get from https://aistudio.google.com/apikey)
2. API key is valid and has quota remaining
3. Test directly: `docker-compose exec backend env | grep GEMINI_API_KEY`

**Fix**:
```bash
# SSH to server and set API key
ssh ubuntu@150.136.38.166 -i /Users/chandlerhardy/.ssh/ampere.key
cd crooked-finger
echo "GEMINI_API_KEY=your_actual_key_here" >> .env
docker-compose -f docker-compose.backend.yml restart backend
```

## 🎨 Enhanced Diagram Generation System (September 2024)

### Professional Crochet Chart Features
**Matplotlib-Based Generation**: Advanced chart creation using Python matplotlib with professional crochet symbols

**Key Services**:
- `matplotlib_crochet_service.py` - **Primary service** for traditional granny square charts
- `granny_square_service.py` - Alternative SVG-based granny charts
- `flowing_granny_service.py` - Flowing/connected granny square variants
- `rag_service.py` - Crochet chart knowledge enhancement

### Traditional Granny Square Charts
**Authentic Symbol Set**:
- **Double Crochet (dc)**: Proper T-shaped symbols with crossbars (one at end, one at middle)
- **Chain (ch)**: Traditional oval symbols for chain spaces
- **Corner Chains (ch-2)**: Two angled chain ovals forming proper right angles

**Square-Framework Construction**:
- **Round 1**: Magic ring with 12 dc stitches in center
- **Round 2**: Corner groups at cardinal positions with ch-2 corners
  - North (0, 1.4), East (1.4, 0), South (0, -1.4), West (-1.4, 0)
  - Fixed corner positioning to form proper right angles at all 4 corners
- **Round 3**: Expanded corner groups with side connections

**Professional Features**:
- Guideline squares for visual structure reference
- Traditional crochet chart color scheme (black symbols, gray guidelines)
- Proper stitch orientation pointing toward center
- Authentic corner construction matching published patterns

### Intelligent Pattern Detection
**Enhanced Chat Integration**:
- Detects diagram requests in user messages ("show me", "diagram", "visual")
- Identifies granny square patterns vs. general crochet patterns
- Routes to appropriate generation service based on pattern type
- Only generates diagrams when explicitly requested (optimizes token usage)

**Smart Routing**:
```python
# Pattern detection examples
"Can you show me a granny square diagram?" → Traditional granny square chart
"Create a visual for this pattern: Round 1: ch 4..." → General pattern chart
"What is a granny square?" → Text response only (no diagram)
```

### Recent Improvements (Latest Session)
1. **Fixed Round 2 Corner Positioning**: All 4 corners now have properly positioned ch-2 chains
2. **Enhanced Corner Angles**: Ch-2 corners form authentic right angles at square corners
3. **Improved Symbol Quality**: Double crochet symbols with proper crossbar placement
4. **Pattern Detection Fix**: Correctly routes general granny square requests to traditional chart generation

## 🤖 AI Integration - Google AI Studio (Gemini)
**Current Architecture: Google Gemini 2.5 Flash** ⭐ **ACTIVE**
- ✅ Fast and efficient for crochet pattern understanding
- ✅ Excellent creative capabilities for pattern explanations
- ✅ Reliable API with good uptime
- ✅ Pay-per-use with generous free tier
- ✅ No token limitations like GitHub models
- 🔑 API Key: Get free key from [Google AI Studio](https://aistudio.google.com/apikey)

**Setup Instructions:**
1. Get API key from https://aistudio.google.com/apikey
2. Set `GEMINI_API_KEY=your_key_here` in server `.env`
3. Restart backend: `docker-compose -f docker-compose.backend.yml restart backend`

**Previous Options (Deprecated):**
- ❌ GitHub Llama 3.1 8B (migrated away from)
- ❌ OpenAI GPT (never implemented)
- ❌ Local Llama (too resource intensive)

## 📊 Key Differences from CryptAssist
1. **Port**: 8001 instead of 8000
2. **Endpoint**: `/crooked-finger/graphql` instead of `/cryptassist/graphql`
3. **Database**: `crooked_finger_db` instead of `crypto_portfolio`
4. **Focus**: Pattern translation + diagrams instead of portfolio tracking
5. **Python Libraries**: matplotlib, PIL for diagram generation
6. **No Redis needed** (unless caching patterns)

## ✅ Deployment Status (Completed)
1. ✅ Review architecture examples
2. ✅ Set up backend structure with FastAPI + GraphQL
3. ✅ Configure PostgreSQL database with crochet schema
4. ✅ Integrate AI service for pattern translation
5. ✅ Add diagram generation capabilities
6. ✅ Deploy to OCI with port 8001
7. ✅ Configure OCI Security Groups for port access
8. ✅ **Frontend Development Complete**
9. ✅ **Professional Crochet Chart Generation ENHANCED** (September 2024)
   - Matplotlib-based granny square charts with traditional symbols
   - Fixed Round 2 corner construction with proper ch-2 positioning
   - Authentic double crochet symbols with crossbars
   - Square-framework construction matching published patterns
10. ✅ **AI Architecture Migration to Google Gemini** (September 2024)
   - Migrated from GitHub Llama 3.1 8B to Google Gemini 2.5 Flash
   - Implemented google-genai SDK integration
   - Updated environment variables and configuration
   - Deployed with new AI architecture

## 🚀 Backend Successfully Deployed!
- **Status**: ✅ Live and operational
- **Server**: Running on OCI instance 150.136.38.166:8001
- **Database**: PostgreSQL healthy and connected
- **GraphQL**: Fully functional with schema explorer
- **AI Integration**: Ready for GitHub Llama token configuration

## 🎨 Frontend Successfully Developed!
- **Status**: ✅ Complete and running locally
- **Dev Server**: http://localhost:3000
- **Framework**: Next.js 15 + TypeScript + Tailwind CSS
- **Components**: 47 UI components + 5 main app components transferred from Figma
- **Features**: Crochet-themed design, dark/light themes, AI chat interface
- **Ready for**: GraphQL integration with backend

### 🖼️ Frontend Features Implemented
**UI Components (47 total)**
- Complete Radix UI + shadcn component library
- Professional form controls, navigation, cards, dialogs
- Responsive design with mobile-first approach

**Main Application Components (5 total)**
- `Navigation.tsx` - Sidebar with theme toggle
- `HomePage.tsx` - Dashboard with project overview
- `ChatInterface.tsx` - AI assistant chat with auto-scroll
- `ProjectsPage.tsx` - Project management interface
- `PatternLibrary.tsx` - Browse and filter patterns

**🎨 Design System**
- **Light Theme**: Clean cream background (`#fdfcfb`) with warm brown accents (`#A47764`)
- **Dark Theme**: Modern dark gray (`#1a1a1a`) with same brown accents
- **Theme Toggle**: Sun/moon button with smooth transitions
- **Typography**: Geist Sans font with consistent spacing
- **Components**: Rounded corners, subtle shadows, glassmorphism effects

**🔧 Technical Features**
- **Auto-scroll Chat**: Messages automatically scroll into view
- **Theme Persistence**: Light/dark preference saved across sessions
- **TypeScript**: Fully typed components and interfaces
- **Mock Data**: Sample projects and responses for development
- **Responsive**: Works on desktop, tablet, and mobile

## 🚧 Next Steps (Frontend ↔ Backend Integration)
1. **Apollo GraphQL Client Setup**
   - Install and configure Apollo Client
   - Create GraphQL queries and mutations for chat
   - Replace mock data with real API calls

2. **AI Chat Integration**
   - Connect chat interface to backend GraphQL endpoint
   - Implement real-time AI responses via GitHub Llama
   - Add loading states and error handling

3. **User Authentication**
   - Add login/register forms (based on CryptAssist pattern)
   - Implement JWT token management
   - Protect routes and user-specific data

4. **Project Management**
   - Connect project CRUD operations to backend
   - Implement project saving and loading
   - Add pattern storage and retrieval

5. **Production Deployment**
   - Deploy frontend to Vercel
   - Configure production environment variables
   - Test full-stack integration

---
*This file provides essential deployment info condensed from CryptAssist architecture for the Crooked-Finger crochet assistant project.*