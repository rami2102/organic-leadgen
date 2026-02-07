"""Content generation using Claude Code CLI in non-interactive mode."""

import asyncio
import json
import subprocess
from pathlib import Path


PROMPTS_DIR = Path(__file__).parent / "prompts"

BLOG_POST_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "slug": {"type": "string"},
        "meta_description": {"type": "string"},
        "body": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["title", "slug", "meta_description", "body", "tags"],
}

SOCIAL_POST_SCHEMA = {
    "type": "object",
    "properties": {
        "linkedin": {"type": "string"},
        "x": {"type": "string"},
        "facebook": {"type": "string"},
        "instagram": {"type": "string"},
        "threads": {"type": "string"},
    },
    "required": ["linkedin", "x", "facebook", "instagram", "threads"],
}


class ContentGenerator:
    """Generate blog and social content via Claude Code CLI."""

    def __init__(self, model: str = "sonnet"):
        self.model = model

    async def _call_claude(self, prompt: str, schema: dict) -> dict:
        cmd = [
            "claude", "--print",
            "--model", self.model,
            "--output-format", "json",
            "--json-schema", json.dumps(schema),
            prompt,
        ]

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: subprocess.run(
                cmd, capture_output=True, text=True, timeout=300
            ),
        )

        if result.returncode != 0:
            raise RuntimeError(f"Claude CLI failed: {result.stderr}")

        response = json.loads(result.stdout)
        return response["structured_output"]

    def _load_prompt(self, name: str, **kwargs: str) -> str:
        template = (PROMPTS_DIR / f"{name}.txt").read_text()
        return template.format(**kwargs)

    async def generate_blog_post(self, niche: str, topic: str) -> dict:
        prompt = self._load_prompt("blog_post", niche=niche, topic=topic)
        return await self._call_claude(prompt, BLOG_POST_SCHEMA)

    async def repurpose_to_social(self, blog_title: str, blog_body: str) -> dict:
        prompt = self._load_prompt(
            "social_post", title=blog_title, body=blog_body[:2000]
        )
        return await self._call_claude(prompt, SOCIAL_POST_SCHEMA)
