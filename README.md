# Organic Leadgen

Automated content and inbound lead generation system for non-tech businesses needing AI agents (restaurants, law firms, dental offices, HVAC, real estate, accounting firms).

The platform researches SEO keywords, generates blog posts and social media content using LLMs, publishes across multiple channels, distributes to social platforms, captures leads via email and lead magnets — all on autopilot for under $7/month.

## How It Works

```
Keyword Research (DataForSEO)
  → Content Generation (Ollama / Claude CLI)
    → Blog Publishing (Hugo → GitHub Pages)
      → Cross-Posting (Dev.to, Ghost/Hashnode)
        → Social Distribution (Postiz → 27+ platforms)
          → Lead Capture (Email + Lead Magnets)
            → Analytics & Feedback Loop
```

## Current Status

**This project is under active development.** The core scaffolding is built and tested, but the full pipeline is not yet wired end-to-end. Several external services still need configuration and live testing.

### What Works

- Content generation via Claude CLI (real blog posts, SEO-optimized)
- Hugo blog builds cleanly with PaperMod theme
- CLI commands: `status`, `generate`, `keywords`, `cron`
- 18/18 unit tests passing
- GitHub Actions workflows defined

### What Still Needs Work

- **Wire full pipeline** — cross-posting, social distribution, and email are coded but not chained into the publish flow
- **Content approval workflow** — currently auto-publishes with no human review
- **Web dashboard / GUI** — CLI only, no visual interface for content management
- **Analytics integration** — publishes content but can't measure results
- **A/B testing** — no variant generation or performance tracking
- **Live testing** — most integrations only tested via unit test mocks
- **External service configuration** — API keys needed for most services

## Tech Stack

### Core Tools (Open Source)

