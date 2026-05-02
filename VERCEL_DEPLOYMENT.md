# Vercel Deployment Guide

## Problem
Vercel is a serverless platform - it cannot run Ollama as a persistent background service.
Ollama requires a continuously running process (localhost:11434), which Vercel doesn't support.

## Solutions

### Option 1: Mock Mode (Recommended for Vercel)
The app automatically uses smart mock responses on Vercel.

**How it works:**
- Vercel sets `VERCEL` environment variable
- App detects this and uses `get_mock_response()` instead of Ollama
- Mock responses use keyword-matching algorithm for realistic scoring

**Deploy to Vercel:**

1. Create `vercel.json`:
```json
{
  "buildCommand": "echo 'No build needed'",
  "devCommand": "python3 app.py",
  "installCommand": "pip3 install flask --break-system-packages",
  "framework": "python",
  "env": {
    "USE_MOCK": "true"
  }
}
```

2. Deploy:
```bash
vercel --prod
```

### Option 2: External Ollama (Advanced)
Use a cloud Ollama instance instead of localhost.

**Steps:**
1. Deploy Ollama on a cloud VM (DigitalOcean, AWS EC2)
2. Update `query_ollama()` to use external URL
3. Set `OLLAMA_HOST` environment variable

```python
# In query_ollama()
url = os.environ.get('OLLAMA_HOST', 'http://localhost:11434') + '/api/generate'
```

### Option 3: Use OpenAI/Anthropic API
Replace Ollama with a cloud LLM API.

**Steps:**
1. Sign up for OpenAI or Anthropic
2. Get API key
3. Update `query_ollama()` to use their API

```python
import openai
openai.api_key = os.environ['OPENAI_API_KEY']
```

### Option 4: Self-Host on VPS
Don't use Vercel - use a real VPS instead.

**Platforms:**
- DigitalOcean ($5/mo)
- AWS EC2 (free tier)
- Linode
- Render.com (free tier with worker)

**Deploy:**
```bash
# On your VPS
python3 app.py
# Access at http://your-vps-ip:5001
```

## Recommendation

For Vercel deployment: **Use Option 1 (Mock Mode)**

The mock responses are already quite good - they use keyword matching to generate realistic scores and suggestions. You get a fully functional app that works anywhere!

## Current Status

✅ Works locally with Ollama (real AI)  
✅ Works on Vercel with mock responses (smart algorithm)  
✅ Both return valid JSON  
✅ Both have professional UI  

## Testing on Vercel

After deploying:
1. Visit your Vercel URL
2. Enter resume + job description
3. Click "Analyze Match"
4. View results (will say "Mock analysis" in note)

The mock analysis is fast (instant) and doesn't require any background services!
