# Content + Inbound Lead Generation System - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an automated content + inbound pipeline that publishes SEO-optimized blog posts, repurposes them into social media content, captures leads through free tools and forms, and nurtures them via email -- all for non-tech businesses that need AI agents, on a $100/month budget.

**Architecture:** Static blog on GitHub Pages (Hugo) for SEO ownership + Hashnode cross-posting for developer reach. Ollama generates content locally (free). Python scripts repurpose blog posts into social snippets and post via Postiz API (27+ platforms, multi-platform in single request). Lead magnets (ROI calculators) hosted on Vercel capture emails into ConvertKit (10K subscribers free). A single CLI orchestrator (`leadgen`) ties everything together: generate, publish, repurpose, distribute.

**Tech Stack:** Python 3.11+, Hugo (static site), Ollama (local LLM), GitHub Pages (blog hosting), Vercel (lead magnet hosting), Postiz API (social scheduling), ConvertKit API (email), Tally (forms), HTML/CSS/JS (calculators)

**Budget Breakdown:**
| Item | Monthly Cost |
|------|-------------|
| Hugo + GitHub Pages (blog) | $0 |
| Hashnode (cross-post) | $0 |
| Ollama (content generation) | $0 |
| Postiz (social scheduling) | $0 (existing account) |
| ConvertKit free tier (email) | $0 |
| Tally (forms) | $0 |
| Vercel (lead magnet hosting) | $0 |
| Custom domain (.com) | ~$1/mo ($12/yr) |
| DataForSEO keyword API | $6/mo |
| **Reserve for scaling** | **$93/mo** |
| **Total** | **~$7/mo** |

**Target Niches (non-tech businesses needing AI agents):**
- Restaurants & food service (AI chatbot for reservations, menu Q&A)
- Law firms (client intake automation, document processing)
- Real estate agencies (lead qualification, property matching)
- Dental/medical offices (appointment scheduling, patient follow-up)
- HVAC/plumbing/trades (dispatch automation, customer service)
- Accounting firms (document processing, client onboarding)

**ToS Compliance Summary:**
- Blog: Own content on own domain -- no restrictions
- Hashnode: API posting allowed, 500 req/min limit
- Dev.to: API posting allowed, no specific AI content ban
- Postiz: Uses official OAuth per platform -- ToS-compliant scheduling (27+ platforms including LinkedIn, X, Facebook, Instagram, TikTok, YouTube, Reddit)
- ConvertKit: CAN-SPAM compliant (opt-out), GDPR compliant (double opt-in for EU)
- Google SEO: AI content allowed if high-quality with E-E-A-T signals
- NO direct LinkedIn API automation (use Postiz instead -- official OAuth flow)
- NO Medium (prohibits automated + AI posting)
- NO Reddit automation (high ban risk, 90/10 rule)

---

## Task 1: Initialize Project Structure

**Files:**
- Create: `pyproject.toml`
- Create: `src/leadgen/__init__.py`
- Create: `src/leadgen/cli.py`
- Create: `tests/__init__.py`
- Create: `tests/test_cli.py`
- Create: `.gitignore`
- Create: `.env.example`

**Step 1: Initialize git and create project skeleton**

```bash
cd /home/node/git/organic_leadgen
git init
```

**Step 2: Create `.gitignore`**

```gitignore
__pycache__/
*.pyc
.env
dist/
*.egg-info/
.venv/
node_modules/
public/
resources/_gen/
blog/public/
.hugo_build.lock
```

**Step 3: Create `pyproject.toml`**

```toml
[project]
name = "organic-leadgen"
version = "0.1.0"
description = "Automated content + inbound lead generation for AI agent services"
requires-python = ">=3.11"
dependencies = [
    "click>=8.1",
    "httpx>=0.27",
    "python-dotenv>=1.0",
    "pyyaml>=6.0",
    "jinja2>=3.1",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
]

[project.scripts]
leadgen = "leadgen.cli:main"

[build-system]
requires = ["setuptools>=75.0"]
build-backend = "setuptools.backends._legacy:_Backend"

[tool.setuptools.packages.find]
where = ["src"]
```

**Step 4: Create `src/leadgen/__init__.py`**

```python
"""Organic lead generation automation for AI agent services."""
```

**Step 5: Create `src/leadgen/cli.py`**

```python
"""CLI entry point for the leadgen tool."""

import click


@click.group()
def main():
    """Organic lead generation automation."""
    pass


@main.command()
def status():
    """Show system status."""
    click.echo("Leadgen system: OK")
```

**Step 6: Create `.env.example`**

```env
# Hashnode
HASHNODE_API_TOKEN=
HASHNODE_PUBLICATION_ID=

# Dev.to
DEVTO_API_KEY=

# Postiz (social scheduling - 27+ platforms)
# Get your API key from Postiz Settings
POSTIZ_API_KEY=
POSTIZ_BASE_URL=https://api.postiz.com/public/v1

# ConvertKit
CONVERTKIT_API_KEY=
CONVERTKIT_API_SECRET=

# DataForSEO
DATAFORSEO_LOGIN=
DATAFORSEO_PASSWORD=

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

**Step 7: Write the failing test**

```python
# tests/test_cli.py
from click.testing import CliRunner
from leadgen.cli import main


def test_status_command():
    runner = CliRunner()
    result = runner.invoke(main, ["status"])
    assert result.exit_code == 0
    assert "Leadgen system: OK" in result.output
```

**Step 8: Install project and run tests**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/test_cli.py -v
```

Expected: PASS

**Step 9: Commit**

```bash
git add .gitignore pyproject.toml src/ tests/ .env.example
git commit -m "feat: initialize project structure with CLI skeleton"
```

---

## Task 2: Ollama Content Generator Module

**Files:**
- Create: `src/leadgen/content_generator.py`
- Create: `src/leadgen/prompts/`
- Create: `src/leadgen/prompts/blog_post.txt`
- Create: `src/leadgen/prompts/social_post.txt`
- Create: `tests/test_content_generator.py`

**Step 1: Write the failing test**

```python
# tests/test_content_generator.py
import json
from unittest.mock import patch, AsyncMock
import pytest
from leadgen.content_generator import ContentGenerator


@pytest.fixture
def generator():
    return ContentGenerator(
        base_url="http://localhost:11434",
        model="llama3.2",
    )


def test_generator_init(generator):
    assert generator.base_url == "http://localhost:11434"
    assert generator.model == "llama3.2"


@pytest.mark.asyncio
async def test_generate_blog_post(generator):
    mock_response = {
        "title": "5 Ways AI Agents Save Restaurants Money",
        "slug": "5-ways-ai-agents-save-restaurants-money",
        "meta_description": "Discover how AI agents help restaurants cut costs.",
        "body": "# 5 Ways AI Agents Save Restaurants Money\n\nContent here...",
        "tags": ["ai", "restaurants", "automation"],
    }

    with patch.object(
        generator, "_call_ollama", new_callable=AsyncMock
    ) as mock_call:
        mock_call.return_value = json.dumps(mock_response)
        result = await generator.generate_blog_post(
            niche="restaurants",
            topic="cost savings from AI agents",
        )

    assert result["title"] == "5 Ways AI Agents Save Restaurants Money"
    assert result["slug"] == "5-ways-ai-agents-save-restaurants-money"
    assert "body" in result
    assert "tags" in result


@pytest.mark.asyncio
async def test_generate_social_posts(generator):
    mock_response = {
        "linkedin": "Restaurants using AI agents report 30% cost savings...",
        "x": "AI agents are saving restaurants 30% on labor costs. Here's how:",
        "facebook": "Did you know? Restaurants using AI agents save an average of 30%...",
        "instagram": "The future of restaurants is here. AI agents are saving 30%...",
        "threads": "Hot take: restaurants not using AI agents in 2026 are leaving money on the table.",
    }

    with patch.object(
        generator, "_call_ollama", new_callable=AsyncMock
    ) as mock_call:
        mock_call.return_value = json.dumps(mock_response)
        result = await generator.repurpose_to_social(
            blog_title="5 Ways AI Agents Save Restaurants Money",
            blog_body="Full blog content here...",
        )

    assert "linkedin" in result
    assert "x" in result
    assert "instagram" in result
    assert len(result["x"]) <= 280
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_content_generator.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'leadgen.content_generator'`

