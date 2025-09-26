# Claude Code Project Information

## Project Overview
Crypto Portfolio Analyzer - A real-time cryptocurrency portfolio tracking and analysis application with AI-powered investment advice.

## Tech Stack
- **Frontend**: Next.js 15 + TypeScript, Tailwind CSS, Apollo GraphQL
- **Charting**: Recharts (current), Chart.js, TradingView widgets (roadmap)
- **Backend**: FastAPI + Strawberry GraphQL, PostgreSQL
- **AI**: GitHub Llama 3.1 8B model integration
- **Deployment**: Vercel (frontend) + Oracle Cloud Infrastructure (backend)

## 🚀 Live Production URLs
- **Main App**: https://cryptassist.chandlerhardy.com
- **Portfolio**: https://chandlerhardy.com
- **Backend API**: https://backend.chandlerhardy.com
- **GraphQL**: https://backend.chandlerhardy.com/cryptassist/graphql
- **Health Check**: https://backend.chandlerhardy.com/cryptassist/health

## 🖥️ Server Access
**OCI Server:**
- **IP**: `150.136.38.166`
- **SSH**: `ssh ubuntu@150.136.38.166 -i /Users/chandlerhardy/.ssh/ampere.key`
- **Location**: `/home/ubuntu/crypto-assistant/`

## ⚙️ Key Environment Variables
**Backend (.env on OCI server):**
- `GITHUB_TOKEN=ghp_***` (for AI chat)
- `CORS_ORIGINS=https://cryptassist.chandlerhardy.com,https://backend.chandlerhardy.com`
- `ADMIN_SECRET=change-this-in-production` (for creating admin users)

**Frontend (Vercel):**
- `NEXT_PUBLIC_GRAPHQL_URL=https://backend.chandlerhardy.com/cryptassist/graphql`

## 🔑 Admin Access
**For GraphQL Playground & Admin Operations:**
- **Access**: Admin-only GraphQL playground access at `/cryptassist/graphql`
- **Usage**: Login via GraphQL with admin credentials, use returned JWT token for playground access
- **Credentials**: Available in secure environment (not stored in public repository)

## 🛠️ Common Commands
```bash
# SSH to server
ssh ubuntu@150.136.38.166 -i /Users/chandlerhardy/.ssh/ampere.key

# Check backend status
cd crypto-assistant && docker-compose -f docker-compose.backend.yml ps

# Restart backend
cd crypto-assistant && docker-compose -f docker-compose.backend.yml restart backend

# Deploy backend updates
./deploy/deploy-backend-to-oci.sh 150.136.38.166

# Test build locally
npm run build

# Test AI chat
curl -X POST "https://backend.chandlerhardy.com/cryptassist/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { chatWithAssistant(message: \"Hello\") }"}'

# Populate sample portfolio data
python3 scripts/populate_with_available_assets.py

# Check available cryptocurrencies
python3 scripts/check_available_cryptos.py
```

## 🤖 AI Chat Service
- **Status**: ✅ Active and working
- **Model**: GitHub Llama 3.1 8B Instruct
- **Features**: Portfolio-aware advice, real-time market analysis
- **UI**: Glassmorphism floating chat widget

## 📊 Sample Portfolio Data & Population Tools
- **Status**: ✅ Working and tested
- **Location**: `/scripts/` directory
- **Purpose**: Create realistic portfolio data for testing and demonstrations

**Available Scripts:**
- `populate_with_available_assets.py` - Creates working demo portfolio with BTC, ETH, XRP
- `check_available_cryptos.py` - Lists available cryptocurrencies in the system
- `sample-portfolio-data.json` - Comprehensive sample data (5 portfolio strategies)
- `populate_sample_data.py` - Full population script (requires more crypto assets)

**Features Demonstrated:**
- Multiple buy transactions (Dollar Cost Averaging)
- Buy and sell transactions (realized profit/loss calculations)
- FIFO cost basis tracking
- Transaction history preservation
- Diverse investment strategies (DeFi, Layer 1, Blue Chip, Speculative)

**GraphQL Schema Requirements:**
- Assets: `portfolioId`, `cryptoId` (not symbol), `amount`, `buyPrice`
- Transactions: `portfolioId`, `assetId`, `transactionType`, `amount`, `pricePerUnit`, `notes`

