# Free Ping Indexer Pro - Deployment Guide

## Multiple Deployment Options

Your Free Ping Indexer Pro can be deployed to various platforms for FREE using GitHub Actions. Here are the available options:

### 🚀 Quick Deploy Options

#### 1. Railway (Recommended)
- **Cost**: Free tier available
- **Features**: PostgreSQL database, automatic HTTPS, custom domains
- **Setup Time**: 5 minutes

**Steps:**
1. Fork this repository to your GitHub account
2. Create a [Railway](https://railway.app) account
3. Get your Railway token from Railway Dashboard → Account → Tokens
4. Add `RAILWAY_TOKEN` to your GitHub repository secrets
5. Push to main branch - deployment happens automatically!

#### 2. Render
- **Cost**: Free tier with 750 hours/month
- **Features**: PostgreSQL database, automatic HTTPS, custom domains
- **Setup Time**: 3 minutes

**Steps:**
1. Create a [Render](https://render.com) account
2. Get API key from Account Settings → API Keys
3. Create a new service and get the service ID
4. Add `RENDER_API_KEY` and `RENDER_SERVICE_ID` to GitHub secrets
5. Push to deploy!

#### 3. Heroku
- **Cost**: Free tier discontinued, but affordable dyno options
- **Features**: PostgreSQL add-on, custom domains, extensive add-ons
- **Setup Time**: 5 minutes

**Steps:**
1. Create [Heroku](https://heroku.com) account
2. Get API key from Account Settings → API Keys
3. Add `HEROKU_API_KEY` and `HEROKU_EMAIL` to GitHub secrets
4. Push to deploy!

#### 4. Vercel (Serverless)
- **Cost**: Free tier with generous limits
- **Features**: Serverless functions, automatic HTTPS, global CDN
- **Setup Time**: 5 minutes
- **Note**: Best for light usage due to serverless limitations

### 🔧 Environment Variables

For any deployment platform, you'll need these environment variables:

**Required:**
```bash
SESSION_SECRET=your-secret-key-here
DATABASE_URL=postgresql://user:password@host:port/database
```

**Optional (for advanced features):**
```bash
# Professional proxy rotation (optional)
PROXY_HTTP=http://username:password@proxy-server:port
PROXY_HTTPS=https://username:password@proxy-server:port

# Email notifications (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 📊 Platform Comparison

| Platform | Cost | Database | Custom Domain | Deployment Time | Best For |
|----------|------|----------|---------------|-----------------|----------|
| Railway | Free/Paid | ✅ PostgreSQL | ✅ | 5 min | Production apps |
| Render | Free/Paid | ✅ PostgreSQL | ✅ | 3 min | Simple deployment |
| Heroku | Paid | ✅ PostgreSQL | ✅ | 5 min | Enterprise features |
| Vercel | Free/Paid | 🔄 External DB | ✅ | 5 min | Light usage |

### 🐳 Docker Deployment

For advanced users, deploy using Docker:

```bash
# Build the image
docker build -t free-ping-indexer-pro .

# Run with environment variables
docker run -d \
  -p 5000:5000 \
  -e SESSION_SECRET=your-secret \
  -e DATABASE_URL=your-db-url \
  --name ping-indexer \
  free-ping-indexer-pro
```

### 📋 GitHub Actions Configuration

The `.github/workflows/deploy.yml` file is already configured for multiple platforms. To enable deployment:

1. **Choose your platform** (Railway, Render, Heroku, or Vercel)
2. **Add secrets** to your GitHub repository:
   - Go to Settings → Secrets and variables → Actions
   - Add the required tokens/keys for your chosen platform
3. **Push to main branch** - deployment happens automatically!

### 🔒 Required GitHub Secrets

**For Railway:**
- `RAILWAY_TOKEN`

**For Render:**
- `RENDER_API_KEY`
- `RENDER_SERVICE_ID`

**For Heroku:**
- `HEROKU_API_KEY`
- `HEROKU_EMAIL`

**For Vercel:**
- `VERCEL_TOKEN`
- `ORG_ID`
- `PROJECT_ID`

**For Docker Hub (optional):**
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

### ✅ Post-Deployment Checklist

After deployment:
1. ✅ Visit your deployed URL to confirm it's working
2. ✅ Test a small ping campaign to verify functionality
3. ✅ Check logs for any errors
4. ✅ Set up your database (if not auto-created)
5. ✅ Configure any environment variables for advanced features

### 🛠 Troubleshooting

**Common Issues:**

1. **Build Failures**: Check that all dependencies are in `pyproject.toml`
2. **Database Errors**: Ensure `DATABASE_URL` is properly set
3. **Port Issues**: The app binds to `0.0.0.0:$PORT` automatically
4. **Environment Variables**: Double-check all required secrets are set

### 📞 Support

If you need help with deployment:
1. Check the platform-specific documentation
2. Review the GitHub Actions logs for error details
3. Ensure all secrets are properly configured

### 🎯 Production Considerations

For production use:
- Set up monitoring and alerting
- Configure backup for your database
- Use environment-specific configurations
- Consider setting up a custom domain
- Monitor your usage to stay within free tiers

---

**Ready to deploy?** Choose your platform above and follow the steps. Your Free Ping Indexer Pro will be live in minutes!