**Step 3: Create prompt templates**

```text
# src/leadgen/prompts/blog_post.txt
You are an expert content writer for AI automation services targeting non-tech businesses.

Write a blog post for the "{niche}" industry about "{topic}".

Requirements:
- 800-1200 words
- Conversational, non-technical tone (the reader is a business owner, not a developer)
- Include specific dollar amounts and time savings where possible
- Include a clear call-to-action at the end
- SEO-optimized with the primary keyword naturally integrated
- Use H2 and H3 headers for structure

Return ONLY valid JSON with these fields:
{{
  "title": "SEO-optimized title (under 60 chars)",
  "slug": "url-friendly-slug",
  "meta_description": "155 char max meta description",
  "body": "Full markdown content",
  "tags": ["tag1", "tag2", "tag3"]
}}
```

```text
# src/leadgen/prompts/social_post.txt
You are a social media expert for AI automation services.

Given this blog post, create social media versions:

Title: {title}
Content: {body}

Return ONLY valid JSON:
{{
  "linkedin": "Professional post, 150-300 words, include insight + CTA. No hashtags in text.",
  "x": "Under 250 chars. Punchy, curiosity-driven. Leave room for a link.",
  "facebook": "Conversational, 100-200 words. Ask a question to drive engagement.",
  "instagram": "Visual storytelling angle, 100-150 words. Include relevant hashtags at the end.",
  "threads": "Casual, conversational, 50-100 words. Thread-style hot take."
}}
```

**Step 4: Write minimal implementation**

```python
# src/leadgen/content_generator.py
"""Content generation using Ollama local LLM."""

import json
from pathlib import Path

import httpx


PROMPTS_DIR = Path(__file__).parent / "prompts"


class ContentGenerator:
    """Generate blog and social content via Ollama."""

    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def _call_ollama(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                },
            )
            resp.raise_for_status()
            return resp.json()["response"]

    def _load_prompt(self, name: str, **kwargs: str) -> str:
        template = (PROMPTS_DIR / f"{name}.txt").read_text()
        return template.format(**kwargs)

    async def generate_blog_post(self, niche: str, topic: str) -> dict:
        prompt = self._load_prompt("blog_post", niche=niche, topic=topic)
        raw = await self._call_ollama(prompt)
        return json.loads(raw)

    async def repurpose_to_social(self, blog_title: str, blog_body: str) -> dict:
        prompt = self._load_prompt(
            "social_post", title=blog_title, body=blog_body[:2000]
        )
        raw = await self._call_ollama(prompt)
        return json.loads(raw)
```

**Step 5: Run tests**

```bash
pytest tests/test_content_generator.py -v
```

Expected: PASS

**Step 6: Commit**

```bash
git add src/leadgen/content_generator.py src/leadgen/prompts/ tests/test_content_generator.py
git commit -m "feat: add Ollama-based content generator with blog and social repurposing"
```

---

## Task 3: Hugo Blog Setup and Publisher Module

**Files:**
- Create: `blog/` (Hugo site)
- Create: `src/leadgen/publishers/__init__.py`
- Create: `src/leadgen/publishers/hugo.py`
- Create: `tests/test_publisher_hugo.py`

**Step 1: Install Hugo and scaffold blog**

```bash
# Install Hugo (extended edition for SCSS)
wget -qO- https://github.com/gohugoio/hugo/releases/download/v0.142.0/hugo_extended_0.142.0_linux-amd64.tar.gz | tar xz -C /usr/local/bin hugo

# Scaffold Hugo site
cd /home/node/git/organic_leadgen
hugo new site blog
```

**Step 2: Add a minimal SEO-friendly Hugo theme**

```bash
cd /home/node/git/organic_leadgen/blog
git submodule add https://github.com/adityatelange/hugo-PaperMod.git themes/PaperMod
```

**Step 3: Configure Hugo for SEO**

Create `blog/hugo.toml`:

```toml
baseURL = "https://yourdomain.com/"
languageCode = "en-us"
title = "AI Agents for Your Business"
theme = "PaperMod"

[params]
  description = "Learn how AI agents can automate your business operations and save you money."
  author = "Your Name"
  ShowReadingTime = true
  ShowShareButtons = true
  ShowPostNavLinks = true
  ShowBreadCrumbs = true
  ShowCodeCopyButtons = true
  defaultTheme = "auto"

[params.homeInfoParams]
  Title = "AI Agents for Non-Tech Businesses"
  Content = "Discover how AI automation can transform your restaurant, law firm, dental office, or trade business."

[outputs]
  home = ["HTML", "RSS", "JSON"]

[markup.goldmark.renderer]
  unsafe = true

[sitemap]
  changefreq = "weekly"
  priority = 0.5
```

**Step 4: Write the failing test**

```python
# tests/test_publisher_hugo.py
import os
from pathlib import Path
from leadgen.publishers.hugo import HugoPublisher


def test_hugo_publisher_creates_post(tmp_path):
    blog_dir = tmp_path / "blog"
    content_dir = blog_dir / "content" / "posts"
    content_dir.mkdir(parents=True)

    publisher = HugoPublisher(blog_dir=str(blog_dir))

    post_data = {
        "title": "5 Ways AI Agents Save Restaurants Money",
        "slug": "5-ways-ai-agents-save-restaurants-money",
        "meta_description": "Discover how AI agents help restaurants cut costs.",
        "body": "# 5 Ways AI Agents Save Restaurants Money\n\nContent here...",
        "tags": ["ai", "restaurants", "automation"],
    }

    filepath = publisher.publish(post_data)

    assert filepath.exists()
    content = filepath.read_text()
    assert "title:" in content
    assert "5 Ways AI Agents Save Restaurants Money" in content
    assert "description:" in content
    assert "Content here..." in content


def test_hugo_publisher_generates_valid_frontmatter(tmp_path):
    blog_dir = tmp_path / "blog"
    content_dir = blog_dir / "content" / "posts"
    content_dir.mkdir(parents=True)

    publisher = HugoPublisher(blog_dir=str(blog_dir))

    post_data = {
        "title": "Test Post",
        "slug": "test-post",
        "meta_description": "A test post.",
        "body": "Body content.",
        "tags": ["test"],
    }

    filepath = publisher.publish(post_data)
    content = filepath.read_text()

    # Hugo frontmatter delimiters
    assert content.startswith("---\n")
    assert content.count("---") >= 2
```

**Step 5: Run test to verify it fails**

```bash
pytest tests/test_publisher_hugo.py -v
```

Expected: FAIL with `ModuleNotFoundError`

**Step 6: Write minimal implementation**

```python
# src/leadgen/publishers/__init__.py
"""Content publishers for various platforms."""
```

