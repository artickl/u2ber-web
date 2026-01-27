# Environment Configuration Guide

## Quick Reference

### For Localhost Development (DEFAULT)

**backend/.env.local:**

```env
API_HOST=0.0.0.0
API_PORT=8000
API_BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
ENVIRONMENT=development
```

**frontend/.env.local:**

```env
VITE_API_BASE=http://localhost:8000
VITE_ENVIRONMENT=development
```

✅ Already set up by default - just copy `.env.example` to `.env.local`

---

### For Production (example.site)

**backend/.env.local or backend/.env (on server):**

```env
API_HOST=0.0.0.0
API_PORT=8000
API_BASE_URL=https://example.site/api
FRONTEND_URL=https://example.site
ENVIRONMENT=production
```

**frontend/.env.local or frontend/.env (on server):**

```env
VITE_API_BASE=https://example.site/api
VITE_ENVIRONMENT=production
# Add your Google Analytics tag for production tracking
VITE_GA_TAG=G-RTDKZSF9G7
```

**Note:** Google Analytics only loads when:
- `VITE_ENVIRONMENT=production`
- `VITE_GA_TAG` is set and not empty

This ensures analytics doesn't run during local development.

---

## Setup Instructions

### First Time Setup (One-Time)

```bash
# Backend
cd web/backend
cp .env.example .env.local

# Frontend  
cd web/frontend
cp .env.example .env.local
```

### For Production Deployment

When deploying to example.site:

```bash
# Copy production examples
cd web/backend
cp .env.production .env

cd web/frontend
cp .env.production .env
```

Then edit both `.env` files to match your actual domain and paths.

---

## How Environment Variables Are Used

### Backend (Python)

- Loaded automatically on startup via `python-dotenv`
- Used to configure CORS, API URLs, and download paths
- CORS automatically restricted to `FRONTEND_URL` in production

### Frontend (React/Vite)

- Vite automatically loads `.env` files with `VITE_` prefix
- `VITE_API_BASE` used for all API calls
- Available as `import.meta.env.VITE_API_BASE` in code

---

## No Code Changes Needed

✨ All configuration happens in `.env` files - no need to touch the code to switch between:

- `localhost:8000` ↔ `example.site/api`
- `localhost:5173` ↔ `example.site`
- Development ↔ Production

Just edit the `.env` file and restart!

---

## Important: Nginx/Reverse Proxy Setup

For production with example.site, you'll need a reverse proxy (Nginx/Apache):

```nginx
# Example Nginx config
server {
    server_name example.site;
    
    # API routes to backend
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Frontend to React app
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Then:

- Backend runs on `localhost:8000` internally
- Frontend runs on `localhost:5173` internally  
- Both accessible via `example.site` externally
- API accessible at `example.site/api`

---

## Troubleshooting

**Q: API calls failing with CORS error?**
A: Check `FRONTEND_URL` in backend `.env.local` matches where frontend is running

**Q: "Module not found: dotenv" error?**
A: Install requirements: `pip install -r requirements.txt`

**Q: Frontend still using old API URL?**
A: Make sure `.env.local` exists with `VITE_API_BASE`, then restart dev server

**Q: Variables not loading?**
A: Restart both services. Env files are only loaded on startup.
