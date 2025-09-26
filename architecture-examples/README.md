# Architecture Examples

This folder contains the essential files to replicate the crypto-assistant architecture in another project.

## Architecture Overview
- **Frontend**: Next.js 15 + TypeScript on Vercel
- **Backend**: FastAPI + Strawberry GraphQL on Oracle Cloud Infrastructure
- **Database**: PostgreSQL with Docker
- **Authentication**: JWT tokens with bcrypt password hashing
- **Deployment**: Backend-only OCI deployment + Vercel frontend auto-deployment

## Essential Files Included

### Core Documentation
- `CLAUDE.md` - Complete architecture documentation and setup guide
- `README.md` - Project overview

### Deployment & Infrastructure
- `deploy-backend-to-oci.sh` - Backend deployment script for OCI
- `docker-compose.backend-postgres.yml` - Production backend configuration
- `backend/Dockerfile` - Backend container setup

### Backend Core
- `backend/app/main.py` - FastAPI application entry point
- `backend/app/core/config.py` - Environment configuration
- `backend/app/database/models.py` - Database models (User, Portfolio, etc.)
- `backend/app/schemas/queries.py` - GraphQL queries
- `backend/app/schemas/mutations.py` - GraphQL mutations
- `backend/app/utils/auth.py` - JWT authentication utilities
- `backend/requirements.txt` - Python dependencies

### Frontend Core
- `frontend/package.json` - Dependencies and scripts
- `frontend/next.config.js` - Next.js configuration
- `frontend/src/lib/apollo-client.ts` - GraphQL client setup

## Key Architecture Patterns

1. **Split Frontend/Backend Deployment**: Frontend on Vercel, backend on OCI
2. **GraphQL with Authentication**: JWT-based auth with role-based access control
3. **PostgreSQL Persistence**: Docker volumes for data persistence across deployments
4. **Environment-based Configuration**: Separate configs for development/production
5. **Containerized Backend**: Docker deployment with health checks

## Getting Started

1. **Review CLAUDE.md** for complete setup instructions
2. **Copy deployment script** and update IP addresses/paths
3. **Configure environment variables** as documented
4. **Deploy backend** using the OCI script
5. **Deploy frontend** to Vercel with environment variables

## Project Structure

```
crypto-assistant/
├── frontend/                 # Next.js React application
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   ├── components/      # Reusable UI components
│   │   ├── lib/             # Apollo Client setup
│   │   └── types/           # TypeScript interfaces
│   └── package.json
│
├── backend/                  # FastAPI GraphQL API
│   ├── app/
│   │   ├── api/             # REST endpoints (if needed)
│   │   ├── core/            # Configuration
│   │   ├── models/          # Database models
│   │   ├── schemas/         # GraphQL schemas
│   │   ├── services/        # Business logic
│   │   └── utils/           # Utility functions
│   └── requirements.txt
│
└── README.md
```

## Development

### Environment Variables

Backend (`.env`):
```bash
DATABASE_URL=postgresql://user:pass@localhost/crypto_db
REDIS_URL=redis://localhost:6379
COINGECKO_API_KEY=your-api-key-here
GITHUB_TOKEN=your-github-personal-access-token
SECRET_KEY=your-secret-key
```

Frontend (`.env.local`):
```bash
NEXT_PUBLIC_GRAPHQL_URL=http://localhost:8000/cryptassist/graphql
```

### Available Scripts

