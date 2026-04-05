# Deployment Guide

## Free Tier Architecture

This guide shows how to deploy the Security Incident Classification System using **free tier services**.

## Frontend: Vercel (Perfect Fit ✓)

### Why Vercel?
- **Optimized for React/Next.js** - Fast CDN, automatic deployments
- **Free tier**: 100GB bandwidth/month
- **Zero-config**: Automatic Git integration
- **Preview deploys**: Test every commit

### Configuration Steps

1. **Install Vercel CLI**
```bash
npm i -g vercel
```

2. **Create vercel.json** (Root directory)
```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/frontend/$1"
    }
  ],
  "env": {
    "VITE_API_URL": "@backend_api_url"
  }
}
```

3. **Build configuration** (Add to frontend/vite.config.ts)
```typescript
export default defineConfig({
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
```

4. **Deploy to Vercel**
```bash
cd frontend
vercel --prod
```

## Backend: Render.com (Free Tier)

### Why Render?
- **Free tier**: 750 service hours/month
- **PostgreSQL support** with extensions
- **Redis** available
- **Docker support**
- **Zero-downtime deploys**

### Configuration

1. **render.yaml** (Root directory)
```yaml
services:
  - type: web
    name: security-api
    env: python
    plan: free
    buildCommand: |
      cd backend
      pip install -r requirements.txt
      alembic upgrade head
    startCommand: |
      cd backend
      uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: security-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          name: security-cache
          property: connectionString
      - key: VAULT_MASTER_KEY
        generateValue: true
      - key: JWT_SECRET_KEY
        generateValue: true

  - type: redis
    name: security-cache
    plan: free
    ipAllowList: []  # From within Render only

databases:
  - name: security-db
    plan: free
    databaseName: security_incidents
    user: security_user
    postgresExtensions:
      - pgcrypto
    ipAllowList: []  # From within Render only
```

2. **Deploy**
```bash
git add render.yaml
git commit -m "chore: add Render deployment configuration"
git push origin main
```

Link GitHub to Render → Auto-deploy

## Alternative: Supabase (All-In-One)

### Why Supabase?
- **PostgreSQL with extensions** (including pgcrypto)
- **Edge Functions** (serverless backend)
- **Real-time subscriptions**
- **Vector embeddings** ready
- **Free tier**: 500MB DB, 1GB bandwidth

### Configuration

1. **Create Supabase project**: supabase.com

2. **supabase/config.toml** (Root directory)
```toml
[database]
extensions = ["pgcrypto"]

[functions.security-classify]
enabled = true
verify_jwt = true
import_map = "./backend/supabase/functions/import_map.json"
entrypoint = "./backend/supabase/functions/classify/index.ts"

[api]
enabled = true
```

3. **Edge Function** (TypeScript for classification)

## Alternative: Railway.app

Similar to Render but with simpler config. Good for Docker-based deployments.

## Database: Supabase PostgreSQL (Recommended)

### Configuration

1. **Enable pgcrypto extension**
```sql
-- In Supabase SQL editor
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

2. **Run migrations**
```bash
# From local machine
DATABASE_URL="postgresql://user:pass@db.supabase.co:5432/dbname" alembic upgrade head
```

3. **Secure connection**
```python
# Use SSL in connection string
postgresql://user:pass@db.supabase.co:5432/dbname?sslmode=require
```

## Redis Alternative: Upstash (Free)

### Configuration

1. **Sign up**: upstash.com
2. **Get Redis URL**
3. **Configure as REDIS_URL**

### Supabase Redis Alternative

Supabase offers Redis-compatible queues:
```sql
-- Enable pg_partman for queue management
CREATE EXTENSION IF NOT EXISTS pg_partman;
```

## Environment Variables Setup

Create `.env.production` template:

```bash
# Frontend (.env.production)
VITE_API_URL=https://your-api.onrender.com/api

# Backend (.env)
DATABASE_URL=${DATABASE_URL}
REDIS_URL=${REDIS_URL}
VAULT_MASTER_KEY=${VAULT_MASTER_KEY}
JWT_SECRET_KEY=${JWT_SECRET_KEY}
OPENAI_API_KEY=${OPENAI_API_KEY}
```

## Deployment Checklist

### Before First Deploy

- [ ] Generate production secrets (32-byte hex)
- [ ] Enable pgcrypto in database
- [ ] Run database migrations
- [ ] Configure CORS in backend
- [ ] Set up Vercel with proper env vars
- [ ] Test file upload limits
- [ ] Verify Redis connectivity
- [ ] Set up monitoring/alerting
- [ ] Create backup strategy

### Security Checklist

- [ ] Change all default passwords
- [ ] Enable 2FA on all services
- [ ] Use environment-specific secrets
- [ ] Restrict database access to backend only
- [ ] Enable SSL for all connections
- [ ] Set up audit log monitoring
- [ ] Configure rate limiting
- [ ] Disable unused services

### Monitoring Setup

**For Render:**
```yaml
# Add to render.yaml
envVars:
  - key: PROMETHEUS_ENABLED
    value: true
  - key: LOG_LEVEL
    value: INFO
```

**For Supabase:**
- Use Supabase monitoring dashboard
- Set up email alerts for anomalies

## Troubleshooting

### Common Issues

**"Database connection failed"**
- Verify SSL mode
- Check IP allowlist
- Confirm credentials

**"Redis connection timeout"**
- Check Redis URL format
- Verify network access
- Test with redis-cli

**"pgcrypto extension not found"**
- Run: CREATE EXTENSION pgcrypto
- Check PostgreSQL version (15+)

**"CORS errors"**
- Add Vercel preview URLs to ALLOWED_ORIGINS
- Include localhost for development

## Cost Estimates (Free Tier)

| Service | Free Tier | Estimated Cost |
|---------|-----------|----------------|
| Vercel Frontend | 100GB/mo | $0 |
| Render API | 750 hrs/mo | $0 |
| Supabase DB | 500MB | $0 |
| Redis/Upstash | 10k commands/day | $0 |
| **Total** | | **$0/month** |

## Next Steps

1. Choose your deployment stack (Recommend: Supabase + Vercel)
2. Set up accounts on chosen platforms
3. Run through deployment checklist
4. Deploy to staging environment first
5. Perform security audit
6. Document production procedures
7. Train users on system

## Production Considerations

For production deployments with >1000 incidents/day, consider:

- Upgraded Supabase ($25+/mo)
- Render paid tier ($25+/mo)
- OpenAI API costs
- Backup storage
- Additional security auditing
