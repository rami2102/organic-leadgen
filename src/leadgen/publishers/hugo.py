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
