# GUI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a web dashboard so non-technical users can generate, preview, approve, and publish content without touching a terminal.

**Architecture:** FastAPI backend (reuses all existing async modules directly) + vanilla HTML/CSS/JS frontend with HTMX for interactivity. No JS framework, no build step. Served from the same VPS. Single `leadgen serve` command starts it.

**Tech Stack:** FastAPI, Jinja2 templates, HTMX, PicoCSS (classless responsive CSS), SQLite (for draft/post state tracking)

---

## Why This Stack

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| FastAPI + HTMX | Python-native, reuses async code, no build step, lightweight | Less flashy | **Chosen** |
| Streamlit | Fastest to build | Limited layout, reloads on interaction, not production-grade | Too limiting |
| Next.js | Polished UI | Adds Node.js, needs API layer, doubles complexity | Over-engineered |
| Flask | Simple | Not async, can't reuse existing async modules without wrapping | Bad fit |

---

## Database: SQLite for State

The CLI is stateless — it generates and publishes immediately. The GUI needs state:
- Drafts waiting for approval
- Published post history
- Social post variants
- Scheduled items

SQLite via `aiosqlite` — zero config, single file, async-compatible.

```sql
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    status TEXT NOT NULL DEFAULT 'draft',  -- draft | approved | published | rejected
    niche TEXT NOT NULL,
    topic TEXT NOT NULL,
    title TEXT,
    slug TEXT,
    meta_description TEXT,
    body TEXT,
    tags TEXT,                             -- JSON array
    hugo_path TEXT,                        -- set after Hugo publish
    hashnode_url TEXT,                     -- set after cross-post
    devto_url TEXT,                        -- set after cross-post
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    published_at TEXT
);

CREATE TABLE social_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL REFERENCES posts(id),
    platform TEXT NOT NULL,               -- linkedin | x | facebook | instagram | threads
    content TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft', -- draft | scheduled | posted
    scheduled_at TEXT,
    posted_at TEXT
);

CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

---

## Pages

### 1. Dashboard (`/`)
- System status (same as `leadgen status`)
- Stats: total posts, drafts pending, posts this week
- Last 5 published posts
- Next scheduled cron run
- Quick action buttons: "Generate New Post", "View Drafts"

### 2. Generate (`/generate`)
- Form: niche dropdown (6 niches), topic text input, model selector
- "Generate" button → shows spinner → displays draft preview
- Preview shows: title, meta description, body (rendered markdown), tags
- Buttons: "Approve & Publish", "Save as Draft", "Regenerate", "Reject"
- Publish flow: Hugo → optional Hashnode → optional Dev.to → generate social → optional Postiz

### 3. Posts (`/posts`)
- Table: title, niche, status (badge), date, actions
- Filter by status: all | draft | approved | published | rejected
- Click row → detail view with full content
- Detail view has: edit title/body, approve, publish, reject, delete
- Shows cross-post status (Hashnode URL, Dev.to URL)

### 4. Social (`/posts/{id}/social`)
- Shows blog post title + summary at top
- 5 platform cards (LinkedIn, X, Facebook, Instagram, Threads)
- Each card: editable text area with character count, preview, "Post Now" or "Schedule"
- "Generate All" button to auto-repurpose from blog content
- "Post All Now" button for one-click distribution via Postiz

### 5. Keywords (`/keywords`)
- Form: niche dropdown, max difficulty slider (0-100)
- Results table: keyword, search volume, difficulty (color-coded)
- "Add to Calendar" button per keyword
- Content calendar view (table: date, niche, keyword, post type)
- "Generate Post from Keyword" button → goes to Generate page pre-filled

### 6. Settings (`/settings`)
- Form for all config values (API keys masked, model selector)
- Save writes to `.env` file
- "Test Connection" buttons for each service (Postiz, ConvertKit, DataForSEO, Hashnode, Dev.to)
- Connection status indicators (green/red)

### 7. Analytics (`/analytics`) — Future
- Placeholder page with "Coming soon" message
- Will integrate Plausible/Umami when added
- Show: page views per post, top posts, lead conversion rate

---

## Tasks

### Task 1: Add FastAPI + dependencies

**Files:**
- Modify: `pyproject.toml`
- Create: `src/leadgen/web/__init__.py`
- Create: `src/leadgen/web/app.py`
- Create: `src/leadgen/web/database.py`

**Step 1: Add dependencies to pyproject.toml**

```toml
[project]
dependencies = [
    "click>=8.1",
    "httpx>=0.27",
    "python-dotenv>=1.0",
    "pyyaml>=6.0",
    "jinja2>=3.1",
    "fastapi>=0.115",
    "uvicorn>=0.34",
    "aiosqlite>=0.20",
    "python-multipart>=0.0.18",
]
```

**Step 2: Create database module**

`src/leadgen/web/database.py`:
```python
"""SQLite database for GUI state tracking."""

