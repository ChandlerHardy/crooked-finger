# Crooked Finger Crochet

**AI-powered pattern assistant for crochet and knitting enthusiasts**

🌐 **Live App**: [crookedfinger.chandlerhardy.com](https://crookedfinger.chandlerhardy.com)

---

## The Problem

Crafters face several challenges when working with crochet and knitting patterns:

- **Cryptic Abbreviations**: Patterns use dense abbreviation systems (sc, dc, sl st, k2tog, etc.) that are intimidating for beginners and easy to misinterpret
- **YouTube Tutorials**: Video patterns are time-consuming to follow, requiring constant pausing and rewinding to catch instructions
- **Pattern Organization**: Crafters accumulate patterns from books, websites, and videos with no centralized way to manage them
- **Project Tracking**: Keeping notes on gauge, yarn used, modifications, and progress is often done on paper or scattered across apps
- **Complex Diagrams**: Traditional pattern charts can be hard to read, especially for visual learners who need clearer representations

## The Solution

Crooked Finger transforms the crafting experience by combining AI intelligence with practical project management:

### 🤖 **AI-Powered Pattern Translation**
- Instantly converts cryptic abbreviations into plain English instructions
- Supports both crochet and knitting terminology
- Multimodal AI can analyze pattern images and PDFs directly
- Contextual understanding helps clarify ambiguous instructions

### 📺 **YouTube Transcript Extraction**
- Extract written patterns from video tutorials automatically
- Save transcripts to your pattern library for quick reference
- No more endless pausing and rewinding

### 📊 **Professional Diagram Generation**
- Converts text patterns into visual crochet charts using matplotlib
- Traditional T-shaped symbols matching published patterns
- SVG granny square generators with multiple style options

### 📚 **Pattern Library**
- Centralized storage for all your patterns
- Rich metadata: images, thumbnails, source URLs
- Full-text search across your entire library
- Templates vs. active projects automatically distinguished

### 🧶 **Project Management**
- Track active projects with notes, gauge, yarn details
- Attach multiple project photos with professional zoom/pan viewer
- Integrated AI chat history for each project
- Cross-platform sync between web and iOS (coming soon)

### 🔄 **Smart AI Model Routing**
- Multi-provider system with both free (OpenRouter) and premium (Gemini) models
- Intelligent fallback chain ensures 100% uptime
- Complexity-based routing: simple queries use free models, complex analysis uses premium
- Real-time usage dashboard tracks quota consumption

---

## Tech Stack

### Frontend
- **Next.js 15** with TypeScript and Tailwind CSS
- **Apollo Client** for GraphQL integration
- **Vercel** hosting with automatic deployments

### Backend
- **FastAPI** + **Strawberry GraphQL**
- **PostgreSQL** database
- **Oracle Cloud Infrastructure** (ARM-based compute)
- **nginx** reverse proxy with Let's Encrypt SSL

### AI Integration
- **Google Gemini** (2.5 Pro, Flash, Flash-Lite) for high-quality analysis
- **OpenRouter** (Qwen 3 30B, DeepSeek v3.1) for unlimited free requests
- **RapidAPI** YouTube service for video transcript extraction

### Diagram Generation
- **matplotlib** for professional crochet charts
- **Pillow (PIL)** for image processing
- **SVG** generation for granny squares

---

## Key Features

- ✅ **Pattern Translation**: Convert "sc2tog, ch 3, dc in next 5 sts" into readable instructions
- ✅ **Multimodal AI**: Upload pattern PDFs or images for analysis
- ✅ **YouTube Integration**: Extract patterns from video tutorials
- ✅ **Diagram Generation**: Create visual charts from text patterns
- ✅ **Project Tracking**: Manage active projects with notes and images
- ✅ **Pattern Library**: Centralized storage with search and filtering
- ✅ **Image Viewer**: Professional zoom/pan for project photos
- ✅ **AI Model Selection**: Choose between free and premium AI models
- ✅ **Usage Dashboard**: Track AI quota consumption in real-time
- ✅ **User Authentication**: JWT-based login with Argon2 password hashing
- ✅ **Cross-Platform**: Web app with iOS companion (in development)

---

## Local Development

### Prerequisites
- Node.js 18+ and npm
- Docker and Docker Compose
- Python 3.11+

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

The frontend will run on `http://localhost:3000`

### Backend Setup
```bash
# Start PostgreSQL database
docker-compose -f docker-compose.dev.yml up -d

# Install Python dependencies
cd backend
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run backend server
uvicorn app.main:app --reload --port 8001
```

The backend will run on `http://localhost:8001`

### Environment Variables

**Frontend (.env.local)**:
```
NEXT_PUBLIC_GRAPHQL_URL=http://localhost:8001/crooked-finger/graphql
```

**Backend (.env)**:
```
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql://crochet_dev_user:devpassword@localhost:5433/crooked_finger_dev
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

---

## Deployment

### Frontend (Vercel)
The frontend automatically deploys to Vercel on every push to `main`:
- Production: [crookedfinger.chandlerhardy.com](https://crookedfinger.chandlerhardy.com)

### Backend (Oracle Cloud)
Deploy backend updates to OCI:
```bash
./deploy-backend-to-oci.sh 150.136.38.166
```

Backend endpoints:
- API: `https://backend.chandlerhardy.com/crooked-finger/`
- GraphQL: `https://backend.chandlerhardy.com/crooked-finger/graphql`
- Health: `https://backend.chandlerhardy.com/crooked-finger/health`

---

## Project Structure

```
crooked-finger/
├── frontend/                 # Next.js web application
│   ├── src/
│   │   ├── app/             # Next.js app router
│   │   ├── components/      # React components
│   │   └── lib/             # GraphQL client, utilities
│   └── package.json
│
├── backend/                  # FastAPI + GraphQL API
│   ├── app/
│   │   ├── main.py          # FastAPI entry point
│   │   ├── database/        # SQLAlchemy models
│   │   ├── schemas/         # GraphQL schema
│   │   └── services/        # AI, pattern, YouTube services
│   └── requirements.txt
│
├── docker-compose.dev.yml   # Local PostgreSQL database
├── docker-compose.backend.yml # Production backend containers
└── deploy-backend-to-oci.sh # Deployment script
```

---

## API Examples

### Chat with AI Assistant
```graphql
mutation {
  chatWithAssistant(message: "What does sc2tog mean?") {
    response
    modelUsed
  }
}
```

### Fetch YouTube Transcript
```graphql
mutation {
  fetchYoutubeTranscript(videoUrl: "https://youtube.com/watch?v=VIDEO_ID") {
    success
    transcript
    wordCount
  }
}
```

### Get AI Usage Dashboard
```graphql
query {
  aiUsageDashboard {
    totalRequestsToday
    totalRemaining
    models {
      modelName
      currentUsage
      dailyLimit
      percentageUsed
    }
  }
}
```

---

## Contributing

This is a personal portfolio project, but suggestions and feedback are welcome! Feel free to open an issue or reach out.

---

## License

MIT License - See LICENSE file for details

---

## Contact

**Chandler Hardy**
📧 Email: hardych04@gmail.com
🌐 Portfolio: [chandlerhardy.com](https://chandlerhardy.com)
💼 LinkedIn: [linkedin.com/in/chandler-hardy-80808112b](https://linkedin.com/in/chandler-hardy-80808112b)

---

*Built with ❤️ for the crochet and knitting community*