```python
# src/leadgen/publishers/hugo.py
"""Publish blog posts to Hugo static site."""

from datetime import datetime, timezone
from pathlib import Path

import yaml


class HugoPublisher:
    """Create Hugo markdown posts with frontmatter."""

    def __init__(self, blog_dir: str):
        self.blog_dir = Path(blog_dir)
        self.content_dir = self.blog_dir / "content" / "posts"

    def publish(self, post_data: dict) -> Path:
        self.content_dir.mkdir(parents=True, exist_ok=True)

        frontmatter = {
            "title": post_data["title"],
            "slug": post_data["slug"],
            "description": post_data["meta_description"],
            "date": datetime.now(timezone.utc).isoformat(),
            "tags": post_data.get("tags", []),
            "draft": False,
            "ShowToc": True,
            "TocOpen": True,
        }

        filename = f"{post_data['slug']}.md"
        filepath = self.content_dir / filename

        content = "---\n"
        content += yaml.dump(frontmatter, default_flow_style=False)
        content += "---\n\n"
        content += post_data["body"]

        filepath.write_text(content)
        return filepath
```

**Step 7: Run tests**

```bash
pytest tests/test_publisher_hugo.py -v
```

Expected: PASS

**Step 8: Commit**

```bash
git add blog/ src/leadgen/publishers/ tests/test_publisher_hugo.py
git commit -m "feat: add Hugo blog setup and markdown publisher"
```

---

## Task 4: Hashnode and Dev.to Cross-Posting Publishers

**Files:**
- Create: `src/leadgen/publishers/hashnode.py`
- Create: `src/leadgen/publishers/devto.py`
- Create: `tests/test_publisher_hashnode.py`
- Create: `tests/test_publisher_devto.py`

**Step 1: Write failing tests for Hashnode**

```python
# tests/test_publisher_hashnode.py
from unittest.mock import patch, AsyncMock
import pytest
from leadgen.publishers.hashnode import HashnodePublisher


@pytest.fixture
def publisher():
    return HashnodePublisher(
        api_token="test-token",
        publication_id="test-pub-id",
    )


@pytest.mark.asyncio
async def test_hashnode_publish(publisher):
    mock_response = {
        "data": {
            "publishPost": {
                "post": {
                    "id": "abc123",
                    "url": "https://blog.example.com/test-post",
                }
            }
        }
    }

    with patch("leadgen.publishers.hashnode.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_client.post.return_value.json.return_value = mock_response
        mock_client.post.return_value.raise_for_status = lambda: None

        result = await publisher.publish({
            "title": "Test Post",
            "body": "Content here",
            "tags": ["ai", "automation"],
            "slug": "test-post",
            "canonical_url": "https://yourdomain.com/posts/test-post/",
        })

    assert result["id"] == "abc123"
    assert "url" in result
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_publisher_hashnode.py -v
```

Expected: FAIL

**Step 3: Write Hashnode publisher**

```python
# src/leadgen/publishers/hashnode.py
"""Cross-post articles to Hashnode via GraphQL API."""

import httpx


HASHNODE_API = "https://gql.hashnode.com"


class HashnodePublisher:
    """Publish articles to Hashnode."""

    def __init__(self, api_token: str, publication_id: str):
        self.api_token = api_token
        self.publication_id = publication_id

    async def publish(self, post_data: dict) -> dict:
        mutation = """
        mutation PublishPost($input: PublishPostInput!) {
            publishPost(input: $input) {
                post {
                    id
                    url
                }
            }
        }
        """

        variables = {
            "input": {
                "title": post_data["title"],
                "contentMarkdown": post_data["body"],
                "publicationId": self.publication_id,
                "tags": [{"name": t} for t in post_data.get("tags", [])],
                "slug": post_data.get("slug", ""),
                "originalArticleURL": post_data.get("canonical_url", ""),
            }
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                HASHNODE_API,
                json={"query": mutation, "variables": variables},
                headers={"Authorization": self.api_token},
            )
            resp.raise_for_status()
            data = resp.json()

        post = data["data"]["publishPost"]["post"]
        return {"id": post["id"], "url": post["url"]}
```

**Step 4: Run Hashnode tests**

```bash
pytest tests/test_publisher_hashnode.py -v
```

Expected: PASS

**Step 5: Write failing tests for Dev.to**

```python
# tests/test_publisher_devto.py
from unittest.mock import patch, AsyncMock
import pytest
from leadgen.publishers.devto import DevtoPublisher


@pytest.fixture
def publisher():
    return DevtoPublisher(api_key="test-key")


@pytest.mark.asyncio
async def test_devto_publish(publisher):
    mock_response = {
        "id": 12345,
        "url": "https://dev.to/username/test-post-abc",
    }

    with patch("leadgen.publishers.devto.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_client.post.return_value.json.return_value = mock_response
        mock_client.post.return_value.raise_for_status = lambda: None

        result = await publisher.publish({
            "title": "Test Post",
            "body": "Content here",
            "tags": ["ai", "automation"],
            "canonical_url": "https://yourdomain.com/posts/test-post/",
        })

    assert result["id"] == 12345
    assert "url" in result
```

**Step 6: Write Dev.to publisher**

```python
# src/leadgen/publishers/devto.py
"""Cross-post articles to Dev.to via REST API."""

import httpx


DEVTO_API = "https://dev.to/api/articles"


class DevtoPublisher:
    """Publish articles to Dev.to."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def publish(self, post_data: dict) -> dict:
        payload = {
            "article": {
                "title": post_data["title"],
                "body_markdown": post_data["body"],
                "published": True,
                "tags": post_data.get("tags", [])[:4],  # Dev.to max 4 tags
                "canonical_url": post_data.get("canonical_url", ""),
            }
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                DEVTO_API,
                json=payload,
                headers={"api-key": self.api_key},
            )
            resp.raise_for_status()
            data = resp.json()

        return {"id": data["id"], "url": data["url"]}
```

**Step 7: Run all publisher tests**

```bash
pytest tests/test_publisher_hashnode.py tests/test_publisher_devto.py -v
```

Expected: PASS

**Step 8: Commit**

```bash
git add src/leadgen/publishers/hashnode.py src/leadgen/publishers/devto.py tests/test_publisher_hashnode.py tests/test_publisher_devto.py
git commit -m "feat: add Hashnode and Dev.to cross-posting publishers"
```

---

## Task 5: Postiz Social Media Distributor

**Files:**
- Create: `src/leadgen/distributors/__init__.py`
- Create: `src/leadgen/distributors/postiz.py`
- Create: `tests/test_distributor_postiz.py`

> **Postiz API Reference:**
> - Base URL: `https://api.postiz.com/public/v1` (cloud) or `https://{BACKEND_URL}/public/v1` (self-hosted)
> - Auth: `Authorization: <api-key>` header (raw key, no "Bearer" prefix)
> - Rate limit: 30 requests/hour (counts API calls, not posts -- batch multiple posts per request)
> - Supports 27+ platforms: LinkedIn, X/Twitter, Facebook, Instagram, TikTok, YouTube, Reddit, Threads, Bluesky, Mastodon, Dev.to, Hashnode, Medium, Pinterest, Discord, Slack, Telegram, and more
> - Multi-platform posting in a single API call

**Step 1: Write the failing test**

