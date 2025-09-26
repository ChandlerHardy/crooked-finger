#!/bin/bash

# Backend-Only OCI Deployment Script for Crooked Finger
# Usage: ./deploy-backend-to-oci.sh <OCI_IP_ADDRESS>

set -e

# Configuration
OCI_IP="${1:-}"
OCI_USER="${OCI_USER:-ubuntu}"
SSH_KEY_PATH="${SSH_KEY_PATH:-/Users/chandlerhardy/.ssh/ampere.key}"
APP_NAME="crooked-finger"
DOCKER_COMPOSE_FILE="docker-compose.backend.yml"

# SSH command with key
SSH_CMD="ssh -i $SSH_KEY_PATH -o ConnectTimeout=10 -o BatchMode=yes"
RSYNC_SSH="ssh -i $SSH_KEY_PATH"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Validate arguments
if [ -z "$OCI_IP" ]; then
    print_error "Usage: $0 <OCI_IP_ADDRESS>"
    print_error "Example: $0 150.136.38.166"
    exit 1
fi

print_status "🚀 Starting Crooked Finger BACKEND deployment to OCI instance: $OCI_IP"
print_status "📍 Frontend will remain on Vercel"
print_status "🎯 Backend will run on port 8001 (separate from CryptAssist)"

# Check if we can SSH to the instance
print_status "Testing SSH connection..."
if ! $SSH_CMD "$OCI_USER@$OCI_IP" "echo 'SSH connection successful'" >/dev/null 2>&1; then
    print_error "Cannot connect to $OCI_IP via SSH"
    print_error "Make sure:"
    print_error "1. The IP address is correct"
    print_error "2. Your SSH key is added to the instance"
    print_error "3. Security groups allow SSH (port 22)"
    exit 1
fi

print_status "✅ SSH connection successful!"

# Create deployment directory on OCI instance
print_status "Setting up backend deployment directory..."
$SSH_CMD "$OCI_USER@$OCI_IP" "mkdir -p ~/$APP_NAME/backend ~/$APP_NAME/deploy"

# Copy backend files only
print_status "Copying backend files..."
rsync -avz --progress -e "$RSYNC_SSH" \
    --exclude='venv' \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='node_modules' \
    --exclude='architecture-examples' \
    ./backend/ "$OCI_USER@$OCI_IP:~/$APP_NAME/backend/"

# Copy deployment files
rsync -avz --progress -e "$RSYNC_SSH" \
    ./docker-compose.backend.yml \
    "$OCI_USER@$OCI_IP:~/$APP_NAME/"

# Install Docker and Docker Compose on OCI instance
print_status "Installing Docker and dependencies..."
$SSH_CMD "$OCI_USER@$OCI_IP" << 'ENDSSH'
# Update system
sudo apt-get update

# Install Docker if not already installed
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# Install Docker Compose if not already installed
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Install curl for health checks if not present
if ! command -v curl &> /dev/null; then
    sudo apt-get install -y curl
fi

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker
ENDSSH

# Build and start backend container
print_status "Building and starting Crooked Finger backend container..."
$SSH_CMD "$OCI_USER@$OCI_IP" << ENDSSH
cd ~/$APP_NAME

# Stop existing containers
docker-compose -f $DOCKER_COMPOSE_FILE down 2>/dev/null || true

# Remove old images to free space (but preserve CryptAssist images)
docker image prune -f --filter "label!=project=crypto-assistant"

# Build and start new backend container
docker-compose -f $DOCKER_COMPOSE_FILE up -d --build

# Wait for service to be healthy
echo "Waiting for Crooked Finger backend to start..."
sleep 30

# Check container status
docker-compose -f $DOCKER_COMPOSE_FILE ps
ENDSSH

# Configure firewall rules for backend only
print_status "Configuring firewall rules..."
$SSH_CMD "$OCI_USER@$OCI_IP" << 'ENDSSH'
# Allow backend API traffic on port 8001
sudo iptables -I INPUT -p tcp --dport 8001 -j ACCEPT

# Allow PostgreSQL access on port 5433 (if needed externally)
sudo iptables -I INPUT -p tcp --dport 5433 -j ACCEPT

# Save iptables rules
sudo sh -c "iptables-save > /etc/iptables/rules.v4" 2>/dev/null || true

# For Ubuntu/Debian, install iptables-persistent if not present
if ! dpkg -l | grep -q iptables-persistent; then
    sudo apt-get install -y iptables-persistent
    sudo sh -c "iptables-save > /etc/iptables/rules.v4"
fi
ENDSSH

# Test backend deployment
print_status "Testing Crooked Finger backend deployment..."
sleep 10

# Test backend health
if curl -f "http://$OCI_IP:8001/crooked-finger/health" >/dev/null 2>&1; then
    print_status "✅ Crooked Finger backend is healthy at http://$OCI_IP:8001"
else
    print_warning "⚠️  Backend health check failed - check logs with: ssh $OCI_USER@$OCI_IP 'cd $APP_NAME && docker-compose -f $DOCKER_COMPOSE_FILE logs backend'"
fi

# Test GraphQL endpoint
if curl -f "http://$OCI_IP:8001/crooked-finger/graphql" >/dev/null 2>&1; then
    print_status "✅ GraphQL endpoint is accessible"
else
    print_warning "⚠️  GraphQL endpoint check failed"
fi

print_status "🎉 Crooked Finger backend deployment completed!"
print_status ""
print_status "Your backend is accessible at:"
print_status "🔗 Backend API: http://$OCI_IP:8001"
print_status "🔗 GraphQL Playground: http://$OCI_IP:8001/crooked-finger/graphql"
print_status "🔗 Health Check: http://$OCI_IP:8001/crooked-finger/health"
print_status ""
print_status "📋 NEXT STEPS:"
print_status "1. Update your Vercel environment variable:"
print_status "   NEXT_PUBLIC_GRAPHQL_URL=http://$OCI_IP:8001/crooked-finger/graphql"
print_status ""
print_status "2. Update your backend CORS to allow Vercel:"
print_status "   CORS_ORIGINS=https://your-crooked-finger-app.vercel.app"
print_status ""
print_status "3. Set up your GitHub token for AI features:"
print_status "   ssh $OCI_USER@$OCI_IP 'cd $APP_NAME && echo \"GITHUB_TOKEN=your_token_here\" >> .env'"
print_status ""
print_status "4. Redeploy your frontend on Vercel to pick up the new backend URL"
print_status ""
print_status "To check logs:"
print_status "ssh $OCI_USER@$OCI_IP 'cd $APP_NAME && docker-compose -f $DOCKER_COMPOSE_FILE logs backend'"
print_status ""
print_status "To update the backend, run this script again."
print_status ""
print_warning "⚠️  Remember to configure OCI Security Groups to allow:"
print_warning "   - Port 8001 (Crooked Finger Backend API)"
print_warning "   - Port 5433 (PostgreSQL - if external access needed)"
print_warning ""
print_status "📊 Running alongside CryptAssist:"
print_status "   - CryptAssist: Port 8000"
print_status "   - Crooked Finger: Port 8001"
print_status "   Both services can run simultaneously!"