## 📁 Key File Locations
```
crypto-assistant/
├── frontend/
│   ├── src/components/auth/      # Authentication components
│   ├── src/components/chatbot/    # AI chat components
│   ├── src/lib/graphql/          # GraphQL queries/mutations
│   ├── src/types/crypto.ts       # TypeScript interfaces
│   └── src/lib/apollo-client.ts  # GraphQL client setup
├── backend/
│   ├── app/main.py               # FastAPI app with admin GraphQL router
│   ├── app/schemas/mutations.py  # GraphQL mutations (AI, auth, admin)
│   ├── app/schemas/queries.py    # GraphQL queries (auth-aware)
│   ├── app/utils/auth.py         # JWT, password, admin utilities
│   ├── app/database/models.py    # User & portfolio models (with is_admin)
│   ├── app/services/ai_service.py # GitHub Llama integration
│   ├── app/core/config.py        # Environment config
│   └── docker-compose.backend.yml # Production container config
├── deploy/
│   └── deploy-backend-to-oci.sh  # Main deployment script
├── scripts/                      # Sample data and utilities
│   ├── populate_with_available_assets.py  # Working portfolio creator
│   ├── check_available_cryptos.py         # Check available assets
│   ├── sample-portfolio-data.json         # Comprehensive sample data
│   ├── populate_sample_data.py            # Full population script
│   └── README.md                          # Scripts documentation
└── CLAUDE.md                     # This file
```

## 🚨 Quick Fixes
- **AI chat not working**: Check `GITHUB_TOKEN` on OCI server
- **CORS errors**: Verify `CORS_ORIGINS` in backend `.env`
- **Build failures**: Usually TypeScript errors, check types
- **GraphQL 404**: Use `/cryptassist/graphql` endpoint (not `/graphql`)

## 📋 Recent Features Added
- ✅ AI chatbot with portfolio context awareness
- ✅ Glassmorphism UI effects on chat widget
- ✅ Portfolio data integration with AI responses
- ✅ GitHub Llama AI model integration
- ✅ Production deployment with SSL/HTTPS
- ✅ **Customizable Dashboard System**
  - Drag-and-drop reordering of dashboard sections
  - Fixed crypto sidebar with main content reordering
  - Glassmorphism effects on all controls
  - localStorage persistence for user preferences
  - Optimized chart heights and layout spacing
- ✅ Enhanced portfolio selling functionality with smart validation
- ✅ Comprehensive transaction ledger with historical preservation
- ✅ Realized P&L tracking with FIFO cost basis calculation
- ✅ Auto-modal closure and user feedback improvements
- ✅ **User Authentication System** (Completed)
  - Complete backend auth with JWT tokens and bcrypt password hashing
  - Frontend auth components with form validation
  - Login/Register forms with glassmorphism design
  - Auth context with localStorage persistence
  - Email validation and strong password requirements
  - User-specific portfolio isolation and security
  - Authentication-aware GraphQL queries and mutations
  - Protected routes and welcome landing page for unauthenticated users
- ✅ **Admin System & GraphQL Security** (Completed)
  - Admin user role system with `is_admin` database field
  - Admin-only GraphQL playground access in production
  - `createAdminUser` mutation with admin secret protection
  - Debug mode for unrestricted local development access
  - Role-based access control for sensitive operations
  - Production security while maintaining developer experience
- ✅ **Cryptocurrency Market Data Integration** (Completed)
  - Top cryptocurrencies list visible to all users (authenticated & unauthenticated)
  - Real-time crypto prices with 24-hour change indicators
  - Clean card-based layout with crypto icons and fallback letters
  - Fixed authentication flow issues (modal dismissal, route redirects)
  - Improved Apollo GraphQL client with proper JWT token authentication
