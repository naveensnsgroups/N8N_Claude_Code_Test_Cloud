# FastAPI Backend - Deployment Guide

## Pre-Deployment Checklist

- [ ] All tests passing (see TESTING_GUIDE.md)
- [ ] Environment variables configured (.env)
- [ ] MongoDB connection verified
- [ ] Frontend URLs updated (if applicable)
- [ ] Performance tested and acceptable
- [ ] Security review completed
- [ ] Backup of Express backend created
- [ ] Rollback plan documented

---

## Local Development

### Option 1: Uvicorn (Simplest)

```bash
# Development with auto-reload
uvicorn main:app --reload

# Production mode
uvicorn main:app --host 0.0.0.0 --port 5000
```

**Pros**: Simple, fast development cycle
**Cons**: Single worker, not recommended for production

---

## Production Deployment

### Option 1: Gunicorn + Uvicorn Workers (Recommended)

Install Gunicorn:
```bash
pip install gunicorn
```

Start server:
```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:5000 \
  --access-logfile - \
  --error-logfile - \
  --log-level info
```

**Pros**: Multiple workers, production-grade, easy scaling
**Cons**: Requires Gunicorn installation

### Configuration for Different Workloads

**Light Load (< 100 concurrent)**
```bash
gunicorn main:app \
  --workers 2 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:5000
```

**Medium Load (100-1000 concurrent)**
```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:5000 \
  --threads 2
```

**Heavy Load (1000+ concurrent)**
```bash
gunicorn main:app \
  --workers 8 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:5000 \
  --threads 2 \
  --max-requests 1000 \
  --max-requests-jitter 100
```

---

### Option 2: Docker

#### Simple Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run application
CMD ["gunicorn", "main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:5000"]
```

#### Build & Run

```bash
# Build image
docker build -t employee-api:latest .

# Run container
docker run -d \
  --name employee-api \
  -p 5000:5000 \
  -e MONGO_URI=<your-mongo-uri> \
  -e NODE_ENV=production \
  -e CLIENT_URL=<your-frontend-url> \
  employee-api:latest

# View logs
docker logs -f employee-api

# Stop container
docker stop employee-api
```

#### Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      MONGO_URI: ${MONGO_URI}
      NODE_ENV: production
      CLIENT_URL: ${CLIENT_URL}
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_USER}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
    volumes:
      - mongodb_data:/data/db
    restart: always

volumes:
  mongodb_data:
```

**Pros**: Containerized, easy deployment, reproducible
**Cons**: Docker required, slightly more complex

---

### Option 3: Heroku

#### Setup

```bash
# Create Heroku app
heroku create your-app-name

# Add MongoDB addon
heroku addons:create mongolab:sandbox

# Or use external MongoDB
heroku config:set MONGO_URI=<your-mongo-uri>

# Set environment variables
heroku config:set NODE_ENV=production
heroku config:set CLIENT_URL=https://your-frontend.com
```

#### Procfile

Create `Procfile` in project root:

```
web: gunicorn main:app --worker-class uvicorn.workers.UvicornWorker --workers 4 --bind 0.0.0.0:$PORT
```

#### Deploy

```bash
# Push to Heroku
git push heroku main

# View logs
heroku logs --tail

# Scale dynos
heroku ps:scale web=3
```

**Pros**: Easy deployment, automatic HTTPS, simple scaling
**Cons**: Limited customization, can be expensive at scale

---

### Option 4: Railway

#### Setup

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Set environment variables
railway variables set MONGO_URI=<your-mongo-uri>
railway variables set NODE_ENV=production
```

#### Deploy

```bash
# Deploy
railway up

# View logs
railway logs

# Check status
railway status
```

**Pros**: Simple, good documentation, free tier available
**Cons**: Smaller community than Heroku

---

### Option 5: Render

#### Setup via Web UI

1. Go to https://render.com
2. Connect GitHub account
3. New → Web Service
4. Select repository
5. Configure:
   - **Name**: `employee-api`
   - **Runtime**: `Python 3.11`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn main:app --worker-class uvicorn.workers.UvicornWorker --workers 4 --bind 0.0.0.0:5000`