import aiosqlite
import json
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent.parent / "leadgen.db"

async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db

async def init_db():
    db = await get_db()
    await db.executescript("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT NOT NULL DEFAULT 'draft',
            niche TEXT NOT NULL,
            topic TEXT NOT NULL,
            title TEXT,
            slug TEXT,
            meta_description TEXT,
            body TEXT,
            tags TEXT,
            hugo_path TEXT,
            hashnode_url TEXT,
            devto_url TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            published_at TEXT
        );
        CREATE TABLE IF NOT EXISTS social_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL REFERENCES posts(id),
            platform TEXT NOT NULL,
            content TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'draft',
            scheduled_at TEXT,
            posted_at TEXT
        );
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
    """)
    await db.commit()
    await db.close()
```

**Step 3: Create FastAPI app skeleton**

`src/leadgen/web/app.py`:
```python
"""FastAPI web application for leadgen GUI."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from leadgen.web.database import init_db

TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="Leadgen Dashboard", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})
```

**Step 4: Add `serve` command to CLI**

Add to `src/leadgen/cli.py`:
```python
@main.command()
@click.option("--host", default="0.0.0.0", help="Bind host")
@click.option("--port", default=8000, help="Bind port")
def serve(host, port):
    """Start the web dashboard."""
    import uvicorn
    from leadgen.web.app import app
    uvicorn.run(app, host=host, port=port)
```

**Step 5: Install and verify**

```bash
pip install -e ".[dev]"
leadgen serve --help
```

Expected: Shows help with --host and --port options.

**Step 6: Commit**

```bash
git add pyproject.toml src/leadgen/web/ src/leadgen/cli.py
git commit -m "feat: add FastAPI web app skeleton with SQLite database"
```

---

### Task 2: Base template + static assets (PicoCSS + HTMX)

**Files:**
- Create: `src/leadgen/web/static/css/app.css`
- Create: `src/leadgen/web/templates/base.html`
- Create: `src/leadgen/web/templates/dashboard.html`

**Step 1: Create base template with PicoCSS + HTMX (CDN)**

`src/leadgen/web/templates/base.html`:
```html
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{% block title %}Leadgen{% endblock %} — Dashboard</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
    <link rel="stylesheet" href="/static/css/app.css">
    <script src="https://unpkg.com/htmx.org@2.0.4"></script>
</head>
<body>
    <nav class="container">
        <ul><li><strong>Leadgen</strong></li></ul>
        <ul>
            <li><a href="/">Dashboard</a></li>
            <li><a href="/generate">Generate</a></li>
            <li><a href="/posts">Posts</a></li>
            <li><a href="/keywords">Keywords</a></li>
            <li><a href="/settings">Settings</a></li>
        </ul>
    </nav>
    <main class="container">
        {% block content %}{% endblock %}
    </main>
    <footer class="container">
        <small>Leadgen v0.1 — Content + Inbound Lead Generation</small>
    </footer>
</body>
</html>
```

**Step 2: Create dashboard template**

`src/leadgen/web/templates/dashboard.html`:
```html
{% extends "base.html" %}
{% block title %}Dashboard{% endblock %}
{% block content %}
<h1>Dashboard</h1>