**Frontend:**
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run lint` - Run ESLint

**Backend:**
- `uvicorn app.main:app --reload` - Start development server
- `pytest` - Run tests
- `alembic upgrade head` - Run database migrations

## Deployment

### Production Status ✅

**Current Live Deployment (as of August 2025):**
- **Frontend**: ✅ https://cryptassist.chandlerhardy.com (Vercel)
- **Portfolio**: ✅ https://chandlerhardy.com (Vercel) 
- **Backend API**: ✅ https://backend.chandlerhardy.com (OCI - 150.136.38.166)
- **GraphQL Endpoint**: ✅ https://backend.chandlerhardy.com/cryptassist/graphql
- **AI Chat**: ✅ Active with GitHub Llama integration
- **Database**: ✅ PostgreSQL in Docker on OCI
- **SSL/HTTPS**: ✅ Let's Encrypt certificates

### Key Deployment Information

**OCI Server:**
- **IP**: `150.136.38.166`
- **SSH**: `ssh ubuntu@150.136.38.166 -i /Users/chandlerhardy/.ssh/ampere.key`
- **Location**: `/home/ubuntu/crypto-assistant/`
- **Docker Compose**: `docker-compose.backend.yml`

**Environment Variables (Production):**
```bash
# On OCI server in ~/crypto-assistant/.env
CORS_ORIGINS=http://localhost:3000,https://cryptassist.chandlerhardy.com,https://backend.chandlerhardy.com
GITHUB_TOKEN=ghp_*** (configured)
```

**Vercel Environment:**
```bash
NEXT_PUBLIC_GRAPHQL_URL=https://backend.chandlerhardy.com/cryptassist/graphql
```

### Architecture Overview
```
┌─────────────────┐    HTTPS    ┌─────────────────┐    HTTPS    ┌─────────────────┐
│                 │ ──────────► │                 │ ─────────► │                 │
│  User Browser   │             │  Vercel (CDN)   │            │ OCI + nginx +   │
│ cryptassist.    │ ◄────────── │  Custom Domains │ ◄───────── │ Let's Encrypt   │
│ chandlerhardy.  │             │                 │            │ 150.136.38.166  │
│ com             │             │                 │            │                 │
└─────────────────┘             └─────────────────┘            └─────────────────┘
```

### Deploy to OCI
```bash
# Deploy backend to Oracle Cloud
./deploy/deploy-backend-to-oci.sh 150.136.38.166

# Set up SSL certificates (if needed)
./deploy/setup-ssl.sh 150.136.38.166 backend.chandlerhardy.com
```

### Maintenance Commands
```bash
# SSH to server
ssh ubuntu@150.136.38.166 -i /Users/chandlerhardy/.ssh/ampere.key

# Check backend status
cd crypto-assistant && docker-compose -f docker-compose.backend.yml ps

# View backend logs
cd crypto-assistant && docker-compose -f docker-compose.backend.yml logs backend

# Restart backend
cd crypto-assistant && docker-compose -f docker-compose.backend.yml restart backend

# Update backend (redeploy)
./deploy/deploy-backend-to-oci.sh 150.136.38.166
```

## API Examples

### GraphQL Queries

```graphql
# Get cryptocurrency list
query GetCryptocurrencies {
  cryptocurrencies(limit: 50) {
    id
    symbol
    name
    current_price
    price_change_percentage_24h
  }
}

# Get portfolio data
query GetPortfolios {
  portfolios {
    id
    name
    totalValue
    totalProfitLoss
    totalRealizedProfitLoss
    totalCostBasis
    assets {
      symbol
      amount
      currentPrice
      totalValue
      profitLoss
      transactions {
        transactionType
        amount
        pricePerUnit
        realizedProfitLoss
        timestamp
      }
    }
  }
}

# Get portfolio transaction history
query GetPortfolioTransactions($portfolioId: String!) {
  portfolioTransactions(portfolioId: $portfolioId) {
    id
    transactionType
    amount
    pricePerUnit
    totalValue
    realizedProfitLoss
    timestamp
    symbol
    name
  }
}
```

### AI Chat Integration

The application includes an intelligent AI assistant powered by GitHub's Llama 3.1 8B model:

```graphql
# Chat with AI assistant
mutation ChatWithAssistant($message: String!, $context: String) {
  chatWithAssistant(message: $message, context: $context)
}
```

**AI Features:**
- 🤖 **Real-time Market Analysis**: Current crypto prices and trends
- 📊 **Portfolio Insights**: Personalized advice based on user holdings
- 💡 **Investment Guidance**: Educational market analysis and strategies
- 🔄 **Context Awareness**: AI receives user portfolio data for personalized responses
- 🎨 **Glassmorphism UI**: Beautiful floating chat widget with blur effects

**AI Configuration:**
- **Model**: GitHub Llama 3.1 8B Instruct
- **Endpoint**: https://models.github.ai/inference
- **Authentication**: GitHub Personal Access Token required
- **Context**: Portfolio data automatically included for personalized advice
- **Rate Limiting**: Managed by GitHub AI API

### Real-time Subscriptions

```graphql
# Subscribe to price updates
subscription PriceUpdates($cryptoIds: [String!]!) {
  priceUpdates(cryptoIds: $cryptoIds) {
    timestamp
    price
  }
}
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.