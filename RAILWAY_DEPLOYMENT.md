# Railway Deployment Guide

## Quick Setup for Free Deployment

### 1. GitHub Repository Setup
1. Create a new GitHub repository for your Free Ping Indexer Pro
2. Push your code to the repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Free Ping Indexer Pro"
   git branch -M main
   git remote add origin https://github.com/yourusername/your-repo-name.git
   git push -u origin main
   ```

### 2. Railway Account Setup
1. Sign up at [railway.app](https://railway.app)
2. Connect your GitHub account for verification (required for free trial)
3. Your verification status will determine your trial type:
   - **Full Trial**: Can deploy code + databases (✓ $5 credit)
   - **Limited Trial**: Can only deploy databases

### 3. Deploy to Railway

#### Option A: Direct GitHub Integration (Recommended)
1. In Railway dashboard, click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your repository
4. Railway will automatically detect the configuration from `railway.json`

#### Option B: Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway link
railway up
```

### 4. Environment Variables
Set these in Railway dashboard under Variables:
```
SESSION_SECRET=your-secure-random-string-here
FLASK_ENV=production
PYTHONPATH=/app
```

### 5. Database (Optional)
If you need PostgreSQL:
1. In Railway project, click "New Service"
2. Select "PostgreSQL"
3. Railway will automatically set DATABASE_URL

## Configuration Files Already Set Up

✓ `railway.json` - Railway-specific configuration
✓ `Procfile` - Process definitions for web server
✓ `runtime.txt` - Python version specification
✓ `.github/workflows/deploy-railway.yml` - Automated CI/CD

## Features Enabled
- ✓ Automatic deployments on git push
- ✓ Health checks configured
- ✓ Proper worker scaling (2 workers)
- ✓ 120-second timeout for long-running ping operations
- ✓ Production-ready gunicorn configuration

## Cost Information
- **Free Trial**: $5 credit (enough for several months of light usage)
- **Hobby Plan**: $5/month (unlimited projects after trial)
- **Pro Plan**: $20/month (team features, more resources)

## Deployment Success Indicators
1. ✅ Build logs show successful Python package installation
2. ✅ Application starts without errors
3. ✅ Health check passes on root route `/`
4. ✅ All ping services and schedulers initialize properly

## Troubleshooting
- **Build Fails**: Check Python version in `runtime.txt` matches requirements
- **App Won't Start**: Verify `main:app` entry point in `Procfile`
- **Environment Issues**: Ensure all required environment variables are set
- **GitHub Actions Fails**: Add `RAILWAY_TOKEN` secret to GitHub repository settings