6. Add Environment Variables:
   - `MONGO_URI`: <your-mongo-uri>
   - `NODE_ENV`: `production`
   - `CLIENT_URL`: <your-frontend-url>
7. Deploy

**Pros**: Automatic from GitHub, good free tier, easy scaling
**Cons**: Smaller service, less documentation

---

### Option 6: AWS Lambda (Serverless)

#### Install Dependencies

```bash
pip install mangum
```

#### Create Wrapper

Create `handler.py`:

```python
from mangum import Mangum
from main import app

handler = Mangum(app)
```

#### Deploy via Serverless Framework

```bash
npm install -g serverless
npm install --save-dev serverless-python-requirements

serverless deploy
```

**Pros**: Pay per request, auto-scaling, reliable
**Cons**: Cold starts possible, more complex setup

---

## Environment Variables

### Required
```bash
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/dbname?retryWrites=true&w=majority
```

### Optional
```bash
PORT=5000                          # Default: 5000
HOST=0.0.0.0                       # Default: 0.0.0.0
NODE_ENV=production                # Default: development
CLIENT_URL=https://yourapp.com     # Default: http://localhost:5173
```

### Setting Environment Variables

#### Local (.env file)
```bash
# Create .env
cp .env.example .env

# Edit with your values
MONGO_URI=your_uri_here
NODE_ENV=production
CLIENT_URL=https://yourapp.com
```

#### Heroku
```bash
heroku config:set KEY=VALUE
```

#### Docker
```bash
docker run -e MONGO_URI=<uri> -e NODE_ENV=production employee-api
```

#### Docker Compose
```yaml
environment:
  MONGO_URI: ${MONGO_URI}
  NODE_ENV: production
```

#### GitHub Actions / CI/CD
```yaml
env:
  MONGO_URI: ${{ secrets.MONGO_URI }}
  NODE_ENV: production
```

---

## Monitoring & Health Checks

### Health Check Endpoint
```bash
curl http://localhost:5000/
# Returns: {"success": true, "message": "Personal Details API is running."}
```

### Logging

Logs are output to stdout/stderr:
```
INFO:     Application startup complete
INFO:     Server running in production mode on port 5000
```

### Performance Monitoring

#### Using Prometheus (Optional)

Install prometheus_client:
```bash
pip install prometheus-client
```

Add to main.py:
```python
from prometheus_client import Counter, Histogram

request_count = Counter('app_requests_total', 'Total requests')
request_duration = Histogram('app_request_duration_seconds', 'Request duration')
```

#### Using APM Services
- **New Relic**: APM monitoring
- **DataDog**: Infrastructure monitoring
- **Sentry**: Error tracking

### Database Monitoring

Monitor MongoDB performance:
- Connection pool status
- Query performance
- Index usage
- Replication lag

---

## Scaling

### Horizontal Scaling

Add more workers:
```bash
# With Gunicorn
gunicorn main:app --workers 8

# With Docker Compose
docker-compose up --scale api=3

# With Heroku
heroku ps:scale web=5
```

### Vertical Scaling

Increase server capacity:
- CPU cores
- Memory
- Database tier

### Load Balancing

Use reverse proxy (Nginx):
```nginx
upstream api {
    server localhost:5000;
    server localhost:5001;
    server localhost:5002;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Backup & Disaster Recovery

### Database Backup
```bash
# Automatic via MongoDB Atlas (recommended)
# Or manual:
mongodump --uri "mongodb+srv://..." --out backup/

# Restore:
mongorestore --uri "mongodb+srv://..." backup/
```

### Code Backup
```bash
# Git push to GitHub/GitLab
git push origin main

# Create release tag
git tag -a v1.0.0 -m "Production release"
git push origin v1.0.0
```

### Environment Backup
```bash
# Save .env before deployment
cp .env .env.backup.$(date +%Y%m%d)

# Keep in secure location (not in Git!)
```

---

## Rollback Procedure

If issues occur after deployment:

### Quick Rollback (< 5 minutes)

```bash
# Option 1: Restart Express backend
cd backend
npm start

