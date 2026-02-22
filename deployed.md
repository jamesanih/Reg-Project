# Deployment

## Production URL

This application is deployed on Render:

> **https://acme-policy-rag.onrender.com**

## Deployment Setup

### Render (Production)

1. Go to [https://render.com](https://render.com) and connect your GitHub account
2. Click **New > Web Service** and select the `Reg-Project` repository
3. Render will auto-detect `render.yaml` and pre-fill the settings
4. Set the environment variable:
   - `OPENROUTER_API_KEY` → your OpenRouter API key
5. Click **Deploy**

The `render.yaml` in this repo configures:
- **Runtime:** Python 3.11
- **Build:** `pip install -r requirements.txt`
- **Start:** `gunicorn run:app --workers 1 --bind 0.0.0.0:$PORT --timeout 300`
- **Health check:** `GET /health`

### CI/CD (GitHub Actions)

On every push to `main`:
1. Tests run on Python 3.10 and 3.11
2. Build check and lint run
3. If all pass → Render deploy hook is triggered automatically

To enable auto-deploy from CI:
1. In Render dashboard → your service → **Settings** → **Deploy Hook** → copy the URL
2. In GitHub repo → **Settings** → **Secrets** → add `RENDER_DEPLOY_HOOK_URL`

### Environment Variables on Render

| Variable | Value |
|----------|-------|
| `OPENROUTER_API_KEY` | Set manually in Render dashboard (secret) |
| `OPENROUTER_MODEL` | `deepseek/deepseek-r1-0528:free` |
| `FLASK_DEBUG` | `false` |