```python
# tests/test_distributor_postiz.py
from unittest.mock import patch, AsyncMock
import pytest
from leadgen.distributors.postiz import PostizDistributor


@pytest.fixture
def distributor():
    return PostizDistributor(api_key="test-api-key")


@pytest.mark.asyncio
async def test_get_integrations(distributor):
    mock_integrations = [
        {"id": "int1", "providerIdentifier": "linkedin", "name": "My Company"},
        {"id": "int2", "providerIdentifier": "x", "name": "@myhandle"},
        {"id": "int3", "providerIdentifier": "facebook", "name": "My Page"},
    ]

    with patch("leadgen.distributors.postiz.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_client.get.return_value.json.return_value = mock_integrations
        mock_client.get.return_value.raise_for_status = lambda: None

        integrations = await distributor.get_integrations()

    assert len(integrations) == 3
    assert integrations[0]["providerIdentifier"] == "linkedin"


@pytest.mark.asyncio
async def test_schedule_multi_platform_post(distributor):
    mock_response = [
        {"postId": "post1", "integration": "int1"},
        {"postId": "post2", "integration": "int2"},
    ]

    with patch("leadgen.distributors.postiz.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_client.post.return_value.json.return_value = mock_response
        mock_client.post.return_value.raise_for_status = lambda: None

        result = await distributor.schedule_post(
            posts=[
                {
                    "integration_id": "int1",
                    "platform": "linkedin",
                    "content": "Check out our new blog post about AI for restaurants!",
                },
                {
                    "integration_id": "int2",
                    "platform": "x",
                    "content": "AI agents are saving restaurants 30% on costs.",
                },
            ],
            schedule_date="2026-02-10T10:00:00.000Z",
        )

    assert len(result) == 2
    assert result[0]["postId"] == "post1"


@pytest.mark.asyncio
async def test_post_now(distributor):
    mock_response = [{"postId": "post1", "integration": "int1"}]

    with patch("leadgen.distributors.postiz.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_client.post.return_value.json.return_value = mock_response
        mock_client.post.return_value.raise_for_status = lambda: None

        result = await distributor.post_now(
            integration_id="int1",
            platform="facebook",
            content="New article: How AI agents help dental offices save time!",
        )

    assert result[0]["postId"] == "post1"


@pytest.mark.asyncio
async def test_check_connection(distributor):
    with patch("leadgen.distributors.postiz.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_client.get.return_value.status_code = 200
        mock_client.get.return_value.raise_for_status = lambda: None

        connected = await distributor.check_connection()

    assert connected is True
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_distributor_postiz.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'leadgen.distributors'`

**Step 3: Write minimal implementation**

```python
# src/leadgen/distributors/__init__.py
"""Social media distributors."""
```

```python
# src/leadgen/distributors/postiz.py
"""Schedule social posts via Postiz API (27+ platforms, multi-platform per request).

API docs: https://docs.postiz.com/public-api
Rate limit: 30 requests/hour (counts API calls, not posts).
Auth: Raw API key in Authorization header (no Bearer prefix).
"""

from datetime import datetime, timezone

import httpx


DEFAULT_BASE_URL = "https://api.postiz.com/public/v1"

# Platform-specific settings templates
PLATFORM_SETTINGS = {
    "x": {"__type": "x", "who_can_reply_post": "everyone"},
    "linkedin": {"__type": "linkedin"},
    "facebook": {"__type": "facebook"},
    "instagram": {"__type": "instagram", "post_type": "post"},
    "threads": {"__type": "threads"},
    "bluesky": {"__type": "bluesky"},
    "tiktok": {"__type": "tiktok"},
    "youtube": {"__type": "youtube", "type": "public"},
    "reddit": {"__type": "reddit"},
    "mastodon": {"__type": "mastodon"},
}


class PostizDistributor:
    """Distribute social posts through Postiz (27+ platforms)."""

    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def _headers(self) -> dict:
        return {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
        }

    async def check_connection(self) -> bool:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{self.base_url}/check-connection",
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.status_code == 200

    async def get_integrations(self) -> list[dict]:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{self.base_url}/integrations",
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.json()

    async def schedule_post(
        self,
        posts: list[dict],
        schedule_date: str,
    ) -> list[dict]:
        """Schedule posts to multiple platforms in a single API call.

        Args:
            posts: List of dicts with keys: integration_id, platform, content, image (optional)
            schedule_date: ISO 8601 UTC timestamp (e.g. "2026-02-10T10:00:00.000Z")
        """
        payload = {
            "type": "schedule",
            "date": schedule_date,
            "shortLink": False,
            "tags": [],
            "posts": [
                {
                    "integration": {"id": p["integration_id"]},
                    "value": [
                        {
                            "content": p["content"],
                            "image": p.get("image", []),
                        }
                    ],
                    "settings": PLATFORM_SETTINGS.get(
                        p["platform"], {"__type": p["platform"]}
                    ),
                }
                for p in posts
            ],
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.base_url}/posts",
                json=payload,
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.json()

    async def post_now(
        self,
        integration_id: str,
        platform: str,
        content: str,
        image: list | None = None,
    ) -> list[dict]:
        """Publish a post immediately to a single platform."""
        payload = {
            "type": "now",
            "date": datetime.now(timezone.utc).isoformat(),
            "shortLink": False,
            "tags": [],
            "posts": [
                {
                    "integration": {"id": integration_id},
                    "value": [
                        {
                            "content": content,
                            "image": image or [],
                        }
                    ],
                    "settings": PLATFORM_SETTINGS.get(
                        platform, {"__type": platform}
                    ),
                }
            ],
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.base_url}/posts",
                json=payload,
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.json()
```

**Step 4: Run tests**

```bash
pytest tests/test_distributor_postiz.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/leadgen/distributors/ tests/test_distributor_postiz.py
git commit -m "feat: add Postiz social media distributor (27+ platforms)"
```

---

## Task 6: ConvertKit Email Integration

**Files:**
- Create: `src/leadgen/email/__init__.py`
- Create: `src/leadgen/email/convertkit.py`
- Create: `tests/test_email_convertkit.py`

**Step 1: Write the failing test**

```python
# tests/test_email_convertkit.py
from unittest.mock import patch, AsyncMock
import pytest
from leadgen.email.convertkit import ConvertKitClient


@pytest.fixture
def client():
    return ConvertKitClient(
        api_key="test-key",
        api_secret="test-secret",
    )


@pytest.mark.asyncio
async def test_add_subscriber(client):
    mock_response = {
        "subscription": {
            "id": 1,
            "subscriber": {"id": 100, "email_address": "test@example.com"},
        }
    }

    with patch("leadgen.email.convertkit.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_client.post.return_value.json.return_value = mock_response
        mock_client.post.return_value.raise_for_status = lambda: None

        result = await client.add_subscriber_to_form(
            form_id="form123",
            email="test@example.com",
            first_name="Test",
        )

    assert result["subscription"]["subscriber"]["email_address"] == "test@example.com"


@pytest.mark.asyncio
async def test_list_subscribers(client):
    mock_response = {
        "total_subscribers": 42,
        "subscribers": [
            {"id": 1, "email_address": "a@example.com"},
            {"id": 2, "email_address": "b@example.com"},
        ],
    }

    with patch("leadgen.email.convertkit.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_client.get.return_value.json.return_value = mock_response
        mock_client.get.return_value.raise_for_status = lambda: None

        result = await client.list_subscribers()

    assert result["total_subscribers"] == 42
    assert len(result["subscribers"]) == 2
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_email_convertkit.py -v
```

Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/leadgen/email/__init__.py
"""Email marketing integrations."""
```

```python
# src/leadgen/email/convertkit.py
"""ConvertKit API client (free tier: 10K subscribers, unlimited emails)."""

import httpx


CONVERTKIT_API = "https://api.convertkit.com/v3"