- ✅ **Enhanced AI Chatbot Interface** (Completed)
  - Auto-expanding textarea for multi-line messages (Facebook-style)
  - Clean single-line input that grows vertically as needed
  - Improved text wrapping for long strings without spaces
  - Fixed send button height consistency and alignment
  - Increased popup height from 500px to 600px for better UX
  - Brand color integration (#F7C817) in UI elements for consistency
  - Removed placeholder text for cleaner initial appearance
  - Better readability with dark gray text on golden buttons
- ✅ **Authentication System Improvements & Database Persistence** (Latest - Completed)
  - Fixed JWT token expiration management (7-day tokens vs 30-minute)
  - Added client-side token validation and auto-cleanup of expired tokens
  - Enhanced GraphQL error handling with automatic auth recovery
  - Implemented persistent PostgreSQL database with proper docker-compose
  - Fixed deployment script to use correct PostgreSQL configuration
  - Resolved database reset issues on backend deployments
  - Admin user persistence across deployments
- ✅ **Sample Portfolio Data & Population Tools** (Latest - Completed)
  - Comprehensive sample portfolio data with 5 investment strategies
  - Working portfolio population scripts with correct GraphQL schema
  - Demonstrated features: DCA, realized P&L, transaction histories
  - Python and Bash scripts for easy data population
  - Fixed GraphQL mutations (cryptoId, buyPrice, transactionType fields)
  - Sample portfolios: Diversified, DeFi, Layer 1s, Blue Chip strategies

## 🔄 Development Workflow
1. **Make changes** locally in frontend/ or backend/
2. **Test locally**: `npm run dev` (frontend) or `uvicorn app.main:app --reload` (backend)
3. **Build test**: `npm run build` to check for TypeScript errors
4. **Commit & push** to main branch
5. **Frontend auto-deploys** via Vercel
6. **Backend deploy**: Run `./deploy/deploy-backend-to-oci.sh 150.136.38.166`

## 📊 Portfolio Features
- **Smart Selling**: Auto-validation caps sell amounts at available holdings
- **Transaction History**: Complete ledger preserving all transactions (even from sold assets)
- **Realized P&L Tracking**: FIFO cost basis calculation for accurate gain/loss reporting
- **P&L Percentage**: Includes both unrealized gains and realized profits in total return calculation
- **Performance Charts**: Recharts-based portfolio value timeline (basic implementation)
- **Modal UX**: Auto-close on asset sellout with user feedback notifications
- **Historical Preservation**: Maintains transaction records after assets are fully sold

## 📈 Charting & Analytics Roadmap
**Current (v1.0 - Basic Charts):**
- ✅ **Recharts Integration**: Simple line charts showing portfolio performance over time
- ✅ **Basic Timeline**: Transaction-based portfolio value reconstruction
- ✅ **Visual P&L**: Green/red coloring based on portfolio performance

**Future Enhancements (v2.0 - Advanced Charting):**
- 🔄 **Time Range Filters**: 1D, 1W, 1M, 3M, 1Y, ALL buttons (like Robinhood)
- 🔄 **Portfolio Snapshots**: Real-time database snapshots for accurate historical data  
- 🔄 **Transaction Date Input**: Allow users to backdate transactions for historical accuracy
- 🔄 **Advanced Charts**: Chart.js integration with zoom, pan, and crosshairs
- 🔄 **Multiple Metrics**: Volume, individual asset performance, correlation analysis
- 🔄 **TradingView Integration**: Professional-grade candlestick and technical analysis charts
- 🔄 **Comparative Analysis**: Portfolio vs market benchmarks (BTC, ETH, S&P 500)
- 🔄 **Performance Analytics**: Sharpe ratio, max drawdown, volatility metrics

## 🎛️ Customizable Dashboard (Next Priority)
**Goal**: Allow users to drag-and-drop reorder dashboard sections and customize layout

**Implementation Plan:**
1. **Add @dnd-kit/core** - Modern, accessible drag & drop library
2. **Create DashboardSection interface** - id, component, title, enabled, order
3. **Dashboard sections to make draggable:**
   - 📊 Summary Cards (Total Value, P&L, P&L %)
   - 📈 Portfolio Performance Chart  
   - 💼 Portfolio List (Your Portfolios)
   - 🪙 Top Cryptocurrencies (if added)
   - 🤖 AI Chat Widget (repositionable)

**Features to implement:**
- ✅ **Drag & Drop Reordering** - Move sections up/down with visual feedback
- ✅ **Toggle Sections On/Off** - Hide/show sections with eye icon
- ✅ **Save Layout** - Persist preferences in localStorage
- ✅ **Reset to Default** - Restore original layout
- 🔄 **Size Options** - Full width, half width, quarter width for sections
- 🔄 **Layout Presets** - "Trading Focus", "Portfolio Focus", "Overview" templates
- 🔄 **Customization Modal** - Settings panel for layout configuration

**Technical Details:**
- Use @dnd-kit/core for accessibility and modern React support
- Store layout in localStorage as DashboardSection[]
- Create DashboardCustomizer component with drag handles
- Implement visual feedback during drag operations

## 🔐 Authentication System (✅ Completed)

### ✅ Completed Components
**Backend:**
- ✅ User model with proper database relationships (`UserModel` in `models.py`)
- ✅ Password hashing with bcrypt (`app/utils/auth.py`)
- ✅ JWT token authentication system
- ✅ GraphQL register/login mutations (`mutations.py`)
- ✅ Email validation and strong password requirements
- ✅ Database migration script (`init_db.py`)

**Frontend:**
- ✅ Authentication GraphQL mutations (`REGISTER`, `LOGIN`)
- ✅ TypeScript types (`User`, `AuthResponse`, `RegisterInput`, `LoginInput`)
- ✅ Authentication context with localStorage (`AuthContext.tsx`)
- ✅ Login form with validation (`LoginForm.tsx`)
- ✅ Register form with strong password requirements (`RegisterForm.tsx`)
- ✅ Combined authentication modal (`AuthModal.tsx`)
- ✅ Clean component exports (`/components/auth/index.ts`)

### 🔄 Next Steps (Optional Enhancements)
1. **Email verification system** - Add email confirmation for new accounts
2. **Password reset functionality** - Allow users to reset forgotten passwords
3. **User profile management** - Edit user settings and preferences
4. **Session management** - Handle token refresh and automatic logout
5. **Two-factor authentication** - Add 2FA for enhanced security
6. **Production deployment** - Deploy updated auth system to production server

### 📝 Integration Guide
```tsx
// In your main layout (app/layout.tsx or _app.tsx):
import { AuthProvider } from '@/components/auth';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        <AuthProvider>
          <ApolloProvider client={client}>
            {children}
          </ApolloProvider>
        </AuthProvider>
      </body>
    </html>
  );
}

// In any component:
import { useAuth, AuthModal } from '@/components/auth';

const { user, isAuthenticated, login, logout } = useAuth();
```

## 📊 Database Schema (Key Models)
- **User**: id, email, hashed_password, is_active, is_verified, **is_admin**, created_at, updated_at, last_login
- **Portfolio**: id, name, totalValue, totalProfitLoss, totalRealizedProfitLoss, totalCostBasis, user_id, assets[]
- **PortfolioAsset**: id, symbol, amount, currentPrice, profitLoss, transactions[]
- **AssetTransaction**: id, type (buy/sell), amount, pricePerUnit, realizedProfitLoss, timestamp, portfolioId

## 🔍 GraphQL Schema (Key Endpoints)
```graphql
# Queries
query GetPortfolios { portfolios { ... } }
query GetPortfolioTransactions($portfolioId: String!) { ... }
query GetCryptocurrencies { cryptocurrencies { ... } }

# Mutations
mutation ChatWithAssistant($message: String!, $context: String)
mutation CreatePortfolio($input: CreatePortfolioInput)
mutation AddAssetToPortfolio($input: AddAssetInput)
mutation AddTransaction($input: AddTransactionInput)

# Authentication Mutations
mutation Register($input: RegisterInput!) { 
  register(input: $input) { 
    user { id, email, isActive, isVerified, isAdmin, createdAt, lastLogin }
    accessToken
    tokenType
  }
}
mutation Login($input: LoginInput!) { 
  login(input: $input) { 
    user { id, email, isActive, isVerified, isAdmin, createdAt, lastLogin }
    accessToken
    tokenType
  }
}

# Admin Mutations (requires ADMIN_SECRET)
mutation CreateAdminUser($email: String!, $password: String!, $adminSecret: String!) {
  createAdminUser(email: $email, password: $password, adminSecret: $adminSecret) {
    user { id, email, isAdmin }
    accessToken
  }
}
```

## ⚠️ Known Issues & Considerations
- **GraphQL endpoint**: Must use `/cryptassist/graphql` (not `/graphql`)
- **TypeScript strict**: All `any` types cause build failures
- **ARM64 architecture**: OCI server uses ARM, not x86
- **Environment variables**: Docker needs explicit env var passing
- **CORS configuration**: Frontend domain must be in backend CORS_ORIGINS
- **Cryptocurrency API Rate Limiting**: CoinGecko API may return limited assets (3 instead of expected 100+) due to rate limiting or API key issues. Core portfolio functionality works correctly - this only affects available asset selection.

## 💡 Important Notes
- Backend runs on OCI Always Free tier (ARM64)
- Frontend auto-deploys from main branch via Vercel
- AI requires GitHub Personal Access Token
- Database is persistent PostgreSQL with Docker volumes
- SSL certificates auto-renew via Let's Encrypt

---
*For detailed troubleshooting, see DEPLOYMENT_STATUS.md*