# Option 2: Revert FastAPI to previous image
docker pull employee-api:previous
docker run -p 5000:5000 employee-api:previous

# Option 3: Heroku rollback
heroku releases
heroku rollback v<number>
```

### Full Rollback (Git)
```bash
# Find previous commit
git log --oneline

# Revert to previous version
git revert <commit-hash>
git push origin main

# Redeploy
git push heroku main
```

### Data Rollback

If data corruption:
```bash
# Restore from backup
mongorestore --uri "mongodb+srv://..." backup/
```

---

## Testing Before Production

### Load Testing
```bash
# 1000 requests, 10 concurrent
ab -n 1000 -c 10 http://localhost:5000/

# Or with wrk
wrk -t4 -c100 -d30s http://localhost:5000/
```

### Full Test Suite
```bash
pytest test_main.py -v --cov=.
```

### Manual Integration Test
```bash
# Run all test cases from TESTING_GUIDE.md
# Create → Read → Update → Delete
```

---

## Monitoring Checklist

After deployment, monitor:

- [ ] API is responding (curl / health check)
- [ ] Response times are acceptable
- [ ] Error rate is low (< 0.1%)
- [ ] Database connections are stable
- [ ] No memory leaks
- [ ] Rate limiting is working
- [ ] CORS headers present
- [ ] Logs are clean (no errors)
- [ ] Frontend can connect
- [ ] All endpoints working

---

## Common Issues & Solutions

### Port Already in Use
```bash
# Find process using port
lsof -i :5000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn main:app --port 8000
```

### High Memory Usage
```bash
# Check current usage
ps aux | grep gunicorn

# Reduce workers if too high
gunicorn main:app --workers 2
```

### Slow Response Times
```bash
# Check database connection
# Verify MongoDB Atlas performance
# Check network latency
# Profile slow queries
```

### Rate Limiting Issues
- Verify correct IP is being rate limited
- Check rate limit settings in config.py
- Test with multiple IPs

### MongoDB Connection Timeout
- Check MONGO_URI format
- Verify IP whitelist in MongoDB Atlas
- Check network connectivity
- Verify credentials

---

## Performance Tuning

### For High Throughput
```bash
gunicorn main:app \
  --workers 8 \
  --worker-class uvicorn.workers.UvicornWorker \
  --threads 2 \
  --max-requests 5000
```

### For Low Latency
```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:5000 \
  --timeout 30
```

### For Stability
```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --max-requests 1000 \
  --max-requests-jitter 100
```

---

## Maintenance

### Regular Tasks

**Daily**:
- Check logs for errors
- Verify health check endpoint
- Monitor error rate

**Weekly**:
- Review performance metrics
- Check database size
- Verify backups

**Monthly**:
- Update dependencies: `pip install --upgrade -r requirements.txt`
- Review security advisories
- Test disaster recovery

### Keeping Up to Date

```bash
# Check for updates
pip list --outdated

# Update FastAPI
pip install --upgrade fastapi

# Update all packages safely
pip install --upgrade -r requirements.txt

# Run tests after update
pytest test_main.py -v
```

---

## Summary

| Deployment | Effort | Scalability | Cost |
|-----------|--------|-------------|------|
| **Gunicorn** | ⭐⭐ | ⭐⭐⭐ | ⭐ |
| **Docker** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ |
| **Heroku** | ⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Railway** | ⭐ | ⭐⭐⭐ | ⭐⭐ |
| **AWS Lambda** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |

**Recommended for most cases: Gunicorn + Docker + Load Balancer**

---

## Next Steps

1. Choose deployment option from above
2. Follow setup instructions
3. Configure environment variables
4. Deploy to staging first
5. Run full test suite
6. Deploy to production
7. Monitor for issues
8. Setup alerts/monitoring
9. Document deployment
10. Create rollback procedure

---

For more information:
- **Setup**: See QUICKSTART.md
- **Testing**: See TESTING_GUIDE.md
- **API Usage**: See README.md
- **Troubleshooting**: See MIGRATION_GUIDE.md