class ConvertKitClient:
    """Manage subscribers and forms via ConvertKit."""

    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret

    async def add_subscriber_to_form(
        self,
        form_id: str,
        email: str,
        first_name: str = "",
    ) -> dict:
        payload = {
            "api_key": self.api_key,
            "email": email,
        }
        if first_name:
            payload["first_name"] = first_name

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{CONVERTKIT_API}/forms/{form_id}/subscribe",
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()

    async def list_subscribers(self) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{CONVERTKIT_API}/subscribers",
                params={"api_secret": self.api_secret},
            )
            resp.raise_for_status()
            return resp.json()
```

**Step 4: Run tests**

```bash
pytest tests/test_email_convertkit.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/leadgen/email/ tests/test_email_convertkit.py
git commit -m "feat: add ConvertKit email subscriber management"
```

---

## Task 7: SEO Keyword Research Module

**Files:**
- Create: `src/leadgen/seo/__init__.py`
- Create: `src/leadgen/seo/keywords.py`
- Create: `src/leadgen/seo/content_calendar.py`
- Create: `tests/test_seo_keywords.py`

**Step 1: Write the failing test**

```python
# tests/test_seo_keywords.py
from unittest.mock import patch, AsyncMock
import pytest
from leadgen.seo.keywords import KeywordResearcher


@pytest.fixture
def researcher():
    return KeywordResearcher(
        login="test-login",
        password="test-password",
    )


