# 🚀 Deployment Guide

This repository includes automated deployment workflows for the Ustad Protocol MCP Server.

## 📋 Overview

- **Development Deployments**: Automatic deployment to `ustad-mcp-dev` service
- **Production Deployments**: Automatic deployment to `ustad-mcp-server` service
- **Continuous Integration**: Automated testing, linting, and security scanning

## 🔄 Automated Workflows

### Development Deployment (`deploy-dev.yml`)
- **Triggers**: Push to `dev`, `develop`, or `ustad-protocol-dev` branches
- **Target**: `ustad-mcp-dev` Cloud Run service
- **Features**:
  - Automated testing and linting
  - Docker build and deployment
  - Health check verification
  - Manual triggering available

### Production Deployment (`deploy-prod.yml`)
- **Triggers**: Push to `main`/`master` branches, releases
- **Target**: `ustad-mcp-server` Cloud Run service
- **Features**:
  - Enhanced security scanning
  - Production environment approval required
  - Version tagging for releases
  - Comprehensive health checks
  - Deployment summaries

### Continuous Integration (`ci.yml`)
- **Triggers**: Pull requests, pushes to main branches
- **Features**:
  - Cross-platform testing (Ubuntu, macOS, Windows)
  - Poetry dependency validation
  - Code quality analysis
  - Security vulnerability scanning
  - Test coverage reporting

## ⚙️ Setup Requirements

### 1. GitHub Secrets

Add these secrets to your GitHub repository:

```bash
GCP_SA_KEY  # Google Cloud Service Account JSON key
CODECOV_TOKEN  # Optional: For code coverage reporting
```

### 2. Google Cloud Setup

1. **Create Service Account**:
   ```bash
   gcloud iam service-accounts create github-actions \
     --display-name="GitHub Actions"
   ```

2. **Grant Permissions**:
   ```bash
   gcloud projects add-iam-policy-binding ustad-470310 \
     --member="serviceAccount:github-actions@ustad-470310.iam.gserviceaccount.com" \
     --role="roles/run.developer"
   
   gcloud projects add-iam-policy-binding ustad-470310 \
     --member="serviceAccount:github-actions@ustad-470310.iam.gserviceaccount.com" \
     --role="roles/cloudbuild.builds.builder"
   
   gcloud projects add-iam-policy-binding ustad-470310 \
     --member="serviceAccount:github-actions@ustad-470310.iam.gserviceaccount.com" \
     --role="roles/storage.admin"
   ```

3. **Create and Download Key**:
   ```bash
   gcloud iam service-accounts keys create github-actions-key.json \
     --iam-account=github-actions@ustad-470310.iam.gserviceaccount.com
   ```

4. **Add Key to GitHub Secrets**:
   - Go to repository Settings → Secrets and variables → Actions
   - Add secret named `GCP_SA_KEY` with the JSON key content

### 3. GitHub Environments

For production deployments, create a `production` environment:
1. Go to repository Settings → Environments
2. Create new environment named `production`
3. Add protection rules (optional):
   - Required reviewers
   - Wait timer
   - Deployment branches

## 🎯 Branch Strategy

```
main/master     → Production deployment
dev/develop     → Development deployment
feature/*       → CI testing only
pull requests   → CI testing only
```

## 📦 Service Configuration

### Development Service (`ustad-mcp-dev`)
- **URL**: https://ustad-mcp-dev-315016802391.us-central1.run.app
- **Max Instances**: 10
- **Memory**: 512Mi
- **CPU**: 1
- **Concurrency**: 1 (session isolation)

### Production Service (`ustad-mcp-server`)
- **URL**: https://ustad-mcp-server-315016802391.us-central1.run.app
- **Max Instances**: 20
- **Memory**: 1Gi
- **CPU**: 1
- **Concurrency**: 1 (session isolation)

## 🔍 Manual Deployment

### Using GitHub Actions UI
1. Go to Actions tab in GitHub
2. Select the desired workflow
3. Click "Run workflow"
4. Choose branch and parameters

### Using gcloud CLI
```bash
# Build image
gcloud builds submit --tag gcr.io/ustad-470310/ustad-mcp-server:latest .

# Deploy to development
gcloud run deploy ustad-mcp-dev \
  --image gcr.io/ustad-470310/ustad-mcp-server:latest \
  --region us-central1 \
  --allow-unauthenticated

# Deploy to production
gcloud run deploy ustad-mcp-server \
  --image gcr.io/ustad-470310/ustad-mcp-server:latest \
  --region us-central1 \
  --allow-unauthenticated
```

## 🧪 Testing Deployments

After deployment, verify endpoints:

```bash
SERVICE_URL="https://ustad-mcp-dev-315016802391.us-central1.run.app"

# Health check
curl -f $SERVICE_URL/health

# Capabilities
curl -f $SERVICE_URL/capabilities

# SSE endpoint
curl -I $SERVICE_URL/sse | grep "text/event-stream"
```

## 📊 Monitoring

- **Logs**: `gcloud logging read "resource.type=cloud_run_revision"`
- **Metrics**: Google Cloud Console → Cloud Run → Service
- **Alerts**: Set up based on error rates and latency

## 🔧 Troubleshooting

### Common Issues

1. **Build Failures**:
   - Check dependency conflicts in `poetry.lock`
   - Verify Docker base image availability
   - Review build logs in Cloud Build console

2. **Deployment Failures**:
   - Verify service account permissions
   - Check resource quotas
   - Validate environment variables

3. **Runtime Issues**:
   - Check service logs
   - Verify health endpoint responses
   - Test MCP protocol connectivity

### Debug Commands

```bash
# View service details
gcloud run services describe ustad-mcp-dev --region us-central1

# Check recent logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=ustad-mcp-dev" --limit 50

# Test local build
docker build -t test-server .
docker run -p 8000:8000 -e PORT=8000 test-server
```

## 🔄 Rollback Strategy

### Automatic Rollback
Cloud Run maintains previous revisions automatically.

### Manual Rollback
```bash
# List revisions
gcloud run revisions list --service ustad-mcp-server --region us-central1

# Rollback to previous revision
gcloud run services update-traffic ustad-mcp-server \
  --to-revisions=REVISION-NAME=100 \
  --region us-central1
```

## 📈 Performance Optimization

- **Cold Start**: Minimized through optimized Docker image
- **Session Isolation**: Concurrency=1 ensures independent Claude sessions
- **Resource Limits**: Tuned for MCP protocol requirements
- **Auto-scaling**: Based on request volume

## 🔐 Security

- **No authentication required**: Public endpoints for MCP protocol
- **Container Security**: Non-root user, minimal attack surface
- **Dependency Scanning**: Automated vulnerability checks
- **Secret Management**: Environment variables only, no hardcoded secrets