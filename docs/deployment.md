# Deployment Guide

## Overview

This guide covers the complete deployment process for the XTHLETE Tournament Management System across different platforms.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (Next.js)     │    │   (Next.js)     │    │  (Supabase)     │
│   Vercel        │    │    Render       │    │   Supabase      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prerequisites

- Node.js 18+ installed locally
- Git repository with the project code
- Supabase account (for database)
- Vercel account (for frontend)
- Render account (for backend)

## Environment Variables

Create `.env.production` file:

```bash
# Database
DATABASE_URL="postgresql://user:password@host:port/database"

# Next.js
NEXTAUTH_URL="https://your-domain.com"
NEXTAUTH_SECRET="your-secret-key"

# Supabase
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_ANON_KEY="your-anon-key"
SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"

# Application
APP_URL="https://your-domain.com"
API_URL="https://your-api-domain.com"
```

## Database Setup (Supabase)

### 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Click "New Project"
3. Choose organization and project name
4. Set database password
5. Select region closest to your users
6. Click "Create new project"

### 2. Configure Database

1. Go to SQL Editor in Supabase dashboard
2. Run the Prisma schema:

```sql
-- Copy the contents of prisma/schema.prisma
-- Convert to SQL and run in Supabase
```

3. Or use Prisma with Supabase:

```bash
# Install Supabase CLI
npm install -g supabase

# Link to your project
supabase link --project-ref your-project-ref

# Push schema
supabase db push
```

### 3. Get Connection Details

From Supabase dashboard → Settings → Database:
- Connection string
- API URL
- Service role key

## Frontend Deployment (Vercel)

### 1. Install Vercel CLI

```bash
npm i -g vercel
```

### 2. Configure Vercel Project

1. Login to Vercel:
```bash
vercel login
```

2. Link project:
```bash
vercel link
```

3. Configure `vercel.json`:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/next"
    }
  ],
  "env": {
    "DATABASE_URL": "@database_url",
    "NEXTAUTH_URL": "@nextauth_url",
    "NEXTAUTH_SECRET": "@nextauth_secret"
  },
  "regions": ["iad1"],
  "functions": {
    "src/pages/api/**/*.ts": {
      "maxDuration": 30
    }
  }
}
```

### 3. Deploy to Vercel

```bash
# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

### 4. Set Environment Variables in Vercel Dashboard

1. Go to Vercel dashboard
2. Select your project
3. Go to Settings → Environment Variables
4. Add all required variables:
   - `DATABASE_URL`
   - `NEXTAUTH_URL`
   - `NEXTAUTH_SECRET`
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`

### 5. Configure Custom Domain (Optional)

1. In Vercel dashboard → Settings → Domains
2. Add your custom domain
3. Configure DNS records as instructed

## Backend Deployment (Render)

### 1. Prepare Backend for Render

Create `render.yaml` in root:

```yaml
services:
  - type: web
    name: xthlete-api
    env: node
    buildCommand: "npm run build"
    startCommand: "npm start"
    healthCheckPath: /api/health
    envVars:
      - key: NODE_ENV
        value: production
      - key: DATABASE_URL
        sync: false
      - key: NEXTAUTH_SECRET
        sync: false
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_SERVICE_ROLE_KEY
        sync: false
    disk:
      name: xthlete-disk
      mountPath: /opt/render/project/.next
      sizeGB: 1
