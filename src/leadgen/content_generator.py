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
