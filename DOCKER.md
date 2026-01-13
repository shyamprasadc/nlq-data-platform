# Docker Deployment Guide

## Quick Start

### Development with Docker Compose

```bash
# Start all services (app + PostgreSQL + Redis)
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

Access the application at: http://localhost:8000

---

## Docker Files Overview

### 1. **Dockerfile**
Multi-stage build for optimized production image:
- **Stage 1 (Builder)**: Installs dependencies
- **Stage 2 (Runtime)**: Minimal runtime image with non-root user

**Key Features:**
- ✅ Multi-stage build (smaller image size)
- ✅ Non-root user for security
- ✅ Health check endpoint
- ✅ Uses `uv` for fast dependency installation

### 2. **docker-compose.yml**
Complete stack with:
- **FastAPI app** (port 8000)
- **PostgreSQL database** (port 5432)
- **Redis cache** (port 6379)

**Key Features:**
- ✅ Service health checks
- ✅ Persistent volumes for data
- ✅ Network isolation
- ✅ Auto-restart policies

### 3. **.dockerignore**
Excludes unnecessary files from build context:
- Virtual environments
- Cache files
- Development databases
- IDE configurations

---

## Common Commands

### Build & Run

```bash
# Build the Docker image
docker build -t nlq-backend .

# Run a single container
docker run -d -p 8000:8000 --name nlq-app nlq-backend

# Run with environment variables
docker run -d -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host/db \
  -e SECRET_KEY=your-secret-key \
  --name nlq-app nlq-backend
```

### Using Docker Compose

```bash
# Start services in background
docker-compose up -d

# Start and rebuild
docker-compose up -d --build

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f app

# Stop services
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v

# Restart a service
docker-compose restart app

# Execute command in running container
docker-compose exec app bash
```

### Debugging

```bash
# Check running containers
docker ps

# View container logs
docker logs fastapi-app

# Follow logs in real-time
docker logs -f fastapi-app

# Execute bash in running container
docker exec -it fastapi-app bash

# Inspect container
docker inspect fastapi-app

# View resource usage
docker stats
```

### Database Operations

```bash
# Access PostgreSQL shell
docker-compose exec db psql -U postgres -d fastapi_db

# Create database backup
docker-compose exec db pg_dump -U postgres fastapi_db > backup.sql

# Restore database
docker-compose exec -T db psql -U postgres fastapi_db < backup.sql

# View database logs
docker-compose logs -f db
```

---

## Environment Variables

### Required
- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - JWT secret key (generate with `openssl rand -hex 32`)

### Optional
- `ALGORITHM` - JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration (default: 30)
- `CORS_ORIGINS` - Allowed CORS origins
- `ENVIRONMENT` - Environment name (development/production)

### Setting Environment Variables

**Option 1: .env file**
```bash
# Create .env file
cp .env .env.production

# Edit values
nano .env.production
```

**Option 2: docker-compose.yml**
```yaml
environment:
  - DATABASE_URL=postgresql://...
  - SECRET_KEY=your-secret-key
```

**Option 3: Command line**
```bash
docker run -e DATABASE_URL=postgresql://... -e SECRET_KEY=... nlq-backend
```

---

## Production Deployment

### 1. Build Production Image

```bash
# Build with tag
docker build -t nlq-backend:1.0.0 .

# Tag for registry
docker tag nlq-backend:1.0.0 your-registry/nlq-backend:1.0.0

# Push to registry
docker push your-registry/nlq-backend:1.0.0
```

### 2. Update docker-compose.yml for Production

```yaml
services:
  app:
    image: your-registry/nlq-backend:1.0.0
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
    # Remove volume mount for code
    # volumes:
    #   - ./app:/app/app
```

### 3. Security Best Practices

✅ **Use secrets management**
```bash
# Docker secrets (Swarm mode)
echo "your-secret-key" | docker secret create jwt_secret -

# Or use environment variables from secure vault
export SECRET_KEY=$(vault read -field=value secret/jwt_key)
```

✅ **Run as non-root user** (already configured in Dockerfile)

✅ **Scan for vulnerabilities**
```bash
docker scan nlq-backend
```

✅ **Use specific image tags** (not `latest`)

✅ **Limit resources**
```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
```

---

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs app

# Check if port is already in use
lsof -i :8000

# Rebuild without cache
docker-compose build --no-cache
```

### Database connection issues
```bash
# Check if database is healthy
docker-compose ps

# Test database connection
docker-compose exec app python -c "from app.db.session import engine; print(engine.connect())"

# Check database logs
docker-compose logs db
```

### Permission issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Or run as root (not recommended)
docker-compose exec -u root app bash
```

### Out of disk space
```bash
# Remove unused containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Remove everything unused
docker system prune -a
```

---

## Health Checks

The application includes a health check endpoint:

```bash
# Manual health check
curl http://localhost:8000/health

# Docker health check status
docker inspect --format='{{.State.Health.Status}}' fastapi-app
```

---

## Scaling

### Horizontal Scaling with Docker Compose

```bash
# Scale app to 3 instances
docker-compose up -d --scale app=3

# Use nginx for load balancing
# Add nginx service to docker-compose.yml
```

### Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml fastapi-stack

# Scale service
docker service scale fastapi-stack_app=3

# View services
docker service ls
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Docker image
        run: docker build -t nlq-backend .
      
      - name: Run tests
        run: docker run nlq-backend pytest
      
      - name: Push to registry
        run: |
          docker tag nlq-backend ${{ secrets.REGISTRY }}/nlq-backend:${{ github.sha }}
          docker push ${{ secrets.REGISTRY }}/nlq-backend:${{ github.sha }}
```

---

## Monitoring

### View Resource Usage

```bash
# Real-time stats
docker stats

# Specific container
docker stats fastapi-app
```

### Export Logs

```bash
# Export to file
docker-compose logs > logs.txt

# Export with timestamps
docker-compose logs -t > logs.txt
```

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `docker-compose up -d` | Start all services |
| `docker-compose down` | Stop all services |
| `docker-compose logs -f app` | View app logs |
| `docker-compose exec app bash` | Access app container |
| `docker-compose restart app` | Restart app |
| `docker-compose ps` | List running services |
| `docker-compose build` | Rebuild images |
| `docker system prune` | Clean up unused resources |

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Docker Deployment](https://fastapi.tiangolo.com/deployment/docker/)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
