# Status & Gaps Report

> Last updated: 2026-02-07

## System Overview

Automated content + inbound lead generation system targeting non-tech businesses
needing AI agents. Uses Claude Code CLI for content generation, Hugo for blogging,
and Python CLI for orchestration.

**Repo:** https://github.com/rami2102/organic-leadgen

---

## What Works (Tested Live)

| Component | Command / How | Verified |
|---|---|---|
| Unit tests (18/18) | `pytest tests/ -v` | All pass |
| CLI status | `leadgen status` | Shows all services + model |
| Blog generation | `leadgen generate --niche X --topic Y` | Real blog post generated via Claude CLI (120 lines, SEO-optimized) |
| Hugo blog build | `cd blog && hugo` | Builds clean, PaperMod theme, 0 errors |
| Keywords error handling | `leadgen keywords --niche X` | Correct error when no credentials |
| Cron install/remove | `leadgen cron --install` / `--remove` | Cron entry in crontab confirmed |
| GitHub repo | `gh repo view` | Live at rami2102/organic-leadgen |
| Git push | 16 commits pushed | All at origin/master |
| Ollama cleanup | Removed binary + 1.9GB model data | Fully gone |

## What Is NOT Tested

| Component | Risk | Why |
|---|---|---|
| `leadgen publish` (manual publish + git push) | Medium | Added but never ran end-to-end |
| `leadgen autopublish` (cron target) | Medium | Delegates to `publish` via CliRunner — untested |
| Cron actually firing | Low | Installed, next trigger Mon 9am UTC, never triggered |
| `repurpose_to_social` via live Claude CLI | Medium | Only mocked in unit tests |
| Hashnode cross-posting | Can't test | No API token |
| Dev.to cross-posting | Can't test | No API key |
| Postiz social distribution | Can't test | No API key |
| ConvertKit email | Can't test | No API key/secret |
| DataForSEO keyword research | Can't test | No login/password |
| GitHub Actions CI workflow | Medium | Workflow exists, Claude CLI install in CI untested |
| GitHub Pages deployment | Can't test | Pages not enabled on repo |
| Lead magnet on Vercel | Can't test | Vercel CLI not installed, no account |

---

## Critical Gaps

### 1. Pipeline Is Not Fully Wired (HIGH)

`pipeline.py` only does: **generate blog → publish to Hugo**

It does NOT chain the full flow:
```
generate blog
  → publish to Hugo
  → cross-post to Hashnode
  → cross-post to Dev.to
  → repurpose to social (5 platforms)
  → distribute via Postiz
  → add to ConvertKit (future)
```

The individual modules exist and pass unit tests, but the pipeline `generate_and_publish()`
only calls the first two steps. Running `leadgen publish` today creates a blog post and
pushes to git — it does NOT cross-post or distribute to social media.

**To fix:** Wire all modules into `pipeline.py` with optional steps (skip if credentials
not configured).

### 2. No GUI — CLI Only (HIGH)

There is no graphical interface. The entire system requires terminal access and
familiarity with CLI commands. A non-technical user (the target audience's profile,
not our profile) cannot:

- View generated content before it goes live
- Approve or reject posts
- Configure settings without editing `.env` files
- See analytics or performance
- Manage the content calendar visually

**What's needed:**
- Web dashboard (even minimal) for content preview + approve/reject
- Settings page for API keys (instead of `.env` editing)
- Content calendar view
- Analytics dashboard (traffic, leads, conversion)

**Options to build this:**
- Lightweight: Static HTML dashboard + JSON API (no framework)
- Medium: Flask/FastAPI single-page app
- Full: Next.js or similar frontend framework

### 3. No A/B Testing (MEDIUM)

Content goes out as-is. There is no mechanism to:

- Generate multiple title/content variants
- Test different CTAs, headlines, or formats
- Measure which variant performs better
- Automatically select winners

**What's needed:**
- Generate 2-3 title/hook variants per post
- Track click-through or engagement per variant (requires analytics integration)
- Auto-select winner after N impressions (or manual selection)

**Simplest approach:**
- Generate 2 title variants with Claude CLI
- Publish the first, A/B test via social posts (different titles → same link)
- Track via UTM parameters + simple analytics (Plausible/Umami, both free/self-hosted)

### 4. No Content Approval Workflow (MEDIUM)

Content is auto-generated and auto-published with zero human review. This means:

