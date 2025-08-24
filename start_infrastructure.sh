#!/bin/bash

# Start Production Infrastructure for Payment Intelligence Platform
# This script sets up PostgreSQL, Redis, and monitoring stack

set -e  # Exit on any error

echo "🚀 Starting Payment Intelligence Infrastructure..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${BLUE}📋 Checking prerequisites...${NC}"

if ! command_exists docker; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command_exists docker-compose; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker and Docker Compose are installed${NC}"

# Create necessary directories
echo -e "${BLUE}📁 Creating directory structure...${NC}"
mkdir -p database monitoring/grafana/dashboards monitoring/grafana/datasources nginx

# Create database initialization script
echo -e "${BLUE}🗄️  Creating database initialization script...${NC}"
cat > database/init.sql << 'EOF'
-- Initialize Payment Intelligence Database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create application user
CREATE ROLE payment_intel_app WITH LOGIN PASSWORD 'app_password_123';

-- Grant permissions
GRANT CONNECT ON DATABASE payment_intel TO payment_intel_app;
GRANT CREATE ON DATABASE payment_intel TO payment_intel_app;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS insights;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS audit;

GRANT USAGE ON SCHEMA insights TO payment_intel_app;
GRANT USAGE ON SCHEMA analytics TO payment_intel_app;
GRANT USAGE ON SCHEMA audit TO payment_intel_app;

GRANT CREATE ON SCHEMA insights TO payment_intel_app;
GRANT CREATE ON SCHEMA analytics TO payment_intel_app;
GRANT CREATE ON SCHEMA audit TO payment_intel_app;

-- Initial setup message
SELECT 'Payment Intelligence Database initialized successfully!' as message;
EOF

# Create Prometheus configuration
echo -e "${BLUE}📊 Creating monitoring configuration...${NC}"
cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'payment-intel-api'
    static_configs:
      - targets: ['host.docker.internal:8000']
    
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
EOF

# Create Nginx configuration
echo -e "${BLUE}🌐 Creating reverse proxy configuration...${NC}"
cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream payment_intel_api {
        server host.docker.internal:8000;
    }
    
    upstream payment_intel_ui {
        server host.docker.internal:3000;
    }

    server {
        listen 80;
        server_name localhost;

        # Health check endpoint
        location /health {
            return 200 'OK';
            add_header Content-Type text/plain;
        }

        # API routes
        location /api/ {
            proxy_pass http://payment_intel_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # UI routes
        location / {
            proxy_pass http://payment_intel_ui;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
EOF

# Start the infrastructure
echo -e "${BLUE}🐳 Starting Docker containers...${NC}"
docker-compose up -d

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"

check_service() {
    local service=$1
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose ps $service | grep -q "healthy\|Up"; then
            echo -e "${GREEN}✅ $service is ready${NC}"
            return 0
        fi
        echo "   Attempt $attempt/$max_attempts: Waiting for $service..."
        sleep 2
        ((attempt++))
    done
    
    echo -e "${RED}❌ $service failed to start properly${NC}"
    return 1
}

# Check each service
check_service postgres
check_service redis
check_service timescaledb

echo -e "${GREEN}🎉 Infrastructure started successfully!${NC}"
echo ""
echo "📊 Service URLs:"
echo "  🗄️  PostgreSQL:     localhost:5432 (admin/secure_password_123)"
echo "  ⚡ Redis:          localhost:6379"  
echo "  📈 TimescaleDB:    localhost:5433 (admin/secure_password_123)"
echo "  📦 MinIO:          http://localhost:9001 (admin/secure_password_123)"
echo "  📊 Grafana:        http://localhost:3001 (admin/secure_password_123)"
echo "  📉 Prometheus:     http://localhost:9090"
echo "  🌐 Nginx Gateway:  http://localhost"
echo ""
echo "🚀 Next Steps:"
echo "  1. Install Python dependencies:"
echo "     pip install sqlalchemy redis asyncpg psycopg2-binary"
echo ""
echo "  2. Test database connection:"
echo "     python database/models.py"
echo ""
echo "  3. Start the enhanced insights manager:"
echo "     python services/enhanced_insights_manager.py"
echo ""
echo "  4. Test Crossmint integration:"
echo "     python processors/crossmint_processor.py"
echo ""
echo "  5. Open your browser:"
echo "     - Main app: http://localhost:3000"
echo "     - Monitoring: http://localhost:3001"
echo ""

# Show container status
echo -e "${BLUE}📋 Container Status:${NC}"
docker-compose ps

echo ""
echo -e "${YELLOW}💡 Pro Tips:${NC}"
echo "  • View logs: docker-compose logs -f [service_name]"
echo "  • Stop all: docker-compose down"
echo "  • Reset data: docker-compose down -v"
echo "  • Monitor resources: docker stats"
echo ""
echo -e "${GREEN}✨ Infrastructure is ready for development!${NC}"