```

### 2. Update package.json for Production

```json
{
  "scripts": {
    "start": "next start",
    "build": "next build",
    "dev": "next dev"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
```

### 3. Deploy to Render

1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your Git repository
4. Configure:
   - Name: `xthlete-api`
   - Environment: `Node`
   - Build Command: `npm run build`
   - Start Command: `npm start`
   - Instance Type: `Free` or `Starter`

5. Add Environment Variables:
   - `NODE_ENV`: `production`
   - `DATABASE_URL`: Your Supabase connection string
   - `NEXTAUTH_SECRET`: Generate random secret
   - `SUPABASE_URL`: Your Supabase URL
   - `SUPABASE_SERVICE_ROLE_KEY`: Your service role key

6. Click "Create Web Service"

### 4. Configure Custom Domain (Optional)

1. In Render dashboard → Custom Domains
2. Add your API domain
3. Configure DNS records

## Database Migration

### 1. Generate Prisma Client

```bash
npx prisma generate
```

### 2. Push Schema to Production

```bash
# Using Supabase CLI
supabase db push

# Or using Prisma with direct connection
DATABASE_URL="your-production-db-url" npx prisma db push
```

### 3. Seed Production Database (Optional)

Create `prisma/seed-production.js`:

```javascript
const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

async function main() {
  // Create default clubs
  const clubs = await Promise.all([
    prisma.club.create({
      data: { name: 'Tennis Club A', code: 'TCA' }
    }),
    prisma.club.create({
      data: { name: 'Sports Academy B', code: 'SAB' }
    })
  ]);

  // Create default events
  await Promise.all([
    prisma.event.create({
      data: {
        name: 'Men\'s Singles',
        category: 'Open',
        type: 'Singles'
      }
    }),
    prisma.event.create({
      data: {
        name: 'Women\'s Singles',
        category: 'Open',
        type: 'Singles'
      }
    })
  ]);

  console.log('Database seeded successfully');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
```

Run seed script:
```bash
DATABASE_URL="your-production-db-url" node prisma/seed-production.js
```

## SSL and Security

### 1. SSL Certificates

- Vercel provides automatic SSL
- Render provides automatic SSL
- Supabase provides automatic SSL

### 2. Security Headers

Create `next.config.js`:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
```

### 3. Rate Limiting

Install rate limiting middleware:

```bash
npm install express-rate-limit
```

Create `middleware.ts`:

```typescript
import rateLimit from 'express-rate-limit';

export const config = {
  matcher: '/api/:path*',
};

export const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
});
```

## Monitoring and Logging

### 1. Vercel Analytics

1. In Vercel dashboard → Analytics
2. Enable analytics for your project
3. Monitor performance and usage

### 2. Render Monitoring

1. In Render dashboard → Metrics
2. Monitor CPU, memory, and response times
3. Set up alerts for thresholds

### 3. Supabase Logs

1. In Supabase dashboard → Logs
2. Monitor database queries and errors
3. Set up log exports

### 4. Custom Error Tracking

Create `lib/error-tracking.ts`:

```typescript
export class ErrorTracker {
  static track(error: Error, context?: any) {
    console.error('Application Error:', error, context);
    
    // Send to error tracking service (Sentry, etc.)
    if (process.env.NODE_ENV === 'production') {
      // Sentry.captureException(error, { extra: context });
    }
  }
}
```

## Performance Optimization

### 1. Frontend Optimization

```javascript
// next.config.js
const nextConfig = {
  compress: true,
  poweredByHeader: false,
  images: {
    domains: ['your-domain.com'],
    formats: ['image/webp', 'image/avif'],
  },
  experimental: {
    optimizeCss: true,
  },
};
```

### 2. Database Optimization

```sql
-- Add indexes for better performance
CREATE INDEX idx_player_club_id ON players(club_id);
CREATE INDEX idx_match_tournament_id ON matches(tournament_id);
CREATE INDEX idx_match_status ON matches(status);
CREATE INDEX idx_tournament_status ON tournaments(status);
```

### 3. Caching Strategy

```typescript
// lib/cache.ts
import { LRUCache } from 'lru-cache';

const cache = new LRUCache<string, any>({
  max: 500,
  ttl: 1000 * 60 * 5, // 5 minutes
});

export const cacheHelper = {
  get: (key: string) => cache.get(key),
  set: (key: string, value: any) => cache.set(key, value),
  del: (key: string) => cache.delete(key),
};
```

## Backup and Recovery

### 1. Database Backups

Supabase provides automatic backups:
- Daily backups retained for 30 days
- Point-in-time recovery for 7 days

Manual backup:
```bash
pg_dump "$DATABASE_URL" > backup.sql
```

### 2. Application Backup

```bash
# Backup source code
git archive --format=zip HEAD > application-backup.zip

# Backup environment variables
vercel env pull .env.production
```

## Scaling Considerations

### 1. Horizontal Scaling

- Vercel automatically scales frontend
- Render can scale backend instances
- Supabase can handle database load

### 2. CDN Configuration

```javascript
// next.config.js
const nextConfig = {
  assetPrefix: process.env.NODE_ENV === 'production' 
    ? 'https://cdn.your-domain.com' 
    : undefined,
};
```

### 3. Database Scaling

Monitor database performance and upgrade Supabase plan as needed:
- Free tier: 500MB database, 2GB bandwidth
- Pro tier: 8GB database, 250GB bandwidth
- Enterprise: Custom limits

## Testing Production

### 1. Health Check Endpoint

Create `pages/api/health.ts`:

```typescript
export default function handler(req, res) {
  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version,
  });
}
```

### 2. Load Testing

```bash
# Install artillery
npm install -g artillery

# Create test config
cat > load-test.yml << EOF
config:
  target: 'https://your-api-domain.com'
  phases:
    - duration: 60
      arrivalRate: 10
scenarios:
  - name: "API Health Check"
    requests:
      - get:
          url: "/api/health"
EOF

# Run load test
artillery run load-test.yml
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check DATABASE_URL format
   - Verify network connectivity
   - Check Supabase status

2. **Build Failures**
   - Check Node.js version compatibility
   - Verify all dependencies installed
   - Check build logs for specific errors

3. **Environment Variables**
   - Ensure all required variables set
   - Check for typos in variable names
   - Verify values are correctly escaped

4. **Performance Issues**
   - Monitor database query performance
   - Check for memory leaks
   - Analyze bundle size

### Debug Commands

```bash
# Check build locally
npm run build

# Test production build locally
npm start

# Check database connection
npx prisma db pull

# Verify environment variables
vercel env ls
```

## Maintenance

### Regular Tasks

1. **Weekly**
   - Check error logs
   - Monitor performance metrics
   - Review security updates

2. **Monthly**
   - Update dependencies
   - Review backup status
   - Clean up old data

3. **Quarterly**
   - Security audit
   - Performance optimization
   - Capacity planning

### Update Process

```bash
# Update dependencies
npm update

# Test updates locally
npm run build
npm test

# Deploy updates
git add .
git commit -m "Update dependencies"
git push origin main

# Deploy to production
vercel --prod
```

This deployment guide provides comprehensive instructions for deploying the XTHLETE Tournament Management System to production environments with proper security, monitoring, and maintenance procedures.