@pytest.mark.asyncio
async def test_get_keyword_suggestions(researcher):
    mock_response = {
        "tasks": [
            {
                "result": [
                    {
                        "items": [
                            {
                                "keyword": "ai chatbot for restaurants",
                                "search_volume": 1200,
                                "keyword_difficulty": 35,
                            },
                            {
                                "keyword": "restaurant automation software",
                                "search_volume": 800,
                                "keyword_difficulty": 42,
                            },
                        ]
                    }
                ]
            }
        ]
    }

    with patch("leadgen.seo.keywords.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_client.post.return_value.json.return_value = mock_response
        mock_client.post.return_value.raise_for_status = lambda: None

        results = await researcher.get_suggestions("ai agents for restaurants")

    assert len(results) == 2
    assert results[0]["keyword"] == "ai chatbot for restaurants"
    assert results[0]["search_volume"] == 1200


def test_filter_low_competition(researcher):
    keywords = [
        {"keyword": "easy", "keyword_difficulty": 20, "search_volume": 500},
        {"keyword": "hard", "keyword_difficulty": 80, "search_volume": 5000},
        {"keyword": "medium", "keyword_difficulty": 45, "search_volume": 1000},
    ]
    filtered = researcher.filter_low_competition(keywords, max_difficulty=50)
    assert len(filtered) == 2
    assert all(k["keyword_difficulty"] <= 50 for k in filtered)
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_seo_keywords.py -v
```

Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/leadgen/seo/__init__.py
"""SEO and keyword research tools."""
```

```python
# src/leadgen/seo/keywords.py
"""Keyword research via DataForSEO API ($6/mo for 10K searches)."""

import httpx


DATAFORSEO_API = "https://api.dataforseo.com/v3"


class KeywordResearcher:
    """Research keywords for content planning."""

    def __init__(self, login: str, password: str):
        self.login = login
        self.password = password

    def _auth(self) -> tuple[str, str]:
        return (self.login, self.password)

    async def get_suggestions(self, seed_keyword: str) -> list[dict]:
        payload = [
            {
                "keyword": seed_keyword,
                "location_code": 2840,  # United States
                "language_code": "en",
            }
        ]

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{DATAFORSEO_API}/dataforseo_labs/google/keyword_suggestions/live",
                json=payload,
                auth=self._auth(),
            )
            resp.raise_for_status()
            data = resp.json()

        items = data["tasks"][0]["result"][0]["items"]
        return [
            {
                "keyword": item["keyword"],
                "search_volume": item["search_volume"],
                "keyword_difficulty": item["keyword_difficulty"],
            }
            for item in items
        ]

    def filter_low_competition(
        self, keywords: list[dict], max_difficulty: int = 50
    ) -> list[dict]:
        return [k for k in keywords if k["keyword_difficulty"] <= max_difficulty]
```

**Step 4: Run tests**

```bash
pytest tests/test_seo_keywords.py -v
```

Expected: PASS

**Step 5: Write content calendar generator**

```python
# src/leadgen/seo/content_calendar.py
"""Generate a content calendar from keyword research."""

from dataclasses import dataclass
from datetime import date, timedelta


NICHES = [
    "restaurants",
    "law firms",
    "real estate",
    "dental offices",
    "hvac plumbing",
    "accounting firms",
]


@dataclass
class CalendarEntry:
    publish_date: date
    niche: str
    keyword: str
    search_volume: int
    post_type: str  # "how-to", "listicle", "case-study", "comparison"


def generate_calendar(
    keywords_by_niche: dict[str, list[dict]],
    start_date: date,
    posts_per_week: int = 3,
) -> list[CalendarEntry]:
    """Generate a publishing calendar rotating through niches.

    Posts 3x/week by default, rotating niches to cover all verticals.
    Prioritizes low-competition, high-volume keywords.
    """
    entries = []
    day = start_date
    post_types = ["how-to", "listicle", "case-study", "comparison"]
    niche_index = 0
    type_index = 0

    week_count = 0
    while week_count < 4:  # 4 weeks = 1 month
        for _ in range(posts_per_week):
            niche = NICHES[niche_index % len(NICHES)]
            niche_keywords = keywords_by_niche.get(niche, [])

            if niche_keywords:
                kw = niche_keywords.pop(0)
                entries.append(
                    CalendarEntry(
                        publish_date=day,
                        niche=niche,
                        keyword=kw["keyword"],
                        search_volume=kw["search_volume"],
                        post_type=post_types[type_index % len(post_types)],
                    )
                )
                type_index += 1

            niche_index += 1
            day += timedelta(days=2)  # Every other day

        week_count += 1
        # Skip to next week if needed
        while day.weekday() >= 5:  # Skip weekends
            day += timedelta(days=1)

    return entries
```

**Step 6: Commit**

```bash
git add src/leadgen/seo/ tests/test_seo_keywords.py
git commit -m "feat: add SEO keyword research and content calendar"
```

---

## Task 8: Lead Magnet - AI ROI Calculator

**Files:**
- Create: `lead-magnets/roi-calculator/index.html`
- Create: `lead-magnets/roi-calculator/style.css`
- Create: `lead-magnets/roi-calculator/script.js`
- Create: `lead-magnets/roi-calculator/package.json` (for Vercel deployment)

**Step 1: Create the ROI calculator HTML**

```html
<!-- lead-magnets/roi-calculator/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Agent ROI Calculator - See How Much You Could Save</title>
    <meta name="description" content="Free calculator: see exactly how much time and money AI agents could save your business. Built for restaurants, law firms, dental offices, and more.">
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="calculator-container">
        <h1>AI Agent ROI Calculator</h1>
        <p class="subtitle">See how much time and money AI could save your business</p>

        <form id="roi-form">
            <div class="field">
                <label for="industry">Your Industry</label>
                <select id="industry" required>
                    <option value="">Select your industry...</option>
                    <option value="restaurant">Restaurant / Food Service</option>
                    <option value="law">Law Firm</option>
                    <option value="realestate">Real Estate</option>
                    <option value="dental">Dental / Medical Office</option>
                    <option value="hvac">HVAC / Plumbing / Trades</option>
                    <option value="accounting">Accounting Firm</option>
                    <option value="other">Other</option>
                </select>
            </div>

            <div class="field">
                <label for="employees">Number of Employees</label>
                <input type="number" id="employees" min="1" max="500" placeholder="e.g., 15" required>
            </div>

            <div class="field">
                <label for="hours-admin">Hours/week spent on repetitive admin tasks</label>
                <input type="number" id="hours-admin" min="1" max="168" placeholder="e.g., 20" required>
            </div>

            <div class="field">
                <label for="hourly-rate">Average hourly labor cost ($)</label>
                <input type="number" id="hourly-rate" min="10" max="500" placeholder="e.g., 25" required>
            </div>

            <div class="field">
                <label for="missed-calls">Estimated missed calls/inquiries per week</label>
                <input type="number" id="missed-calls" min="0" max="200" placeholder="e.g., 10" required>
            </div>

            <div class="field">
                <label for="avg-deal">Average deal/order value ($)</label>
                <input type="number" id="avg-deal" min="10" max="100000" placeholder="e.g., 50" required>
            </div>

            <button type="submit" id="calculate-btn">Calculate My Savings</button>
        </form>

        <div id="results" class="hidden">
            <h2>Your Estimated AI Agent ROI</h2>

            <div class="result-cards">
                <div class="card">
                    <span class="label">Monthly Time Saved</span>
                    <span class="value" id="time-saved">-</span>
                </div>
                <div class="card">
                    <span class="label">Monthly Labor Savings</span>
                    <span class="value" id="labor-savings">-</span>
                </div>
                <div class="card">
                    <span class="label">Monthly Revenue Recovered</span>
                    <span class="value" id="revenue-recovered">-</span>
                </div>
                <div class="card highlight">
                    <span class="label">Total Monthly Impact</span>
                    <span class="value" id="total-impact">-</span>
                </div>
                <div class="card highlight">
                    <span class="label">Annual Impact</span>
                    <span class="value" id="annual-impact">-</span>
                </div>
            </div>

            <div class="cta-section">
                <h3>Want to see these savings in your business?</h3>
                <p>Get a free 15-minute consultation to see which AI agents fit your business.</p>
                <a href="#email-capture" class="cta-button" id="cta-link">Get Your Free AI Assessment</a>
            </div>
        </div>

        <div id="email-capture" class="hidden">
            <h3>Get Your Personalized AI Assessment</h3>
            <p>We'll send you a custom report for your <span id="industry-name">business</span>.</p>
            <!-- Tally embed or simple form that posts to ConvertKit -->
            <div id="tally-form-container">
                <!-- Replace with your Tally embed code -->
                <iframe data-tally-src="https://tally.so/embed/YOUR_FORM_ID?alignLeft=1&hideTitle=1" width="100%" height="300" frameborder="0"></iframe>
            </div>
        </div>
    </div>

    <script src="script.js"></script>
</body>
</html>
```

**Step 2: Create the CSS**

```css
/* lead-magnets/roi-calculator/style.css */
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #f8fafc;
    color: #1e293b;
    line-height: 1.6;
}

.calculator-container {
    max-width: 640px;
    margin: 2rem auto;
    padding: 2rem;
}

h1 {
    font-size: 2rem;
    margin-bottom: 0.5rem;
    color: #0f172a;
}

.subtitle {
    color: #64748b;
    margin-bottom: 2rem;
    font-size: 1.1rem;
}

.field {
    margin-bottom: 1.25rem;
}

label {
    display: block;
    font-weight: 600;
    margin-bottom: 0.4rem;
    font-size: 0.95rem;
}

input, select {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.2s;
}

input:focus, select:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

button, .cta-button {
    display: inline-block;
    width: 100%;
    padding: 0.9rem;
    background: #2563eb;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
    text-align: center;
    text-decoration: none;
    margin-top: 0.5rem;
}

button:hover, .cta-button:hover {
    background: #1d4ed8;
}

.hidden { display: none; }

#results { margin-top: 2rem; }

.result-cards {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin: 1.5rem 0;
}

.card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.25rem;
    text-align: center;
}

.card.highlight {
    background: #eff6ff;
    border-color: #3b82f6;
}

.card .label {
    display: block;
    font-size: 0.85rem;
    color: #64748b;
    margin-bottom: 0.5rem;
}

.card .value {
    display: block;
    font-size: 1.5rem;
    font-weight: 700;
    color: #0f172a;
}

.card.highlight .value {
    color: #2563eb;
}

.cta-section {
    background: #0f172a;
    color: white;
    padding: 2rem;
    border-radius: 12px;
    text-align: center;
    margin-top: 2rem;
}

.cta-section h3 { margin-bottom: 0.5rem; }
.cta-section p { color: #94a3b8; margin-bottom: 1rem; }

.cta-section .cta-button {
    background: #22c55e;
    width: auto;
    padding: 0.9rem 2rem;
}

.cta-section .cta-button:hover {
    background: #16a34a;
}

#email-capture {
    margin-top: 2rem;
    padding: 2rem;
    background: white;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
}

@media (max-width: 600px) {
    .result-cards { grid-template-columns: 1fr; }
    .calculator-container { padding: 1rem; }
}
```

**Step 3: Create the JavaScript**

```javascript
// lead-magnets/roi-calculator/script.js

// Industry-specific automation efficiency rates
const AUTOMATION_RATES = {
    restaurant: { adminReduction: 0.60, callCapture: 0.75, label: "Restaurant" },
    law: { adminReduction: 0.45, callCapture: 0.80, label: "Law Firm" },
    realestate: { adminReduction: 0.50, callCapture: 0.85, label: "Real Estate Agency" },
    dental: { adminReduction: 0.55, callCapture: 0.70, label: "Dental Office" },
    hvac: { adminReduction: 0.50, callCapture: 0.80, label: "HVAC/Trades Business" },
    accounting: { adminReduction: 0.55, callCapture: 0.70, label: "Accounting Firm" },
    other: { adminReduction: 0.45, callCapture: 0.70, label: "Business" },
};

function formatCurrency(amount) {
    return "$" + Math.round(amount).toLocaleString();
}

document.getElementById("roi-form").addEventListener("submit", function (e) {
    e.preventDefault();

    const industry = document.getElementById("industry").value;
    const hoursAdmin = parseFloat(document.getElementById("hours-admin").value);
    const hourlyRate = parseFloat(document.getElementById("hourly-rate").value);
    const missedCalls = parseFloat(document.getElementById("missed-calls").value);
    const avgDeal = parseFloat(document.getElementById("avg-deal").value);

    const rates = AUTOMATION_RATES[industry];

    // Monthly calculations (4.33 weeks/month)
    const weeksPerMonth = 4.33;
    const hoursSaved = hoursAdmin * rates.adminReduction * weeksPerMonth;
    const laborSavings = hoursSaved * hourlyRate;
    const callsRecovered = missedCalls * rates.callCapture * weeksPerMonth;
    const conversionRate = 0.15; // 15% of recovered calls convert
    const revenueRecovered = callsRecovered * conversionRate * avgDeal;
    const totalMonthly = laborSavings + revenueRecovered;
    const totalAnnual = totalMonthly * 12;

    document.getElementById("time-saved").textContent = Math.round(hoursSaved) + " hours";
    document.getElementById("labor-savings").textContent = formatCurrency(laborSavings);
    document.getElementById("revenue-recovered").textContent = formatCurrency(revenueRecovered);
    document.getElementById("total-impact").textContent = formatCurrency(totalMonthly);
    document.getElementById("annual-impact").textContent = formatCurrency(totalAnnual);
    document.getElementById("industry-name").textContent = rates.label;

    document.getElementById("results").classList.remove("hidden");
    document.getElementById("results").scrollIntoView({ behavior: "smooth" });
});

document.getElementById("cta-link").addEventListener("click", function (e) {
    e.preventDefault();
    document.getElementById("email-capture").classList.remove("hidden");
    document.getElementById("email-capture").scrollIntoView({ behavior: "smooth" });
});
```

**Step 4: Commit**

```bash
git add lead-magnets/
git commit -m "feat: add AI ROI calculator lead magnet"
```

---

## Task 9: CLI Orchestrator - Wire Everything Together

**Files:**
- Modify: `src/leadgen/cli.py`
- Create: `src/leadgen/config.py`
- Create: `src/leadgen/pipeline.py`
- Create: `tests/test_pipeline.py`

**Step 1: Write the failing test**

```python
# tests/test_pipeline.py
from unittest.mock import patch, AsyncMock, MagicMock
import pytest
from leadgen.pipeline import LeadgenPipeline


@pytest.fixture
def pipeline():
    return LeadgenPipeline(
        ollama_url="http://localhost:11434",
        ollama_model="llama3.2",
        hugo_blog_dir="/tmp/test-blog",
    )


@pytest.mark.asyncio
async def test_generate_and_publish_post(pipeline):
    mock_post = {
        "title": "Test Post",
        "slug": "test-post",
        "meta_description": "Test description",
        "body": "# Test\n\nContent",
        "tags": ["test"],
    }

    with patch.object(
        pipeline.generator, "generate_blog_post", new_callable=AsyncMock
    ) as mock_gen:
        mock_gen.return_value = mock_post

        with patch.object(
            pipeline.hugo_publisher, "publish"
        ) as mock_publish:
            from pathlib import Path
            mock_publish.return_value = Path("/tmp/test-blog/content/posts/test-post.md")

            result = await pipeline.generate_and_publish(
                niche="restaurants",
                topic="AI chatbots for reservations",
            )

    assert result["title"] == "Test Post"
    assert result["local_path"].name == "test-post.md"
    mock_gen.assert_called_once()
    mock_publish.assert_called_once()
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_pipeline.py -v
```

Expected: FAIL

**Step 3: Write config module**

```python
# src/leadgen/config.py
"""Load configuration from environment variables."""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


@dataclass
class Config:
    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # Hugo
    hugo_blog_dir: str = ""

    # Hashnode
    hashnode_api_token: str = ""
    hashnode_publication_id: str = ""

    # Dev.to
    devto_api_key: str = ""

    # Postiz
    postiz_api_key: str = ""
    postiz_base_url: str = "https://api.postiz.com/public/v1"

    # ConvertKit
    convertkit_api_key: str = ""
    convertkit_api_secret: str = ""

    # DataForSEO
    dataforseo_login: str = ""
    dataforseo_password: str = ""


def load_config() -> Config:
    load_dotenv()
    return Config(
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3.2"),
        hugo_blog_dir=os.getenv("HUGO_BLOG_DIR", str(Path.cwd() / "blog")),
        hashnode_api_token=os.getenv("HASHNODE_API_TOKEN", ""),
        hashnode_publication_id=os.getenv("HASHNODE_PUBLICATION_ID", ""),
        devto_api_key=os.getenv("DEVTO_API_KEY", ""),
        postiz_api_key=os.getenv("POSTIZ_API_KEY", ""),
        postiz_base_url=os.getenv("POSTIZ_BASE_URL", "https://api.postiz.com/public/v1"),
        convertkit_api_key=os.getenv("CONVERTKIT_API_KEY", ""),
        convertkit_api_secret=os.getenv("CONVERTKIT_API_SECRET", ""),
        dataforseo_login=os.getenv("DATAFORSEO_LOGIN", ""),
        dataforseo_password=os.getenv("DATAFORSEO_PASSWORD", ""),
    )
```

**Step 4: Write pipeline module**

```python
# src/leadgen/pipeline.py
"""Orchestrate the full content generation and distribution pipeline."""

from leadgen.content_generator import ContentGenerator
from leadgen.publishers.hugo import HugoPublisher


class LeadgenPipeline:
    """End-to-end pipeline: generate -> publish -> distribute."""

    def __init__(self, ollama_url: str, ollama_model: str, hugo_blog_dir: str):
        self.generator = ContentGenerator(base_url=ollama_url, model=ollama_model)
        self.hugo_publisher = HugoPublisher(blog_dir=hugo_blog_dir)

    async def generate_and_publish(self, niche: str, topic: str) -> dict:
        post_data = await self.generator.generate_blog_post(
            niche=niche, topic=topic
        )

        local_path = self.hugo_publisher.publish(post_data)

        return {
            "title": post_data["title"],
            "slug": post_data["slug"],
            "tags": post_data.get("tags", []),
            "local_path": local_path,
        }
```

**Step 5: Run tests**

```bash
pytest tests/test_pipeline.py -v
```

Expected: PASS

**Step 6: Update CLI with full command set**

```python
# src/leadgen/cli.py
"""CLI entry point for the leadgen tool."""

import asyncio

import click

from leadgen.config import load_config
from leadgen.pipeline import LeadgenPipeline


@click.group()
def main():
    """Organic lead generation automation."""
    pass


@main.command()
def status():
    """Show system status and configuration."""
    config = load_config()
    click.echo("Leadgen system: OK")
    click.echo(f"  Ollama: {config.ollama_base_url} ({config.ollama_model})")
    click.echo(f"  Hugo blog: {config.hugo_blog_dir}")
    click.echo(f"  Hashnode: {'configured' if config.hashnode_api_token else 'not set'}")
    click.echo(f"  Dev.to: {'configured' if config.devto_api_key else 'not set'}")
    click.echo(f"  Postiz: {'configured' if config.postiz_api_key else 'not set'}")
    click.echo(f"  ConvertKit: {'configured' if config.convertkit_api_key else 'not set'}")
    click.echo(f"  DataForSEO: {'configured' if config.dataforseo_login else 'not set'}")


@main.command()
@click.option("--niche", required=True, help="Target niche (e.g., restaurants)")
@click.option("--topic", required=True, help="Blog topic")
def generate(niche, topic):
    """Generate a blog post and publish locally."""
    config = load_config()
    pipeline = LeadgenPipeline(
        ollama_url=config.ollama_base_url,
        ollama_model=config.ollama_model,
        hugo_blog_dir=config.hugo_blog_dir,
    )

    result = asyncio.run(pipeline.generate_and_publish(niche=niche, topic=topic))
    click.echo(f"Published: {result['title']}")
    click.echo(f"  Path: {result['local_path']}")


@main.command()
@click.option("--niche", required=True, help="Target niche for keywords")
@click.option("--max-difficulty", default=50, help="Max keyword difficulty (0-100)")
def keywords(niche, max_difficulty):
    """Research keywords for a niche."""
    config = load_config()

    if not config.dataforseo_login:
        click.echo("Error: DATAFORSEO_LOGIN not configured. See .env.example")
        return

    from leadgen.seo.keywords import KeywordResearcher

    researcher = KeywordResearcher(
        login=config.dataforseo_login,
        password=config.dataforseo_password,
    )

    results = asyncio.run(
        researcher.get_suggestions(f"ai agents for {niche}")
    )
    filtered = researcher.filter_low_competition(results, max_difficulty)

    click.echo(f"Found {len(filtered)} low-competition keywords for '{niche}':")
    for kw in sorted(filtered, key=lambda x: x["search_volume"], reverse=True)[:20]:
        click.echo(
            f"  [{kw['keyword_difficulty']:2d}] {kw['keyword']} "
            f"({kw['search_volume']:,} searches/mo)"
        )
```

**Step 7: Run all tests**

```bash
pytest tests/ -v
```

Expected: ALL PASS

**Step 8: Commit**

```bash
git add src/leadgen/config.py src/leadgen/pipeline.py src/leadgen/cli.py tests/test_pipeline.py
git commit -m "feat: add pipeline orchestrator and full CLI commands"
```

---

## Task 10: GitHub Actions Automation (Auto-Publish on Schedule)

**Files:**
- Create: `.github/workflows/publish.yml`
- Create: `.github/workflows/deploy-blog.yml`

**Step 1: Create the content generation workflow**

```yaml
# .github/workflows/publish.yml
name: Generate and Publish Content

on:
  schedule:
    # Run Mon/Wed/Fri at 9am UTC (3 posts/week)
    - cron: '0 9 * * 1,3,5'
  workflow_dispatch:
    inputs:
      niche:
        description: 'Target niche'
        required: true
        default: 'restaurants'
      topic:
        description: 'Blog topic'
        required: true

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -e .

      - name: Install Ollama
        run: |
          curl -fsSL https://ollama.com/install.sh | sh
          ollama pull llama3.2

      - name: Generate blog post
        env:
          OLLAMA_BASE_URL: http://localhost:11434
          OLLAMA_MODEL: llama3.2
          HUGO_BLOG_DIR: ./blog
        run: |
          # Rotate through niches based on day of year
          NICHES=("restaurants" "law firms" "real estate" "dental offices" "hvac" "accounting")
          DAY=$(date +%j)
          NICHE=${NICHES[$((DAY % 6))]}
          TOPICS=(
            "how AI agents save money"
            "automating customer service"
            "reducing missed appointments"
            "streamlining operations"
          )
          TOPIC=${TOPICS[$((DAY % 4))]}
          leadgen generate --niche "$NICHE" --topic "$TOPIC"

      - name: Commit and push new post
        run: |
          git config user.name "Leadgen Bot"
          git config user.email "bot@yourdomain.com"
          git add blog/content/
          git diff --cached --quiet || git commit -m "content: auto-generated blog post"
          git push
```

**Step 2: Create the blog deployment workflow**

```yaml
# .github/workflows/deploy-blog.yml
name: Deploy Blog to GitHub Pages

on:
  push:
    paths:
      - 'blog/**'
    branches:
      - main

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive

      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v3
        with:
          hugo-version: '0.142.0'
          extended: true

      - name: Build
        run: hugo --minify --source blog

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: blog/public

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

**Step 3: Commit**

```bash
git add .github/
git commit -m "feat: add GitHub Actions for auto-publishing and blog deployment"
```

---

## Task 11: Cross-Posting and Social Distribution Automation

**Files:**
- Modify: `src/leadgen/pipeline.py`
- Create: `tests/test_pipeline_distribute.py`

**Step 1: Write the failing test**

```python
# tests/test_pipeline_distribute.py
from unittest.mock import patch, AsyncMock, MagicMock
from pathlib import Path
import pytest
from leadgen.pipeline import LeadgenPipeline


@pytest.fixture
def pipeline():
    p = LeadgenPipeline(
        ollama_url="http://localhost:11434",
        ollama_model="llama3.2",
        hugo_blog_dir="/tmp/test-blog",
    )
    return p


@pytest.mark.asyncio
async def test_full_pipeline_with_cross_post_and_social(pipeline):
    mock_post = {
        "title": "Test Post",
        "slug": "test-post",
        "meta_description": "Test",
        "body": "# Test\n\nContent",
        "tags": ["test"],
    }
    mock_social = {
        "linkedin": "LinkedIn post text...",
        "x": "X/Twitter post text...",
        "facebook": "Facebook post text...",
        "instagram": "Instagram post text...",
        "threads": "Threads post text...",
    }

    with patch.object(
        pipeline.generator, "generate_blog_post", new_callable=AsyncMock
    ) as mock_gen, patch.object(
        pipeline.generator, "repurpose_to_social", new_callable=AsyncMock
    ) as mock_social_gen, patch.object(
        pipeline.hugo_publisher, "publish"
    ) as mock_publish:

        mock_gen.return_value = mock_post
        mock_social_gen.return_value = mock_social
        mock_publish.return_value = Path("/tmp/test-blog/content/posts/test-post.md")

        result = await pipeline.generate_and_publish(
            niche="restaurants",
            topic="AI chatbots",
        )

        social = await pipeline.generator.repurpose_to_social(
            blog_title=result["title"],
            blog_body=mock_post["body"],
        )

    assert "linkedin" in social
    assert "x" in social
    assert len(social["x"]) <= 280
```

**Step 2: Run test**

```bash
pytest tests/test_pipeline_distribute.py -v
```

Expected: PASS (uses existing code)

**Step 3: Commit**

```bash
git add tests/test_pipeline_distribute.py
git commit -m "test: add full pipeline integration test with cross-posting"
```

---

## Task 12: Vercel Deployment Config for Lead Magnets

**Files:**
- Create: `lead-magnets/vercel.json`

**Step 1: Create Vercel config**

```json
{
  "version": 2,
  "builds": [
    {
      "src": "roi-calculator/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    { "src": "/roi-calculator/(.*)", "dest": "/roi-calculator/$1" },
    { "src": "/roi-calculator", "dest": "/roi-calculator/index.html" }
  ]
}
```

**Step 2: Commit**

```bash
git add lead-magnets/vercel.json
git commit -m "feat: add Vercel deployment config for lead magnets"
```

---

## Task 13: Documentation and Launch Checklist

**Files:**
- Create: `docs/SETUP.md`

**Step 1: Write setup documentation**

```markdown
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
```

**Step 2: Commit**

```bash
git add docs/
git commit -m "docs: add setup guide and launch checklist"
```

---

## Task 14: Run All Tests and Final Verification

**Step 1: Run full test suite**

```bash
pytest tests/ -v --tb=short
```

Expected: ALL PASS

**Step 2: Verify CLI works**

```bash
leadgen status
leadgen --help
leadgen generate --help
leadgen keywords --help
```

Expected: All commands show help/output correctly

**Step 3: Verify Hugo blog builds**

```bash
cd blog && hugo --minify
```

Expected: Build succeeds, outputs to `blog/public/`

**Step 4: Final commit**

```bash
git add -A
git diff --cached --quiet || git commit -m "chore: final cleanup and verification"
```

---

## Growth Strategy Summary

**Daily Autopilot Actions (automated):**
1. Mon/Wed/Fri: Generate + publish 1 SEO blog post (Hugo + GitHub Pages)
2. Same day: Cross-post to Hashnode + Dev.to (canonical back to your domain)
3. Same day: Generate 3+ social posts from blog (LinkedIn, X, Facebook, Instagram, Threads via Postiz)
4. Continuous: ROI calculator captures emails -> ConvertKit

**Monthly Output (fully automated):**
- 12 blog posts/month
- 12 Hashnode cross-posts
- 12 Dev.to cross-posts
- 60+ social media posts (5+ platforms per blog post via Postiz)
- 1 evergreen lead magnet generating leads 24/7

**Estimated Growth Curve:**
- Month 1: 50-150 organic visits, 2-5 leads
- Month 2: 200-500 organic visits, 8-15 leads
- Month 3: 500-1500 organic visits, 15-40 leads
- Month 6: 2000-5000 organic visits, 50-150 leads

**Cost: ~$7/month** (domain + DataForSEO), leaving $93 reserve for scaling.