<div class="grid">
    <article>
        <header>Total Posts</header>
        <p id="total-posts" hx-get="/api/stats" hx-trigger="load" hx-target="#stats">
            Loading...
        </p>
    </article>
    <article>
        <header>Pending Drafts</header>
        <p>{{ drafts_count }}</p>
    </article>
    <article>
        <header>Published This Week</header>
        <p>{{ week_count }}</p>
    </article>
</div>

<h2>System Status</h2>
<div hx-get="/api/status" hx-trigger="load"></div>

<h2>Recent Posts</h2>
<div hx-get="/api/posts/recent" hx-trigger="load"></div>

<a href="/generate" role="button">Generate New Post</a>
{% endblock %}
```

**Step 3: Create minimal app.css**

```css
/* Status badges */
.badge { padding: 0.2em 0.6em; border-radius: 4px; font-size: 0.8em; }
.badge-draft { background: #fef3c7; color: #92400e; }
.badge-published { background: #d1fae5; color: #065f46; }
.badge-rejected { background: #fee2e2; color: #991b1b; }

/* Character counter */
.char-count { font-size: 0.8em; color: var(--muted-color); text-align: right; }
.char-count.over { color: #dc2626; }

/* Spinner for HTMX */
.htmx-indicator { display: none; }
.htmx-request .htmx-indicator { display: inline-block; }

/* Post preview */
.post-preview { border-left: 3px solid var(--primary); padding-left: 1em; }
```

**Step 4: Verify server starts and renders dashboard**

```bash
leadgen serve &
curl -s http://localhost:8000/ | head -5
kill %1
```

Expected: HTML response with "Leadgen" in output.

**Step 5: Commit**

```bash
git add src/leadgen/web/
git commit -m "feat: add base template with PicoCSS + HTMX and dashboard page"
```

---

### Task 3: API routes — status + stats + recent posts

**Files:**
- Create: `src/leadgen/web/routes/__init__.py`
- Create: `src/leadgen/web/routes/api.py`
- Modify: `src/leadgen/web/app.py` (include router)

**Step 1: Create API routes**

`src/leadgen/web/routes/api.py`:
```python
from fastapi import APIRouter
from leadgen.config import load_config
from leadgen.web.database import get_db

router = APIRouter(prefix="/api")

@router.get("/status")
async def status():
    config = load_config()
    return {
        "content_model": config.content_model,
        "hugo_blog_dir": config.hugo_blog_dir,
        "services": {
            "hashnode": bool(config.hashnode_api_token),
            "devto": bool(config.devto_api_key),
            "postiz": bool(config.postiz_api_key),
            "convertkit": bool(config.convertkit_api_key),
            "dataforseo": bool(config.dataforseo_login),
        },
    }

@router.get("/stats")
async def stats():
    db = await get_db()
    total = await db.execute("SELECT COUNT(*) FROM posts")
    drafts = await db.execute("SELECT COUNT(*) FROM posts WHERE status = 'draft'")
    week = await db.execute(
        "SELECT COUNT(*) FROM posts WHERE status = 'published' "
        "AND published_at > datetime('now', '-7 days')"
    )
    result = {
        "total": (await total.fetchone())[0],
        "drafts": (await drafts.fetchone())[0],
        "published_this_week": (await week.fetchone())[0],
    }
    await db.close()
    return result

@router.get("/posts/recent")
async def recent_posts():
    db = await get_db()
    cursor = await db.execute(
        "SELECT id, title, niche, status, created_at, published_at "
        "FROM posts ORDER BY created_at DESC LIMIT 10"
    )
    rows = await cursor.fetchall()
    await db.close()
    return [dict(row) for row in rows]
```

**Step 2: Wire router into app.py**

Add to `app.py`:
```python
from leadgen.web.routes.api import router as api_router
app.include_router(api_router)
```

**Step 3: Test endpoints**

```bash
leadgen serve &
curl -s http://localhost:8000/api/status | python3 -m json.tool
curl -s http://localhost:8000/api/stats | python3 -m json.tool
kill %1
```

**Step 4: Commit**

```bash
git add src/leadgen/web/routes/
git commit -m "feat: add API routes for status, stats, and recent posts"
```

---

### Task 4: Generate page — form + preview + save draft

**Files:**
- Create: `src/leadgen/web/templates/generate.html`
- Create: `src/leadgen/web/routes/generate.py`
- Modify: `src/leadgen/web/app.py` (include router)

**Step 1: Create generate page template**

Form with niche dropdown, topic input. HTMX POST to `/api/generate` returns
rendered preview. Preview has "Save as Draft" and "Approve & Publish" buttons.

**Step 2: Create generate API route**

`src/leadgen/web/routes/generate.py`:
```python
@router.post("/api/generate")
async def generate_post(niche: str, topic: str):
    config = load_config()
    generator = ContentGenerator(model=config.content_model)
    post_data = await generator.generate_blog_post(niche=niche, topic=topic)

    # Save as draft in DB
    db = await get_db()
    cursor = await db.execute(
        "INSERT INTO posts (status, niche, topic, title, slug, meta_description, body, tags) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ("draft", niche, topic, post_data["title"], post_data["slug"],
         post_data["meta_description"], post_data["body"],
         json.dumps(post_data.get("tags", []))),
    )
    post_id = cursor.lastrowid
    await db.commit()
    await db.close()

    return {"id": post_id, **post_data}
```

**Step 3: Add approve + publish endpoint**

```python
@router.post("/api/posts/{post_id}/publish")
async def publish_post(post_id: int):
    db = await get_db()
    row = await (await db.execute("SELECT * FROM posts WHERE id = ?", (post_id,))).fetchone()
    post_data = dict(row)

    # Publish to Hugo
    config = load_config()
    publisher = HugoPublisher(blog_dir=config.hugo_blog_dir)
    hugo_path = publisher.publish({
        "title": post_data["title"],
        "slug": post_data["slug"],
        "meta_description": post_data["meta_description"],
        "body": post_data["body"],
        "tags": json.loads(post_data["tags"]),
    })

    # Update DB
    await db.execute(
        "UPDATE posts SET status = 'published', hugo_path = ?, published_at = datetime('now') WHERE id = ?",
        (str(hugo_path), post_id),
    )
    await db.commit()
    await db.close()

    return {"status": "published", "hugo_path": str(hugo_path)}
```

**Step 4: Test generate flow**

```bash
leadgen serve &
# Generate via API
curl -s -X POST "http://localhost:8000/api/generate?niche=restaurants&topic=AI+reservations"
# Check draft in DB
curl -s http://localhost:8000/api/stats
kill %1
```

**Step 5: Commit**

```bash
git add src/leadgen/web/
git commit -m "feat: add generate page with preview, draft save, and publish"
```

---

### Task 5: Posts list page — view, approve, reject, delete

**Files:**
- Create: `src/leadgen/web/templates/posts.html`
- Create: `src/leadgen/web/templates/post_detail.html`
- Create: `src/leadgen/web/routes/posts.py`

**Step 1: Posts list page**

Table with: title, niche, status badge, date, action buttons.
Filter tabs: All | Drafts | Published | Rejected.
HTMX-powered filtering without page reload.

**Step 2: Post detail page**

Shows full rendered content. Editable title and body fields.
Action buttons: Approve, Publish, Reject, Delete.
Shows cross-post status (Hashnode URL, Dev.to URL) if published.

**Step 3: API routes for post management**

```python
@router.post("/api/posts/{post_id}/approve")
@router.post("/api/posts/{post_id}/reject")
@router.delete("/api/posts/{post_id}")
@router.put("/api/posts/{post_id}")  # edit title/body
```

**Step 4: Commit**

```bash
git add src/leadgen/web/
git commit -m "feat: add posts list and detail pages with approve/reject/delete"
```

---

### Task 6: Social repurposing page

**Files:**
- Create: `src/leadgen/web/templates/social.html`
- Create: `src/leadgen/web/routes/social.py`

**Step 1: Social page for a post**

At `/posts/{id}/social`. Shows blog post title at top.
5 platform cards (LinkedIn, X, Facebook, Instagram, Threads).
Each card has: editable textarea, character count, platform icon.
"Generate All" button calls `repurpose_to_social()` and fills all cards.
"Post Now" per-card and "Post All" buttons.

**Step 2: API routes**

```python
@router.post("/api/posts/{post_id}/social/generate")
async def generate_social(post_id: int):
    # Calls ContentGenerator.repurpose_to_social()
    # Saves to social_posts table
    ...

@router.post("/api/social/{social_id}/post")
async def post_social(social_id: int):
    # Calls PostizDistributor.post_now()
    ...

@router.post("/api/posts/{post_id}/social/post-all")
async def post_all_social(post_id: int):
    # Posts all social variants via Postiz
    ...
```

**Step 3: Commit**

```bash
git add src/leadgen/web/
git commit -m "feat: add social repurposing page with per-platform editing and posting"
```

---

### Task 7: Keywords + content calendar page

**Files:**
- Create: `src/leadgen/web/templates/keywords.html`
- Create: `src/leadgen/web/routes/keywords.py`

**Step 1: Keywords research form**

Niche dropdown + max difficulty slider. Results table with keyword, volume,
difficulty (color-coded green/yellow/red). "Generate Post" button per keyword
links to `/generate?niche=X&topic=KEYWORD`.

**Step 2: Content calendar view**

Table showing: date, niche, keyword, post type.
Generated from `content_calendar.generate_calendar()`.
"Generate Post" button per entry.

**Step 3: Commit**

```bash
git add src/leadgen/web/
git commit -m "feat: add keywords research and content calendar pages"
```

---

### Task 8: Settings page — API keys + connection tests

**Files:**
- Create: `src/leadgen/web/templates/settings.html`
- Create: `src/leadgen/web/routes/settings.py`

**Step 1: Settings form**

All config fields as inputs. API keys shown masked (type=password).
Model selector dropdown (sonnet, haiku, opus).
Save button writes to `.env` file.

**Step 2: Connection test endpoints**

```python
@router.post("/api/settings/test/{service}")
async def test_connection(service: str):
    # service: postiz | convertkit | dataforseo | hashnode | devto
    # Returns {"ok": True/False, "message": "..."}
```

Tests:
- Postiz: `PostizDistributor.check_connection()`
- ConvertKit: `ConvertKitClient.list_subscribers()` (catches auth error)
- DataForSEO: `KeywordResearcher.get_suggestions("test")` (catches auth error)
- Hashnode: Simple GraphQL query
- Dev.to: GET `https://dev.to/api/articles/me` with key

**Step 3: Commit**

```bash
git add src/leadgen/web/
git commit -m "feat: add settings page with API key management and connection tests"
```

---

### Task 9: Wire full pipeline — cross-post + distribute on publish

**Files:**
- Modify: `src/leadgen/pipeline.py`
- Modify: `src/leadgen/web/routes/generate.py`

**Step 1: Extend pipeline to optionally cross-post and distribute**

```python
class LeadgenPipeline:
    def __init__(self, config: Config):
        self.config = config
        self.generator = ContentGenerator(model=config.content_model)
        self.hugo_publisher = HugoPublisher(blog_dir=config.hugo_blog_dir)

    async def generate_and_publish(self, niche, topic, cross_post=True, distribute=True):
        post_data = await self.generator.generate_blog_post(niche, topic)
        local_path = self.hugo_publisher.publish(post_data)

        result = {"title": post_data["title"], "local_path": local_path}

        if cross_post and self.config.hashnode_api_token:
            hashnode = HashnodePublisher(self.config.hashnode_api_token, self.config.hashnode_publication_id)
            result["hashnode"] = await hashnode.publish(post_data)

        if cross_post and self.config.devto_api_key:
            devto = DevtoPublisher(self.config.devto_api_key)
            result["devto"] = await devto.publish(post_data)

        if distribute and self.config.postiz_api_key:
            social = await self.generator.repurpose_to_social(post_data["title"], post_data["body"])
            postiz = PostizDistributor(self.config.postiz_api_key, self.config.postiz_base_url)
            integrations = await postiz.get_integrations()
            # Post to each configured platform
            for integration in integrations:
                platform = integration["id"]
                if platform in social:
                    await postiz.post_now(integration["id"], platform, social[platform])
            result["social"] = social

        return result
```

**Step 2: Update tests**

```bash
pytest tests/ -v
```

**Step 3: Commit**

```bash
git add src/leadgen/pipeline.py src/leadgen/web/ tests/
git commit -m "feat: wire full pipeline with optional cross-posting and social distribution"
```

---

### Task 10: Tests for web routes

**Files:**
- Create: `tests/test_web_api.py`
- Create: `tests/test_web_generate.py`

**Step 1: Test API endpoints**

Use FastAPI TestClient:
```python
from fastapi.testclient import TestClient
from leadgen.web.app import app

client = TestClient(app)

def test_dashboard():
    response = client.get("/")
    assert response.status_code == 200

def test_api_status():
    response = client.get("/api/status")
    assert response.status_code == 200
    assert "content_model" in response.json()

def test_api_stats():
    response = client.get("/api/stats")
    assert response.status_code == 200
    assert "total" in response.json()
```

**Step 2: Test generate flow with mocked Claude CLI**

```python
async def test_generate_creates_draft():
    # Mock ContentGenerator._call_claude
    # POST /api/generate
    # Assert draft appears in /api/stats
    ...
```

**Step 3: Commit**

```bash
git add tests/
git commit -m "test: add web API and generate flow tests"
```

---

### Task 11: Production readiness

**Files:**
- Modify: `src/leadgen/cli.py` (add --workers flag)
- Create: `src/leadgen/web/auth.py` (basic auth)
- Modify: `.github/workflows/deploy-blog.yml` (optional)

**Step 1: Add basic auth**

Simple username/password from env vars (`DASHBOARD_USER`, `DASHBOARD_PASS`).
Middleware that returns 401 if not authenticated. No auth = no restriction (local dev).

```python
# Only enabled if DASHBOARD_USER is set in .env
DASHBOARD_USER=admin
DASHBOARD_PASS=changeme
```

**Step 2: Add systemd service file (optional)**

```ini
# /etc/systemd/system/leadgen-web.service
[Unit]
Description=Leadgen Web Dashboard
After=network.target

[Service]
User=node
WorkingDirectory=/home/node/git/organic_leadgen
ExecStart=/home/node/.local/bin/leadgen serve --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**Step 3: Update docs/SETUP.md**

Add GUI section:
```
## Web Dashboard

Start the dashboard:
  leadgen serve

Access at http://localhost:8000

For production, set auth in .env:
  DASHBOARD_USER=admin
  DASHBOARD_PASS=your-secure-password
```

**Step 4: Commit**

```bash
git add src/leadgen/ docs/
git commit -m "feat: add basic auth and production deployment config"
```

---

## Task Summary

| Task | Description | Depends On |
|------|-------------|------------|
| 1 | FastAPI skeleton + SQLite database + `leadgen serve` | — |
| 2 | Base template (PicoCSS + HTMX) + dashboard page | 1 |
| 3 | API routes: status, stats, recent posts | 1, 2 |
| 4 | Generate page: form → preview → save draft → publish | 3 |
| 5 | Posts list: view, approve, reject, delete | 3 |
| 6 | Social repurposing: per-platform editing + Postiz posting | 4, 5 |
| 7 | Keywords research + content calendar | 3 |
| 8 | Settings page: API keys + connection tests | 3 |
| 9 | Wire full pipeline: cross-post + distribute on publish | 4, 6 |
| 10 | Tests for web routes | 1-9 |
| 11 | Production: basic auth + systemd + docs | 1-10 |

**Estimated new dependencies:** fastapi, uvicorn, aiosqlite, python-multipart
**Estimated new files:** ~20 (routes, templates, static)
**No changes to existing working modules** — GUI wraps them via their public APIs.
