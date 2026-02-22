# Deployment

## Production URL

This application is deployed on Railway.

> **URL will be available in Railway dashboard after first deploy**

## Deployment Setup

### Railway (Production)

1. Go to [https://railway.app](https://railway.app) and create a new project
2. Click **Deploy from GitHub repo** and select `Reg-Project`
3. Railway auto-detects `railway.toml` and the `Dockerfile`
4. Set the environment variable in Railway dashboard:
   - `OPENROUTER_API_KEY` → your OpenRouter API key
   - `OPENROUTER_MODEL` → `deepseek/deepseek-r1-0528:free`
5. Click **Deploy**

The `railway.toml` configures:
- **Builder:** Dockerfile
- **Health check:** `GET /health`
- **Restart policy:** on failure (max 3 retries)

### CI/CD (GitHub Actions)

On every push to `main`:
1. Tests run on Python 3.10 and 3.11
2. Docker build check (without model download)
3. If tests pass → Railway deploy hook is triggered automatically

To enable auto-deploy from CI:
1. In Railway dashboard → your service → **Settings** → **Deploy** → **Deploy Hook** → copy the URL
2. In GitHub → `Reg-Project` → **Settings** → **Secrets** → add `RAILWAY_DEPLOY_HOOK_URL`

### Environment Variables on Railway

| Variable | Value |
|----------|-------|
| `OPENROUTER_API_KEY` | Set manually in Railway dashboard (secret) |
| `OPENROUTER_MODEL` | `deepseek/deepseek-r1-0528:free` |
| `FLASK_DEBUG` | `false` |
