# Claude Code Project Information

## Project Overview
Crooked Finger - A crochet pattern assistant with AI-powered pattern translation and diagram generation.

## Tech Stack
- **Frontend**: Next.js 15 + TypeScript, Tailwind CSS, Apollo GraphQL
- **Backend**: FastAPI + Strawberry GraphQL, PostgreSQL
- **AI**: GitHub Llama 3.1 8B model integration (or Claude API as alternative)
- **Diagram Generation**: Python libraries (matplotlib, PIL, SVG)
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
- `GITHUB_TOKEN=ghp_***` (for AI chat - configured)
- `CORS_ORIGINS=https://crooked-finger-app.vercel.app,https://backend.chandlerhardy.com`
- `ADMIN_SECRET=change-this-in-production`
- `DATABASE_URL=postgresql://crochet_user:crochet_password@postgres:5432/crooked_finger_db`

**Frontend (.env file created):**
- `GITHUB_TOKEN=ghp_***` (configured for AI integration)
- `NEXT_PUBLIC_GRAPHQL_URL=http://150.136.38.166:8001/crooked-finger/graphql`
- `NEXT_PUBLIC_API_URL=http://localhost:3000`
- `NEXT_PUBLIC_BACKEND_URL=http://150.136.38.166:8001`

**Frontend (Vercel deployment):**
- `NEXT_PUBLIC_GRAPHQL_URL=https://backend.chandlerhardy.com:8001/crooked-finger/graphql`

## Core Features
1. **Pattern Translation**: Convert crochet notation to readable instructions
2. **AI Assistant**: Chat interface for pattern clarification
3. **Diagram Generation**: Visual crochet diagrams using Python libraries
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
│   │   ├── ai_service.py      # AI integration (Llama/Claude)
│   │   └── pattern_service.py # Pattern parsing & diagram generation
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

# Test GraphQL hello query
curl -X POST "http://150.136.38.166:8001/crooked-finger/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ hello }"}'

# Test health check
curl http://150.136.38.166:8001/crooked-finger/health

# View backend logs
cd crooked-finger && docker-compose -f docker-compose.backend.yml logs backend
```

## 🤖 AI Integration Options
**Option 1: GitHub Llama (Existing Setup)**
- ✅ Already working in CryptAssist
- ✅ Free after setup
- ✅ Good for crochet pattern understanding

**Option 2: Claude API**
- ✅ Excellent for creative tasks and pattern explanation
- ✅ Better at contextual understanding
- 💰 Pay-per-use

**Option 3: Local Llama**
- ✅ Complete privacy
- ❌ Resource intensive on OCI

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