- Factually incorrect content could go live
- Off-brand tone could reach social media
- No quality gate between generation and publication

**What's needed:**
- `leadgen generate` creates a draft (not published)
- Human reviews draft (via GUI or email notification)
- `leadgen approve <post-id>` publishes the approved draft
- OR: Auto-publish with a "confidence threshold" (e.g., only if Claude rates quality > 8/10)

### 5. No Analytics or Feedback Loop (MEDIUM)

The system publishes content but has no way to know if it's working:

- No traffic tracking
- No lead conversion tracking
- No content performance scoring
- No feedback into content strategy (which niches/topics perform best)

**What's needed:**
- Integrate analytics (Plausible or Umami — free self-hosted)
- Track: page views, time on page, CTA clicks, form submissions
- Feed performance data back into topic selection

### 6. External Services Not Configured (BLOCKED)

These require manual account setup and API key configuration:

| Service | Status | Action Required |
|---|---|---|
| Hashnode | Module ready, no credentials | Create account, get API token |
| Dev.to | Module ready, no credentials | Create account, get API key |
| Postiz | Module ready, no credentials | Log in, connect channels, get API key |
| ConvertKit | Module ready, no credentials | Create account, create form, get API key/secret |
| DataForSEO | Module ready, no credentials | Create account, add $6 credit |
| GitHub Pages | Workflow ready, not enabled | Enable in repo Settings > Pages |
| Vercel | Config ready, not deployed | Create account, run `npx vercel` |
| Tally | Placeholder in lead magnet | Create form, update iframe src |

---

## Architecture Completeness

```
Component                    Code    Unit Test    Live Test    Wired in Pipeline
─────────────────────────────────────────────────────────────────────────────────
Content Generator (Claude)    ✅        ✅           ✅             ✅
Hugo Publisher                ✅        ✅           ✅             ✅
Hashnode Publisher            ✅        ✅           ❌             ❌
Dev.to Publisher              ✅        ✅           ❌             ❌
Postiz Distributor            ✅        ✅           ❌             ❌
ConvertKit Email              ✅        ✅           ❌             ❌
DataForSEO Keywords           ✅        ✅           ❌             N/A (standalone)
Content Calendar              ✅        ❌           ❌             ❌
Lead Magnet (ROI calc)        ✅        N/A          ❌             N/A (static)
CLI (status)                  ✅        ✅           ✅             N/A
CLI (generate)                ✅        ✅           ✅             N/A
CLI (publish)                 ✅        ❌           ❌             N/A
CLI (autopublish)             ✅        ❌           ❌             N/A
CLI (cron)                    ✅        ❌           ✅             N/A
CLI (keywords)                ✅        ✅           ❌             N/A
GitHub Actions (publish)      ✅        N/A          ❌             N/A
GitHub Actions (deploy)       ✅        N/A          ❌             N/A
GUI / Dashboard               ❌        ❌           ❌             ❌
A/B Testing                   ❌        ❌           ❌             ❌
Content Approval              ❌        ❌           ❌             ❌
Analytics Integration         ❌        ❌           ❌             ❌
```

## Priority Order to Close Gaps

1. **Wire full pipeline** — connect cross-posting + social distribution into publish flow
2. **Test `leadgen publish` live** — verify end-to-end manual publish works
3. **Configure external services** — Postiz, ConvertKit, DataForSEO (needs user)
4. **Add content approval** — draft → review → approve → publish flow
5. **Build minimal GUI** — web dashboard for non-technical users
6. **Add analytics** — Plausible/Umami for traffic + conversion tracking
7. **Add A/B testing** — title variants + UTM tracking
8. **Enable GitHub Pages** — needs user to enable in repo settings

---

## Cost Status

| Service | Planned | Actual | Status |
|---|---|---|---|
| Claude Code CLI | $0 (subscription) | $0 | Using existing subscription |
| GitHub Pages | $0 | $0 | Not yet enabled |
| Vercel (lead magnet) | $0 | $0 | Not yet deployed |
| Postiz | $0 | $0 | Not yet configured |
| ConvertKit | $0 | $0 | Not yet configured |
| DataForSEO | $6/mo | $0 | Not yet configured |
| Domain (optional) | ~$1/mo | $0 | Not purchased |
| **Total** | **~$7/mo** | **$0/mo** | Partially deployed |
