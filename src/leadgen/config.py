"""Load configuration from environment variables."""

import os
from dataclasses import dataclass
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