| Tool | GitHub Stars | License | Tech Stack | What It Does |
|---|---|---|---|---|
| [Hugo](https://github.com/gohugoio/hugo) | ~86.5k | Apache-2.0 | Go | Builds the static blog site from markdown |
| [PaperMod](https://github.com/adityatelange/hugo-PaperMod) | ~13.1k | MIT | Hugo templates, CSS/JS | Blog theme — clean, fast, SEO-friendly |
| [Ollama](https://github.com/ollama/ollama) | ~162k | MIT | Go, llama.cpp (C/C++) | Runs LLMs locally for free content generation |
| [Dev.to (Forem)](https://github.com/forem/forem) | ~22.6k | AGPL-3.0 | Ruby on Rails, Preact, PostgreSQL | Cross-post blog articles to dev community |
| [Postiz](https://github.com/gitroomhq/postiz-app) | ~26.5k | AGPL-3.0 | Next.js, NestJS, Prisma, PostgreSQL | Distribute content to 27+ social platforms |

### Services Under Consideration

The following proprietary services are currently integrated but may be replaced with open-source alternatives. Each alternative listed is free to self-host and has a permissive or copyleft license that allows commercial use.

#### Blog Cross-Posting: Hashnode → considering Ghost or WordPress

Hashnode is proprietary (free to use). We are evaluating open-source replacements:

| Tool | GitHub Stars | License | Free Self-Host | Commercial Use | Tech Stack | What It Does |
|---|---|---|---|---|---|---|
| Hashnode (current) | N/A | Proprietary | No | N/A | Node.js, React, GraphQL | Blog cross-posting platform |
| [Ghost](https://github.com/TryGhost/Ghost) | ~51.7k | MIT | Yes | Yes (unrestricted) | Node.js, Ember.js, SQLite/MySQL | Modern blogging with memberships & newsletters |
| [WordPress](https://github.com/WordPress/WordPress) | ~13k | GPLv2+ | Yes | Yes (unrestricted) | PHP, MySQL/MariaDB | Flexible CMS with massive plugin ecosystem |

#### Email Marketing: ConvertKit → considering open-source alternatives

ConvertKit/Kit is proprietary SaaS (free tier up to 10K subscribers). Open-source alternatives:

| Tool | GitHub Stars | License | Free Self-Host | Commercial Use | Tech Stack | What It Does |
|---|---|---|---|---|---|---|
| ConvertKit / Kit (current) | N/A | Proprietary | No | N/A | Ruby on Rails, React, MySQL | Email marketing — newsletters, automation |
| [Listmonk](https://github.com/knadh/listmonk) | ~18.9k | AGPL-3.0 | Yes | Yes (copyleft) | Go, PostgreSQL | High-performance newsletter manager (single binary) |
| [Mautic](https://github.com/mautic/mautic) | ~9.1k | GPL-3.0 | Yes | Yes (copyleft) | PHP, Symfony, MySQL | Full marketing automation platform |

#### SEO Keyword Research: DataForSEO → considering open-source alternatives

DataForSEO is a proprietary API ($6/month). Open-source alternatives:

| Tool | GitHub Stars | License | Free Self-Host | Commercial Use | Tech Stack | What It Does |
|---|---|---|---|---|---|---|
| DataForSEO (current) | N/A | Proprietary | No | N/A | REST API | Keyword research, search volume, SERP data |
| [SearXNG](https://github.com/searxng/searxng) | ~24.7k | AGPL-3.0 | Yes | Yes (copyleft) | Python | Meta search engine — scrape keyword suggestions for free |

#### Lead Capture Forms: Tally → considering open-source alternatives

Tally is a proprietary no-code form builder. Open-source alternatives:

| Tool | GitHub Stars | License | Free Self-Host | Commercial Use | Tech Stack | What It Does |
|---|---|---|---|---|---|---|
| Tally (current) | N/A | Proprietary | No | N/A | Not disclosed | No-code form builder |
| [Formbricks](https://github.com/formbricks/formbricks) | ~11.8k | AGPL-3.0 | Yes | Yes (copyleft) | TypeScript, Next.js, Prisma | Open-source forms & survey builder |
| [Heyform](https://github.com/heyform/heyform) | ~8.6k | AGPL-3.0 | Yes | Yes (copyleft) | Node.js, React, TypeScript | Conversational form builder |

### Analytics (Planned)

| Tool | GitHub Stars | License | Free Self-Host | Commercial Use | Tech Stack | What It Does |
|---|---|---|---|---|---|---|
| [Umami](https://github.com/umami-software/umami) | ~35.1k | MIT | Yes | Yes (unrestricted) | Next.js, TypeScript, PostgreSQL | Lightweight privacy-first web analytics |
| [Plausible](https://github.com/plausible/analytics) | ~24.2k | AGPL-3.0 | Yes | Yes (copyleft) | Elixir, Phoenix, ClickHouse | Privacy-first Google Analytics alternative |

## Project Architecture

```
src/leadgen/
  cli.py              # Click CLI — status, generate, publish, keywords, cron
  config.py           # Environment-based configuration
  pipeline.py         # Orchestrator — wires content generation + publishing
  content_generator.py # LLM content generation (Ollama / Claude CLI)
  publishers/
    hugo.py           # Publish to Hugo static blog
    hashnode.py       # Cross-post to Hashnode
    devto.py          # Cross-post to Dev.to
  distributors/
    postiz.py         # Social media distribution (27+ platforms)
  email/
    convertkit.py     # Email subscriber management
  seo/
    keywords.py       # DataForSEO keyword research
    content_calendar.py # Content planning & scheduling

blog/                 # Hugo blog with PaperMod theme
lead-magnets/
  roi-calculator/     # Static HTML/CSS/JS lead capture tool
.github/workflows/
  publish.yml         # Auto-generate content 3x/week
  deploy-blog.yml     # Deploy blog to GitHub Pages
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# 18 tests, all passing
# Uses pytest + pytest-asyncio (strict mode)
# HTTP clients mocked with MagicMock/AsyncMock
```

## Deployment

```bash
# Install the CLI
pip install -e .

# Check system status
leadgen status

# Generate a blog post
leadgen generate --niche "restaurants" --topic "AI chatbots for reservations"

# Publish (generate + push to Hugo blog)
leadgen publish --niche "restaurants" --topic "AI chatbots for reservations"

# Install cron job (auto-publish 3x/week)
leadgen cron --install

# Build the Hugo blog locally
cd blog && hugo serve
```

### Environment Variables

Create a `.env` file with the credentials for services you want to use:

```bash
# Content Generation
OLLAMA_HOST=http://localhost:11434

# Cross-Posting
HASHNODE_API_TOKEN=
DEVTO_API_KEY=

# Social Distribution
POSTIZ_API_KEY=
POSTIZ_API_URL=https://app.postiz.com/api/v1

# Email
CONVERTKIT_API_KEY=
CONVERTKIT_API_SECRET=
CONVERTKIT_FORM_ID=

# SEO
DATAFORSEO_LOGIN=
DATAFORSEO_PASSWORD=
```

### GitHub Actions

- **publish.yml** — Runs 3x/week (Mon, Wed, Fri at 9am UTC), generates and publishes a blog post automatically
- **deploy-blog.yml** — Deploys the Hugo blog to GitHub Pages on push to master

## Cost

| Service | Cost | Notes |
|---|---|---|
| Claude Code CLI | $0 | Existing subscription |
| GitHub Pages | $0 | Free static hosting |
| Postiz | $0 | Free / self-hosted |
| ConvertKit | $0 | Free tier (10K subscribers) |
| DataForSEO | ~$6/mo | Keyword research API |
| Domain | ~$1/mo | Optional |
| **Total** | **~$7/mo** | |

## License

All core tools are open source. Proprietary service integrations are being evaluated for replacement with open-source alternatives (see "Services Under Consideration" above).
