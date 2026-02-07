# Setup Guide

## Prerequisites

- Python 3.11+
- Git
- Ollama (for local content generation)

## Quick Start

1. **Clone and install:**
   ```bash
   git clone <repo-url> && cd organic-leadgen
   python -m venv .venv && source .venv/bin/activate
   pip install -e ".[dev]"
   ```

2. **Install Ollama and pull a model:**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ollama pull llama3.2
   ```

3. **Copy and fill environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Verify setup:**
   ```bash
   leadgen status
   ```

## Service Setup Checklist

### Blog (GitHub Pages + Hugo) - $0/mo
- [ ] Push repo to GitHub
- [ ] Enable GitHub Pages (Settings > Pages > Deploy from GitHub Actions)
- [ ] Configure custom domain (optional, ~$12/yr)

### Hashnode - $0/mo
- [ ] Create Hashnode account
- [ ] Generate API token (Settings > Developer)
- [ ] Create a publication and note the publication ID
- [ ] Add to `.env`: `HASHNODE_API_TOKEN`, `HASHNODE_PUBLICATION_ID`

### Dev.to - $0/mo
- [ ] Create Dev.to account
- [ ] Generate API key (Settings > Extensions)
- [ ] Add to `.env`: `DEVTO_API_KEY`

### Postiz - $0/mo (existing account)
- [ ] Log into your Postiz account
- [ ] Connect social channels (LinkedIn, X/Twitter, Facebook, Instagram, etc.)
- [ ] Generate API key (Settings > API Key)
- [ ] Add to `.env`: `POSTIZ_API_KEY`
- [ ] (Optional) If self-hosted, set `POSTIZ_BASE_URL` to your backend URL

### ConvertKit - $0/mo (free tier, 10K subscribers)
- [ ] Create ConvertKit account
- [ ] Create a form for email collection
- [ ] Generate API key and secret (Settings > Advanced)
- [ ] Add to `.env`: `CONVERTKIT_API_KEY`, `CONVERTKIT_API_SECRET`

### DataForSEO - $6/mo
- [ ] Create account at dataforseo.com
- [ ] Add $6 credit
- [ ] Add to `.env`: `DATAFORSEO_LOGIN`, `DATAFORSEO_PASSWORD`

### Tally (forms) - $0/mo
- [ ] Create Tally account
- [ ] Create lead capture form
- [ ] Embed in ROI calculator (update iframe src in index.html)

### Vercel (lead magnet hosting) - $0/mo
- [ ] Create Vercel account
- [ ] Deploy lead-magnets/ directory
- [ ] Configure custom subdomain (e.g., tools.yourdomain.com)

## Usage

### Generate a blog post:
```bash
leadgen generate --niche "restaurants" --topic "AI chatbots for reservations"
```

### Research keywords:
```bash
leadgen keywords --niche "restaurants" --max-difficulty 40
```

### Build and preview blog locally:
```bash
cd blog && hugo server -D
```

## Automated Schedule

GitHub Actions runs 3x/week (Mon/Wed/Fri at 9am UTC):
1. Generates a blog post targeting rotating niches
2. Commits to main branch
3. Triggers Hugo build + GitHub Pages deployment
4. (Future) Cross-posts to Hashnode and Dev.to
5. (Future) Schedules social posts via Postiz (LinkedIn, X, Facebook, Instagram, etc.)

## Expected Growth Rate

| Week | Blog Posts | Social Posts (5 platforms via Postiz) | Est. Organic Traffic | Est. Leads |
|------|-----------|--------------------------------------|---------------------|------------|
| 1    | 3         | 15                                   | 10-20               | 0-1        |
| 2    | 6         | 30                                   | 30-60               | 1-2        |
| 4    | 12        | 60                                   | 80-150              | 3-5        |
| 8    | 24        | 120                                  | 200-400             | 8-15       |
| 12   | 36        | 180                                  | 500-1000            | 15-30      |

*Traffic estimates assume 3 posts/week, low-competition keywords, proper SEO.*
*Lead estimates assume 2-3% conversion rate on organic traffic.*
